from azure.identity import DeviceCodeCredential
from tau.core import Signal, HistoricNetworkScheduler, MutableSignal, NetworkScheduler, SignalGenerator

from serenity.marketdata.api import MarketdataService, Trade, OrderBook, BookLevel
from serenity.model.exchange import ExchangeInstrument
from serenity.marketdata.tickstore.api import AzureBlobTickstore
from serenity.trading.api import Side
from serenity.utils import get_global_defaults


class AzureHistoricMarketdataService(MarketdataService):
    """
    A historical replay service based off of Serenity's native AzureBlobTickstore.
    """

    def __init__(self, scheduler: HistoricNetworkScheduler):
        self.scheduler = scheduler
        self.subscribed_instruments = MutableSignal()
        self.scheduler.get_network().attach(self.subscribed_instruments)

        self.start_time = scheduler.get_clock().get_start_time()
        self.end_time = scheduler.get_clock().get_end_time()

        self.all_subscribed = set()
        self.book_signal_by_symbol = {}
        self.trade_signal_by_symbol = {}

        self.credential = DeviceCodeCredential(client_id=get_global_defaults()['azure']['client_id'],
                                               tenant_id=get_global_defaults()['azure']['tenant_id'])

    def get_subscribed_instruments(self) -> Signal:
        return self.subscribed_instruments

    def get_order_book_events(self, instrument: ExchangeInstrument) -> Signal:
        raise NotImplementedError()

    def get_order_books(self, instrument: ExchangeInstrument) -> Signal:
        symbol = instrument.get_exchange_instrument_code()
        exchange_code_upper = instrument.get_exchange().get_exchange_code().upper()

        order_books = self.book_signal_by_symbol.get(symbol, None)
        if order_books is None:
            self._maybe_notify_subscription(instrument)

            order_books = MutableSignal()
            self.scheduler.network.attach(order_books)
            self.book_signal_by_symbol[symbol] = order_books

            class OrderBookGenerator(SignalGenerator):
                def __init__(self, mds):
                    self.mds = mds

                def generate(self, scheduler: NetworkScheduler):
                    tickstore = AzureBlobTickstore(self.mds.credential, f'{exchange_code_upper}_BOOKS',
                                                   timestamp_column='time')
                    books_df = tickstore.select(symbol, self.mds.start_time, self.mds.end_time)
                    for row in books_df.itertuples():
                        at_time = row[0].asm8.astype('int64') / 10**6
                        best_bid = BookLevel(row[2], row[1])
                        best_ask = BookLevel(row[4], row[3])
                        book = OrderBook(bids=[best_bid], asks=[best_ask])
                        scheduler.schedule_update_at(order_books, book, at_time)
                    tickstore.close()

            self.scheduler.add_generator(OrderBookGenerator(self))

            # workaround: force scheduling of all historic trade events
            self.get_trades(instrument)

        return order_books

    def get_trades(self, instrument: ExchangeInstrument) -> Signal:
        trade_symbol = instrument.get_exchange_instrument_code()
        exchange_code_upper = instrument.get_exchange().get_exchange_code().upper()

        self._maybe_notify_subscription(instrument)

        trades = self.trade_signal_by_symbol.get(trade_symbol, None)
        if trades is None:
            trades = MutableSignal()
            self.scheduler.network.attach(trades)
            self.trade_signal_by_symbol[trade_symbol] = trades

            class TradeGenerator(SignalGenerator):
                def __init__(self, mds):
                    self.mds = mds

                def generate(self, scheduler: NetworkScheduler):
                    tickstore = AzureBlobTickstore(self.mds.credential, f'{exchange_code_upper}_TRADES',
                                                   timestamp_column='time')
                    trades_df = tickstore.select(trade_symbol, self.mds.start_time, self.mds.end_time)
                    for row in trades_df.itertuples():
                        at_time = row[0].asm8.astype('int64') / 10 ** 6
                        sequence = row[1]
                        trade_id = row[2]
                        side = Side.SELL if row[4] == 'sell' else Side.BUY
                        qty = row[5]
                        price = row[6]
                        trade = Trade(instrument, sequence, trade_id, side, qty, price)
                        scheduler.schedule_update_at(trades, trade, at_time)

                    tickstore.close()

            self.scheduler.add_generator(TradeGenerator(self))

            # workaround: force scheduling of all historic order book events
            self.get_order_books(instrument)

        return trades

    def _maybe_notify_subscription(self, instrument: ExchangeInstrument):
        if instrument not in self.all_subscribed:
            self.scheduler.schedule_update(self.subscribed_instruments, instrument)
            self.all_subscribed.add(instrument)
