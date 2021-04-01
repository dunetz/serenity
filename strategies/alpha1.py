import logging
from datetime import timedelta

from phemex.order import Contract, Side, Trigger, Condition, ConditionalOrder
from tau.core import Event, Network
from tau.event import Do
from tau.math import ExponentialMovingAverage
from tau.signal import Filter, BufferWithTime, Map

from serenity.algo.api import Strategy, StrategyContext
from serenity.signal.marketdata import ComputeOHLC


class Alpha1Trader(Event):
    logger = logging.getLogger(__name__)

    def __init__(self, network: Network, strategy):
        self.network = network
        self.strategy = strategy
        self.order_factory = self.strategy.order_placer.get_order_factory()

        self.open_orders = list()

    def stop(self):
        for order_hnd in self.open_orders:
            order_hnd.cancel()

    # noinspection DuplicatedCode
    def on_activate(self) -> bool:
        if self.network.has_activated(self.strategy.big_prints):
            big_print = self.strategy.big_prints.get_value()
            self.strategy.logger.info(f'Big print in spot market: {big_print}')

            # 5 minute bin volumes dropping below EWMA
            ewma = self.strategy.ewma.get_value()
            volume = self.strategy.volume.get_value()
            if self.strategy.volume.is_valid() and volume < ewma:
                contract = Contract('BTCUSD')
                if big_print.get_side().get_type_code() == 'Buy':
                    # enter short position with a stop-loss and a take-profit at +/- 0.5% last trade px
                    self.logger.info(f'Going short, buy print of {big_print} BTC, EWMA={ewma}, volume={volume}')

                    # create a market order for BTCUSD, "cross" (no leverage), sell / short
                    primary_order = self.order_factory.create_market_order(Side.SELL, self.strategy.trade_qty, contract)

                    last_trade_px = self.strategy.futures_trades.get_value()
                    stop_loss_px = last_trade_px.get_price() * 1.005
                    take_profit_px = last_trade_px.get_price() * 0.995

                    # create stop loss order
                    stop_loss = self.order_factory.create_market_order(Side.BUY, self.strategy.trade_qty, contract)
                    stop_loss_cond = ConditionalOrder(Condition.STOP, Trigger.LAST_PRICE, stop_loss_px, stop_loss)

                    # create take profit order
                    take_profit = self.order_factory.create_market_order(Side.BUY, self.strategy.trade_qty, contract)
                    take_profit_cond = ConditionalOrder(Condition.IF_TOUCHED, Trigger.LAST_PRICE, take_profit_px,
                                                        take_profit)

                    # place the orders
                    self.open_orders.append(self.strategy.order_placer.submit(primary_order))
                    self.open_orders.append(self.strategy.order_placer.submit(stop_loss_cond))
                    self.open_orders.append(self.strategy.order_placer.submit(take_profit_cond))
                else:
                    # enter long position with a stop-loss and a take-profit at +/- 5% last trade px
                    self.logger.info(f'Going long, sell print of {big_print} BTC, EWMA={ewma}, volume={volume}')

                    # create a market order for BTCUSD, "cross" (no leverage), buy / long
                    primary_order = self.order_factory.create_market_order(Side.BUY, self.strategy.trade_qty, contract)

                    last_trade_px = self.strategy.futures_trades.get_value()
                    stop_loss_px = last_trade_px.get_price() * 0.995
                    take_profit_px = last_trade_px.get_price() * 1.005

                    # create stop loss order
                    stop_loss = self.order_factory.create_market_order(Side.SELL, self.strategy.trade_qty, contract)
                    stop_loss_cond = ConditionalOrder(Condition.STOP, Trigger.LAST_PRICE, stop_loss_px, stop_loss)

                    # create take profit order
                    take_profit = self.order_factory.create_market_order(Side.SELL, self.strategy.trade_qty, contract)
                    take_profit_cond = ConditionalOrder(Condition.IF_TOUCHED, Trigger.LAST_PRICE, take_profit_px,
                                                        take_profit)

                    # place the orders
                    self.open_orders.append(self.strategy.order_placer.submit(primary_order))
                    self.open_orders.append(self.strategy.order_placer.submit(stop_loss_cond))
                    self.open_orders.append(self.strategy.order_placer.submit(take_profit_cond))

            return True
        else:
            return False


class Alpha1(Strategy):
    """
    An example investment strategy. This signal has not been backtested & calibrated and you should not
    trade it; this is for example purposes only. Likely this is TOTAL NONSENSE. Furthermore, the fast
    position keeper has not yet been implemented, so it's relying on stop-loss / take-profit to clean
    up positions. There are no limits either, so likely this is also DANGEROUS NONSENSE.
    """

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.ctx = None
        self.trade_qty = None
        self.order_placer = None
        self.spot_feed = None
        self.futures_feed = None
        self.big_prints = None
        self.futures_trades = None
        self.futures_book = None
        self.ohlc_5min = None
        self.volume = None
        self.ewma = None
        self.trader = None

    def init(self, ctx: StrategyContext):
        self.ctx = ctx

        big_print_qty = float(ctx.getenv('BIG_PRINT_QTY'))
        self.trade_qty = float(ctx.getenv('CONTRACT_TRADE_QTY'))

        exchange_instance = ctx.getenv('EXCHANGE_INSTANCE', 'prod')
        op_uri = f'phemex:{exchange_instance}'
        self.order_placer = ctx.get_order_placer_service().get_order_placer(op_uri)

        self.logger.info(f'Connected to Phemex {exchange_instance} instance')

        network = self.ctx.get_network()

        # scan the spot market for large trades
        btc_usd_spot = self.ctx.get_instrument_cache().get_crypto_exchange_instrument('CoinbasePro', 'BTC-USD')
        spot_trades = self.ctx.get_marketdata_service().get_trades(btc_usd_spot)
        Do(network, spot_trades, lambda: self.logger.info(f'Spot market trade: {spot_trades.get_value()}'))
        self.big_prints = Filter(network, spot_trades, lambda x: x.get_qty() >= big_print_qty)

        # compute 5 minute bins for the futures market and extract the volume field
        btc_usd_future = self.ctx.get_instrument_cache().get_crypto_exchange_instrument('Phemex', 'BTCUSD')
        self.futures_trades = self.ctx.get_marketdata_service().get_trades(btc_usd_future)
        buffer_5min = BufferWithTime(self.ctx.get_scheduler(), self.futures_trades, timedelta(minutes=5))
        self.ohlc_5min = ComputeOHLC(network, buffer_5min)
        Do(network, self.ohlc_5min, lambda: self.logger.info(f'OHLC[5min]: {self.ohlc_5min.get_value()}'))
        self.volume = Map(network, self.ohlc_5min, lambda x: x.volume)

        # subscribe to top of book
        self.futures_book = self.ctx.get_marketdata_service().get_order_books(btc_usd_future)
        Do(network, self.futures_book, lambda: self.logger.info(f'Futures bid/ask: '
                                                                f'{self.futures_book.get_value().get_best_bid()} / '
                                                                f'{self.futures_book.get_value().get_best_ask()}'))

        # track the exponentially weighted moving average of the futures volume
        self.ewma = ExponentialMovingAverage(network, self.volume)

    def start(self):
        super().start()

        self.trader = Alpha1Trader(self.ctx.get_network(), self)
        self.ctx.get_network().connect(self.big_prints, self.trader)
        self.ctx.get_network().connect(self.ewma, self.trader)

    def stop(self):
        super().stop()

        self.trader.stop()
        self.ctx.get_network().disconnect(self.big_prints, self.trader)
        self.ctx.get_network().disconnect(self.ewma, self.trader)
        self.trader = None
