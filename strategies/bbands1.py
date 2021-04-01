import logging
from enum import Enum, auto

import pandas as pd

from datetime import timedelta

from tau.core import Event, NetworkScheduler
from tau.event import Do
from tau.signal import Map, BufferWithTime

from serenity.algo.api import Strategy, StrategyContext
from serenity.signal.indicators import ComputeBollingerBands
from serenity.signal.marketdata import ComputeOHLC
from serenity.trading.api import Side, OrderStatus, ExecutionReport, Reject
from serenity.trading.oms import OrderPlacerService


class BollingerBandsStrategy1(Strategy):
    """
    An example strategy that uses Bollinger Band crossing as a signal to buy or sell.
    """

    logger = logging.getLogger(__name__)

    def init(self, ctx: StrategyContext):
        scheduler = ctx.get_scheduler()
        network = scheduler.get_network()

        contract_qty = int(ctx.getenv('BBANDS_QTY', 1))
        window = int(ctx.getenv('BBANDS_WINDOW'))
        num_std = int(ctx.getenv('BBANDS_NUM_STD'))
        stop_std = int(ctx.getenv('BBANDS_STOP_STD'))
        bin_minutes = int(ctx.getenv('BBANDS_BIN_MINUTES', 5))
        cooling_period_seconds = int(ctx.getenv('BBANDS_COOL_SECONDS', 15))
        exchange_code, instrument_code = ctx.getenv('TRADING_INSTRUMENT').split(':')
        instrument = ctx.get_instrument_cache().get_crypto_exchange_instrument(exchange_code, instrument_code)
        trades = ctx.get_marketdata_service().get_trades(instrument)
        trades_5m = BufferWithTime(scheduler, trades, timedelta(minutes=bin_minutes))
        prices = ComputeOHLC(network, trades_5m)
        close_prices = Map(network, prices, lambda x: x.close_px)
        bbands = ComputeBollingerBands(network, close_prices, window, num_std)

        op_service = ctx.get_order_placer_service()
        oms = op_service.get_order_manager_service()
        dcs = ctx.get_data_capture_service()

        exchange_id = ctx.getenv('EXCHANGE_ID', 'phemex')
        exchange_instance = ctx.getenv('EXCHANGE_INSTANCE', 'prod')
        account = ctx.getenv('EXCHANGE_ACCOUNT')
        op_uri = f'{exchange_id}:{exchange_instance}'

        # subscribe to marks, position updates and exchange position updates
        marks = ctx.get_mark_service().get_marks(instrument)
        Do(scheduler.get_network(), marks, lambda: self.logger.debug(marks.get_value()))

        position = ctx.get_position_service().get_position(account, instrument)
        Do(scheduler.get_network(), position, lambda: self.logger.info(position.get_value()))

        exch_position = ctx.get_exchange_position_service().get_exchange_positions()
        Do(scheduler.get_network(), exch_position, lambda: self.logger.info(exch_position.get_value()))

        # capture position and Bollinger Band data
        Do(scheduler.get_network(), position, lambda: dcs.capture('Position', {
            'time': pd.to_datetime(scheduler.get_time(), unit='ms'),
            'position': position.get_value().get_qty()
        }))
        Do(scheduler.get_network(), bbands, lambda: dcs.capture('BollingerBands', {
            'time': pd.to_datetime(scheduler.get_time(), unit='ms'),
            'sma': bbands.get_value().sma,
            'upper': bbands.get_value().upper,
            'lower': bbands.get_value().lower
        }))

        # debug log basic marketdata
        Do(scheduler.get_network(), prices, lambda: self.logger.debug(prices.get_value()))

        class TraderState(Enum):
            GOING_LONG = auto()
            LONG = auto()
            FLATTENING = auto()
            FLAT = auto()

        # order placement logic
        class BollingerTrader(Event):
            # noinspection PyShadowingNames
            def __init__(self, scheduler: NetworkScheduler, op_service: OrderPlacerService,
                         strategy: BollingerBandsStrategy1):
                self.scheduler = scheduler
                self.op = op_service.get_order_placer(f'{op_uri}')
                self.strategy = strategy
                self.last_entry = 0
                self.last_exit = 0
                self.cum_pnl = 0
                self.stop = None
                self.trader_state = TraderState.FLAT
                self.last_trade_time = 0

                self.scheduler.get_network().connect(oms.get_order_events(), self)
                self.scheduler.get_network().connect(position, self)

            def on_activate(self) -> bool:
                if self.scheduler.get_network().has_activated(oms.get_order_events()):
                    order_event = oms.get_order_events().get_value()
                    if isinstance(order_event, ExecutionReport) and order_event.is_fill():
                        order_type = 'stop order' if self.stop is not None and order_event.get_order_id() == \
                                                     self.stop.order_id else 'market order'
                        self.strategy.logger.info(f'Received fill event for {order_type}: {order_event}')
                        if self.trader_state == TraderState.GOING_LONG:
                            self.last_entry = order_event.get_last_px()
                            if order_event.get_order_status() == OrderStatus.FILLED:
                                self.strategy.logger.info(f'Entered long position: entry price={self.last_entry}')
                                self.trader_state = TraderState.LONG
                        elif self.trader_state in (TraderState.FLATTENING, TraderState.LONG) and \
                                order_event.get_order_status() == OrderStatus.FILLED:
                            if order_type == 'stop order':
                                self.strategy.logger.info(f'stop loss filled at {order_event.get_last_px()}')
                                self.stop = None

                            trade_pnl = (order_event.get_last_px() - self.last_entry) * \
                                        (contract_qty / self.last_entry)
                            self.cum_pnl += trade_pnl
                            self.strategy.logger.info(f'Trade P&L={trade_pnl}; cumulative P&L={self.cum_pnl}')

                            dcs.capture('PnL', {
                                'time': pd.to_datetime(scheduler.get_time(), unit='ms'),
                                'trade_pnl': trade_pnl,
                                'cum_pnl': self.cum_pnl
                            })
                            self.trader_state = TraderState.FLAT
                    elif isinstance(order_event, Reject):
                        self.strategy.logger.error(f'Order rejected: {order_event.get_message()}')
                        self.trader_state = TraderState.FLAT
                elif self.trader_state == TraderState.FLAT and close_prices.get_value() < bbands.get_value().lower:
                    if self.last_trade_time != 0 and (scheduler.get_time() - self.last_trade_time) < \
                            cooling_period_seconds * 1000:
                        self.strategy.logger.info('Cooling off -- not trading again on rapidly repeated signal')
                        return False

                    self.strategy.logger.info(f'Close below lower Bollinger band, enter long position '
                                              f'at {scheduler.get_clock().get_time()}')

                    stop_px = close_prices.get_value() - ((bbands.get_value().sma - bbands.get_value().lower) *
                                                          (stop_std / num_std))

                    self.strategy.logger.info(f'Submitting orders: last_px = {close_prices.get_value()}, '
                                              f'stop_px = {stop_px}')

                    order = self.op.get_order_factory().create_market_order(Side.BUY, contract_qty, instrument)
                    self.stop = self.op.get_order_factory().create_stop_order(Side.SELL, contract_qty, stop_px,
                                                                              instrument)

                    self.op.submit(order)
                    self.op.submit(self.stop)

                    self.last_trade_time = scheduler.get_time()
                    self.trader_state = TraderState.GOING_LONG
                elif self.trader_state == TraderState.LONG and close_prices.get_value() > bbands.get_value().upper:
                    self.strategy.logger.info(f'Close above upper Bollinger band, exiting long position at '
                                              f'{scheduler.get_clock().get_time()}')

                    order = self.op.get_order_factory().create_market_order(Side.SELL, contract_qty, instrument)
                    self.op.submit(order)
                    if self.stop is not None:
                        self.op.cancel(self.stop)
                        self.stop = None

                    self.trader_state = TraderState.FLATTENING
                return False

        network.connect(bbands, BollingerTrader(scheduler, op_service, self))
