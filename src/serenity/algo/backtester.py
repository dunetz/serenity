import importlib
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import fire
import yaml
from tau.core import HistoricNetworkScheduler
from tau.event import Do

from serenity.algo.api import StrategyContext
from serenity.analytics.api import HDF5DataCaptureService, Mode, Snapshot
from serenity.db.api import connect_serenity_db, InstrumentCache, TypeCodeCache
from serenity.marketdata.azure import AzureHistoricMarketdataService
from serenity.pnl.api import MarketdataMarkService
from serenity.position.api import PositionService, NullExchangePositionService
from serenity.trading.oms import OrderManagerService, OrderPlacerService
from serenity.trading.connector.simulator import AutoFillOrderPlacer
from serenity.utils import init_logging, Environment


class BacktestConfig:
    @staticmethod
    def load(config_path: Path, strategy_basedir: Path, start_time_txt: str, end_time_txt):
        timestamp_fmt = '%Y-%m-%dT%H:%M:%S'
        start_time_millis = int(time.mktime(datetime.strptime(start_time_txt, timestamp_fmt).timetuple()) * 1000)
        end_time_millis = int(time.mktime(datetime.strptime(end_time_txt, timestamp_fmt).timetuple()) * 1000)

        with open(config_path, 'r') as config_yaml:
            config = yaml.safe_load(config_yaml)
            api_version = config['api-version']
            if api_version != 'v1Beta':
                raise ValueError(f'Unsupported API version: {api_version}')

            env = Environment(config['environment'])
            strategy_name = config['strategy']['name']
            strategy_class = config['strategy']['strategy-class']
            strategy_module = config['strategy']['module']
            strategy_env = Environment(config['strategy']['environment'], parent=env)
            return BacktestConfig(env, strategy_name, strategy_class, strategy_module, strategy_basedir, strategy_env,
                                  start_time_millis, end_time_millis)

    def __init__(self, env: Environment, strategy_name: str, strategy_class: str, strategy_module: str,
                 strategy_basedir: Path, strategy_env: Environment, start_time_millis: int, end_time_millis: int):
        self.env = env
        self.strategy_name = strategy_name
        self.strategy_class = strategy_class
        self.strategy_module = strategy_module
        self.strategy_basedir = strategy_basedir
        self.strategy_env = strategy_env
        self.start_time_millis = start_time_millis
        self.end_time_millis = end_time_millis

    def get_env(self) -> Environment:
        return self.env

    def get_strategy_name(self) -> str:
        return self.strategy_name

    def get_strategy_instance(self) -> Any:
        module = importlib.import_module(self.strategy_module)
        klass = getattr(module, self.strategy_class)
        strategy_instance = klass()
        return strategy_instance

    def get_strategy_basedir(self) -> Path:
        return self.strategy_basedir

    def get_strategy_env(self) -> Environment:
        return self.strategy_env

    def get_start_time_millis(self) -> int:
        return self.start_time_millis

    def get_end_time_millis(self) -> int:
        return self.end_time_millis


class BacktestResult:
    def __init__(self, strategy_id: str, snapshot: Snapshot):
        self.strategy_id = strategy_id
        self.snapshot = snapshot

    def get_strategy_id(self) -> str:
        return self.strategy_id

    def get_snapshot(self) -> Snapshot:
        return self.snapshot


class AlgoBacktester:
    """"
    Algorithmic trading strategy backtester.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, config: BacktestConfig):
        logger = logging.getLogger(__name__)
        logger.info('Serenity backtester starting up')

        sys.path.append(str(config.get_strategy_basedir()))

        bt_env = config.get_env()

        exchange_id = bt_env.getenv('EXCHANGE_ID', 'autofill')
        instance_id = bt_env.getenv('EXCHANGE_INSTANCE', 'prod')
        account = bt_env.getenv('EXCHANGE_ACCOUNT', 'Main')

        self.logger.info('Connecting to Serenity database')
        conn = connect_serenity_db()
        conn.autocommit = True
        cur = conn.cursor()

        self.scheduler = HistoricNetworkScheduler(config.get_start_time_millis(), config.get_end_time_millis())
        instrument_cache = InstrumentCache(cur, TypeCodeCache(cur))

        oms = OrderManagerService(self.scheduler)

        md_service = AzureHistoricMarketdataService(self.scheduler)
        mark_service = MarketdataMarkService(self.scheduler.get_network(), md_service)
        op_service = OrderPlacerService(self.scheduler, oms)
        op_service.register_order_placer(f'{exchange_id}:{instance_id}',
                                         AutoFillOrderPlacer(self.scheduler, oms, md_service, account))

        xps = NullExchangePositionService(self.scheduler)

        extra_outputs_txt = bt_env.getenv('EXTRA_OUTPUTS')
        if extra_outputs_txt is None:
            extra_outputs = []
        else:
            extra_outputs = extra_outputs_txt.split(',')
        self.dcs = HDF5DataCaptureService(Mode.BACKTEST, self.scheduler, extra_outputs)

        # wire up orders and fills from OMS
        Do(self.scheduler.get_network(), oms.get_orders(),
           lambda: self.dcs.capture_order(oms.get_orders().get_value()))
        Do(self.scheduler.get_network(), oms.get_order_events(),
           lambda: self.dcs.capture_fill(oms.get_order_events().get_value()))

        self.strategy_name = config.get_strategy_name()
        strategy_env = config.get_strategy_env()
        ctx = StrategyContext(self.scheduler, instrument_cache, md_service, mark_service, op_service,
                              PositionService(self.scheduler, oms), xps, self.dcs, strategy_env.values)
        strategy_instance = config.get_strategy_instance()
        strategy_instance.init(ctx)
        strategy_instance.start()

    def run(self) -> BacktestResult:
        self.scheduler.run()

        # store output after historic run completes
        snapshot = self.dcs.store_snapshot(self.strategy_name)
        self.logger.info(f'stored snapshot: {snapshot.get_id()}')

        return BacktestResult(self.strategy_name, snapshot)


def main(config_path: str, start_time: str = None, end_time: str = None, strategy_dir: str = '.'):
    init_logging()
    config = BacktestConfig.load(Path(config_path), Path(strategy_dir), start_time, end_time)
    engine = AlgoBacktester(config)
    engine.run()


if __name__ == '__main__':
    fire.Fire(main)
