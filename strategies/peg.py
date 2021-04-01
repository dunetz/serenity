import logging
from enum import Enum, auto

from tau.core import Event
from tau.event import Do

from serenity.algo.api import Strategy, StrategyContext
from serenity.trading.api import Side


class PegType(Enum):
    NEAR = auto()
    MID = auto()


class PegTrader(Event):
    def __init__(self, strategy):
        self.strategy = strategy
        self.last_level = None
        self.peg_order = None

    def on_activate(self) -> bool:
        if self.strategy.peg_type == PegType.NEAR:
            if self.strategy.peg_side == Side.BUY:
                book_level = self.strategy.peg_book.get_value().get_best_bid()
                side_name = 'bid'
            else:
                book_level = self.strategy.peg_book.get_value().get_best_ask()
                side_name = 'ask'

            if self.last_level is None or book_level.get_px() != self.last_level.get_px():
                self.last_level = book_level
                self.strategy.logger.info(f'{side_name} price moved to '
                                          f'{self.last_level.get_qty()}@{self.last_level.get_px()}')

                if self.peg_order is not None:
                    self.strategy.logger.info(f'cancelling previous peg order: '
                                              f'clOrdID={self.peg_order.get_cl_ord_id()}')
                    self.strategy.order_placer.cancel(self.peg_order)

                order_factory = self.strategy.order_placer.get_order_factory()
                self.peg_order = order_factory.create_limit_order(self.strategy.peg_side,
                                                                  self.strategy.peg_qty,
                                                                  book_level.get_px(),
                                                                  self.strategy.peg_instrument)
                self.strategy.logger.info(f'submitting new peg order: clOrdID={self.peg_order.get_cl_ord_id()}')
                self.strategy.order_placer.submit(self.peg_order)
        else:
            raise ValueError(f'Unsupported PegType: {self.strategy.peg_type}')
        return False

    def stop(self):
        if self.peg_order is not None:
            self.strategy.order_placer.cancel(self.peg_order)


class Peg(Strategy):
    """
    An example simple strategy that pegs an order so it tracks the near side (best bid or offer).
    """

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.ctx = None
        self.peg_instrument = None
        self.peg_type = None
        self.peg_side = None
        self.peg_qty = None
        self.order_placer = None
        self.peg_book = None
        self.trader = None

    def init(self, ctx: StrategyContext):
        self.ctx = ctx

        account = ctx.getenv('EXCHANGE_ACCOUNT')
        if account is None:
            raise ValueError('Missing EXCHANGE_ACCOUNT')

        exchange_code, peg_symbol = ctx.getenv('PEG_INSTRUMENT').split(':')
        self.peg_instrument = ctx.get_instrument_cache().get_crypto_exchange_instrument(exchange_code, peg_symbol)

        peg_type = ctx.getenv('PEG_TYPE', 'Near')
        if peg_type == 'Near':
            self.peg_type = PegType.NEAR

        peg_side = ctx.getenv('PEG_SIDE')
        if peg_side == 'Buy':
            self.peg_side = Side.BUY
        elif peg_side == 'Sell':
            self.peg_side = Side.SELL
        else:
            raise ValueError(f'Unknown or missing PegSide: {peg_side}')

        self.peg_qty = ctx.getenv('PEG_QTY', 1)

        exchange_id = ctx.getenv('EXCHANGE_ID', 'phemex')
        exchange_instance = ctx.getenv('EXCHANGE_INSTANCE', 'prod')
        op_uri = f'{exchange_id}:{exchange_instance}'
        self.order_placer = ctx.get_order_placer_service().get_order_placer(op_uri)

        self.logger.info(f'Connected to Phemex {exchange_instance} instance')

        # subscribe to top of book
        self.peg_book = self.ctx.get_marketdata_service().get_order_books(self.peg_instrument)

        # subscribe to position updates and exchange position updates
        position = self.ctx.get_position_service().get_position(account, self.peg_instrument)
        Do(ctx.get_scheduler().get_network(), position, lambda: self.logger.info(position.get_value()))

        exch_position = self.ctx.get_exchange_position_service().get_exchange_positions()
        Do(ctx.get_scheduler().get_network(), exch_position, lambda: self.logger.info(exch_position.get_value()))

        # subscribe to order events from the OMS, and log them
        order_events = self.ctx.get_order_placer_service().get_order_manager_service().get_order_events()
        Do(ctx.get_scheduler().get_network(), order_events, lambda: self.logger.info(order_events.get_value()))

    def start(self):
        super().start()

        self.trader = PegTrader(self)
        self.ctx.get_network().connect(self.peg_book, self.trader)

    def stop(self):
        super().stop()

        self.ctx.get_network().disconnect(self.peg_book, self.trader)
        self.trader.stop()

        self.trader = None
