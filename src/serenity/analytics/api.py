import logging
import os
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List

import datetime
import pandas as pd
from tau.core import NetworkScheduler

from serenity.model.exchange import ExchangeInstrument
from serenity.trading.api import Order, ExecutionReport, StopOrder, LimitOrder, OrderEvent


class Mode(Enum):
    BACKTEST = auto()
    LIVE = auto()


class SnapshotId:
    def __init__(self, mode: Mode, strategy_id: str, timestamp: datetime.datetime):
        self.mode = mode
        self.strategy_id = strategy_id
        self.timestamp = timestamp

    def get_mode(self) -> Mode:
        return self.mode

    def get_strategy_id(self) -> str:
        return self.strategy_id

    def get_timestamp(self) -> datetime.datetime:
        return self.timestamp

    def __str__(self) -> str:
        ts = self.get_timestamp().strftime('%Y%m%d%H%M%S')
        return f'{self.get_mode().name}/{self.get_strategy_id()}/{ts}'


class Snapshot:
    def __init__(self, snapshot_id: SnapshotId, orders: pd.DataFrame, fills: pd.DataFrame,
                 daily_positions: pd.DataFrame, daily_returns: pd.DataFrame, extra_output: Dict):
        self.snapshot_id = snapshot_id
        self.orders = orders
        self.fills = fills
        self.daily_positions = daily_positions
        self.daily_returns = daily_returns
        self.extra_output = extra_output

    def get_id(self) -> SnapshotId:
        return self.snapshot_id

    def get_orders(self) -> pd.DataFrame:
        return self.orders

    def get_fills(self) -> pd.DataFrame:
        return self.fills

    def get_daily_positions(self) -> pd.DataFrame:
        return self.daily_positions

    def get_daily_returns(self) -> pd.DataFrame:
        return self.daily_returns

    def get_extra_output(self, output_name: str) -> pd.DataFrame:
        return self.extra_output[output_name]


class DataCaptureService(ABC):
    @abstractmethod
    def capture_order(self, order: Order):
        pass

    @abstractmethod
    def capture_fill(self, exec_rpt: ExecutionReport):
        pass

    @abstractmethod
    def capture_daily_position(self, account: str, instrument: ExchangeInstrument, qty: float):
        pass

    @abstractmethod
    def capture_daily_return(self, return_frac: float):
        pass

    @abstractmethod
    def capture(self, channel: str, data: Dict):
        pass

    @abstractmethod
    def create_snapshot(self, strategy_id: str) -> Snapshot:
        pass

    @abstractmethod
    def load_snapshot(self, snapshot_id: SnapshotId) -> Snapshot:
        pass

    @abstractmethod
    def store_snapshot(self, strategy_id: str) -> Snapshot:
        pass


