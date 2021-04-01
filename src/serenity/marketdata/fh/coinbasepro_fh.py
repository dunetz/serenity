import json
import logging

import coinbasepro
import fire
import websockets
from tau.core import MutableSignal, NetworkScheduler, Event
from tau.signal import Map, Filter

from serenity.db.api import InstrumentCache
from serenity.marketdata.fh.feedhandler import FeedHandlerState, WebsocketFeedHandler, ws_fh_main, Feed, \
    OrderBookBuilder
from serenity.marketdata.api import Trade, OrderBookEvent, BookLevel, OrderBookSnapshot, OrderBookUpdate
from serenity.model.exchange import ExchangeInstrument
from serenity.trading.api import Side


class CoinbaseProFeedHandler(WebsocketFeedHandler):
    """
    Market data feedhandler for the Coinbase Pro exchange. Supports both trade print and top of order book feeds.

    :see: https://docs.pro.coinbase.com/
    """

    logger = logging.getLogger(__name__)

    def __init__(self, scheduler: NetworkScheduler, instrument_cache: InstrumentCache, include_symbol: str = '*',
                 instance_id: str = 'prod'):
        if instance_id == 'prod':
            self.ws_uri = 'wss://ws-feed.pro.coinbase.com'
            self.cbp_client = coinbasepro.PublicClient()
        elif instance_id == 'test':
            self.ws_uri = 'wss://ws-feed-public.sandbox.pro.coinbase.com'
            self.cbp_client = coinbasepro.PublicClient(api_url='https://api-public.sandbox.pro.coinbase.com')
        else:
            raise ValueError(f'Unknown instance_id: {instance_id}')

        # ensure we've initialized client before loading instruments in super()
        super().__init__(scheduler, instrument_cache, instance_id)

        self.include_symbol = include_symbol

        self.instrument_trades = {}
        self.instrument_order_book_events = {}
        self.instrument_order_books = {}

    @staticmethod
    def get_uri_scheme() -> str:
        return 'coinbasepro'

    def _load_instruments(self):
        self.logger.info("Downloading supported products")

        for product in self.cbp_client.get_products():
            symbol = product['id']
            base_ccy = product['base_currency']
            quote_ccy = product['quote_currency']
            currency_pair = self.instrument_cache.get_or_create_cryptocurrency_pair(base_ccy, quote_ccy)
            instrument = currency_pair.get_instrument()
            exchange = self.instrument_cache.get_crypto_exchange('COINBASEPRO')
            exch_instr = self.instrument_cache.get_or_create_exchange_instrument(symbol, instrument, exchange)

            self.logger.info(f'\t{symbol} - {base_ccy}/{quote_ccy} [ID #{instrument.get_instrument_id()}]')
            self.known_instrument_ids[symbol] = exch_instr
            self.instruments.append(exch_instr)

    def _create_feed(self, instrument: ExchangeInstrument):
        symbol = instrument.get_exchange_instrument_code()
        return Feed(instrument, self.instrument_trades[symbol], self.instrument_order_book_events[symbol],
                    self.instrument_order_books[symbol])

    # noinspection DuplicatedCode
    async def _subscribe_trades_and_quotes(self):
        network = self.scheduler.get_network()

        symbols = []
        for instrument in self.get_instruments():
            symbol = instrument.get_exchange_instrument_code()
            if symbol == self.include_symbol or self.include_symbol == '*':
                symbols.append(f'{symbol}')

                self.instrument_trades[symbol] = MutableSignal()
                self.instrument_order_book_events[symbol] = MutableSignal()
                self.instrument_order_books[symbol] = OrderBookBuilder(network,
                                                                       self.instrument_order_book_events[symbol])

                # magic: inject the bare Signal into the graph so we can
                # fire events on it without any downstream connections
                # yet made
                network.attach(self.instrument_trades[symbol])
                network.attach(self.instrument_order_book_events[symbol])
                network.attach(self.instrument_order_books[symbol])

        subscribe_msg = {
            'type': 'subscribe',
            'product_ids': symbols,
            'channels': ['matches', 'level2', 'heartbeat']
        }

        messages = MutableSignal()
        json_messages = Map(network, messages, lambda x: json.loads(x))
        match_messages = Filter(network, json_messages, lambda x: x.get('type', None) == 'match')
        book_messages = Filter(network, json_messages, lambda x: x.get('type', None) in {'snapshot', 'l2update'})
        trades = Map(network, match_messages, lambda x: self.__extract_trade(x))
        books = Map(network, book_messages, lambda x: self.__extract_order_book_event(x))

        class TradeScheduler(Event):
            def __init__(self, fh: CoinbaseProFeedHandler):
                self.fh = fh

            def on_activate(self) -> bool:
                if trades.is_valid():
                    trade = trades.get_value()
                    trade_symbol = trade.get_instrument().get_exchange_instrument_code()
                    trade_signal = self.fh.instrument_trades[trade_symbol]
                    self.fh.scheduler.schedule_update(trade_signal, trade)
                    return True
                else:
                    return False

        network.connect(trades, TradeScheduler(self))

        class OrderBookScheduler(Event):
            def __init__(self, fh: CoinbaseProFeedHandler):
                self.fh = fh

            def on_activate(self) -> bool:
                if books.is_valid():
                    obe = books.get_value()
                    obe_symbol = obe.get_instrument().get_exchange_instrument_code()
                    obe_signal = self.fh.instrument_order_book_events[obe_symbol]
                    self.fh.scheduler.schedule_update(obe_signal, obe)
                    return True
                else:
                    return False

        network.connect(books, OrderBookScheduler(self))

        async with websockets.connect(self.ws_uri) as sock:
            self.logger.info('Sending subscription request for all products')
            await sock.send(json.dumps(subscribe_msg))
            self.scheduler.schedule_update(self.state, FeedHandlerState.LIVE)
            while True:
                self.scheduler.schedule_update(messages, await sock.recv())

    def __extract_trade(self, msg) -> Trade:
        sequence = msg['sequence']
        trade_id = msg['trade_id']
        side = Side.BUY if msg['side'] == 'buy' else Side.SELL
        qty = float(msg['size'])
        price = float(msg['price'])

        symbol = msg['product_id']
        instrument = self.known_instrument_ids[symbol]
        return Trade(instrument, sequence, trade_id, side, qty, price)

    def __extract_order_book_event(self, msg) -> OrderBookEvent:
        symbol = msg['product_id']
        msg_type = msg['type']

        instrument = self.known_instrument_ids[symbol]

        def to_book_level_list(px_qty_list):
            book_levels = []
            for px_qty in px_qty_list:
                px = float(px_qty[0])
                qty = float(px_qty[1])
                book_levels.append(BookLevel(px, qty))
            return book_levels

        if msg_type == 'snapshot':
            self.logger.info('received initial L2 order book snapshot')
            bids = to_book_level_list(msg['bids'])
            asks = to_book_level_list(msg['asks'])
            return OrderBookSnapshot(instrument, bids, asks, 0)
        else:
            changes = msg['changes']
            bids = []
            asks = []
            for side_px_qty in changes:
                side = side_px_qty[0]
                px = float(side_px_qty[1])
                qty = float(side_px_qty[2])
                if side == 'buy':
                    bids.append(BookLevel(px, qty))
                else:
                    asks.append(BookLevel(px, qty))
            return OrderBookUpdate(instrument, bids, asks, 0)


def create_fh(scheduler: NetworkScheduler, instrument_cache: InstrumentCache, include_symbol: str, instance_id: str):
    """
    Helper function that instantiates a CBP feedhandler; used in the main method
    """
    return CoinbaseProFeedHandler(scheduler, instrument_cache, include_symbol, instance_id)


def main(instance_id: str = 'prod', journal_path: str = '/behemoth/journals/', include_symbol: str = '*'):
    """
    Command-line entry point used by Fire runner for CBP feedhandler.
    """
    ws_fh_main(create_fh, CoinbaseProFeedHandler.get_uri_scheme(), instance_id, journal_path, 'COINBASE_PRO',
               include_symbol=include_symbol)


if __name__ == '__main__':
    fire.Fire(main)