class HDF5DataCaptureService(DataCaptureService):
    logger = logging.getLogger(__name__)

    def __init__(self, mode: Mode, scheduler: NetworkScheduler, extra_outputs: List[str]):
        self.mode = mode
        self.scheduler = scheduler
        self.dataframes = defaultdict(list)
        self.extra_outputs = extra_outputs

    def capture_order(self, order: Order):
        payload = {
            'time': pd.to_datetime(self.scheduler.get_time(), unit='ms'),
            'order_id': order.get_order_id(),
            'cl_ord_id': order.get_cl_ord_id(),
            'account': order.get_account(),
            'side': order.get_side().name,
            'instrument': order.get_instrument().get_exchange_instrument_code(),
            'qty': order.get_qty(),
        }
        if isinstance(order, LimitOrder):
            payload['price'] = order.get_price()
            payload['tif'] = order.get_time_in_force().name
        else:
            payload['price'] = 0
            payload['tif'] = ''

        if isinstance(order, StopOrder):
            payload['stop_px'] = order.get_stop_px()
        else:
            payload['stop_px'] = 0

        self.capture('Orders', payload)

    def capture_fill(self, exec_rpt: OrderEvent):
        if not (isinstance(exec_rpt, ExecutionReport) and exec_rpt.is_fill()):
            return

        payload = {
            'time': pd.to_datetime(self.scheduler.get_time(), unit='ms'),
            'exec_id': exec_rpt.get_exec_id(),
            'order_id': exec_rpt.get_order_id(),
            'cl_ord_id': exec_rpt.get_cl_ord_id(),
            'exec_type': exec_rpt.get_exec_type().name,
            'order_status': exec_rpt.get_order_status().name,
            'cum_qty': exec_rpt.get_cum_qty(),
            'leaves_qty': exec_rpt.get_leaves_qty(),
            'last_qty': exec_rpt.get_last_qty(),
            'last_px': exec_rpt.get_last_px()
        }

        self.capture('Fills', payload)

    def capture_daily_position(self, account: str, instrument: ExchangeInstrument, qty: float):
        self.capture('DailyPositions', {
            'date': pd.to_datetime(self.scheduler.get_time(), unit='ms').date(),
            'account': account,
            'instrument': instrument.get_exchange_instrument_code(),
            'qty': qty
        })

    def capture_daily_return(self, return_frac: float):
        self.capture('DailyReturns', {
            'date': pd.to_datetime(self.scheduler.get_time(), unit='ms').date(),
        })

    def capture(self, output_name: str, data: Dict):
        self.dataframes[output_name].append(data)

    def create_snapshot(self, strategy_id: str) -> Snapshot:
        ts = datetime.datetime.now()
        snapshot_id = SnapshotId(self.mode, strategy_id, ts)

        orders = pd.DataFrame(self.dataframes['Orders'])
        if not orders.empty:
            orders.set_index('time', inplace=True)

        fills = pd.DataFrame(self.dataframes['Fills'])
        if not fills.empty:
            fills.set_index('time', inplace=True)

        daily_positions = pd.DataFrame(self.dataframes['DailyPositions'])
        if not daily_positions.empty:
            daily_positions.set_index('date', inplace=True)

        daily_returns = pd.DataFrame(self.dataframes['DailyReturns'])
        if not daily_returns.empty:
            daily_returns.set_index('date', inplace=True)

        extra_output_dfs = {}
        for extra_output in self.extra_outputs:
            extra_output_df = pd.DataFrame(self.dataframes[extra_output])
            if not extra_output_df.empty:
                extra_output_df.set_index('time', inplace=True)
            extra_output_dfs[extra_output] = extra_output_df

        return Snapshot(snapshot_id, orders, fills, daily_positions, daily_returns, extra_output_dfs)

    def load_snapshot(self, snapshot_id: SnapshotId) -> Snapshot:
        snapshot_path = f'{os.getenv("HOME")}/.serenity/snapshots/{str(snapshot_id)}'

        orders = pd.read_hdf(f'{snapshot_path}/Orders.h5')
        fills = pd.read_hdf(f'{snapshot_path}/Fills.h5')
        daily_positions = pd.read_hdf(f'{snapshot_path}/DailyPositions.h5')
        daily_returns = pd.read_hdf(f'{snapshot_path}/DailyReturns.h5')

        extra_output_dfs = {}
        for extra_output in self.extra_outputs:
            extra_output_dfs[extra_output] = pd.read_hdf(f'{snapshot_path}/{extra_output}.h5')

        # noinspection PyTypeChecker
        return Snapshot(snapshot_id, orders, fills, daily_positions, daily_returns, extra_output_dfs)

    def store_snapshot(self, strategy_id: str) -> Snapshot:
        snapshot = self.create_snapshot(strategy_id)
        snapshot_id = snapshot.get_id()
        snapshot_path = f'{os.getenv("HOME")}/.serenity/snapshots/{snapshot_id}'
        Path(snapshot_path).mkdir(parents=True, exist_ok=True)
        self.logger.info(f'storing snapshots in {snapshot_path}')

        snapshot.get_orders().to_hdf(f'{snapshot_path}/Orders.h5', key='Orders')
        snapshot.get_fills().to_hdf(f'{snapshot_path}/Fills.h5', key='Fills')
        snapshot.get_daily_positions().to_hdf(f'{snapshot_path}/DailyPositions.h5', key='DailyPositions')
        snapshot.get_daily_returns().to_hdf(f'{snapshot_path}/DailyReturns.h5', key='DailyReturns')

        for extra_output in self.extra_outputs:
            extra_output_df = snapshot.get_extra_output(extra_output)
            extra_output_df.to_hdf(f'{snapshot_path}/{extra_output}.h5', key=extra_output)

        return snapshot
