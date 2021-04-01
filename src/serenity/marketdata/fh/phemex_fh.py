import asyncio
import json
import logging

from typing import List

import fire
from phemex import PublicCredentials
from tau.core import MutableSignal, NetworkScheduler, Event, Signal
from tau.signal import Filter, FlatMap, Map

from serenity.db.api import InstrumentCache
from serenity.exchange.phemex import get_phemex_connection
from serenity.marketdata.fh.feedhandler import FeedHandlerState, WebsocketFeedHandler, ws_fh_main, Feed, \
    OrderBookBuilder
from serenity.marketdata.api import Trade, OrderBookEvent, OrderBookSnapshot, OrderBookUpdate, BookLevel
from serenity.model.exchange import ExchangeInstrument
from serenity.trading.api import Side
from serenity.utils import websocket_subscribe_with_retry


class PhemexFeedHandler(WebsocketFeedHandler):
    """
    Market data feedhandler for the Phemex derivatives exchange. Supports both trade print and top of order book feeds.

    :see: https://github.com/phemex/phemex-api-docs/blob/master/Public-Contract-API-en.md
    """

    logger = logging.getLogger(__name__)

    def __init__(self, scheduler: NetworkScheduler, instrument_cache: InstrumentCache, include_symbol: str = '*',
                 instance_id: str = 'prod'):
        (self.phemex, self.ws_uri) = get_phemex_connection(PublicCredentials(), instance_id)

        # ensure we've initialized PhemexConnection before loading instruments in super()
        super().__init__(scheduler, instrument_cache, instance_id)

        self.instrument_trades = {}
        self.instrument_order_book_events = {}
        self.instrument_order_books = {}

        self.include_symbol = include_symbol

        # timeout in seconds
        self.timeout = 60

    @staticmethod
    def get_uri_scheme() -> str:
        return 'phemex'

    def _load_instruments(self):
        self.logger.info("Downloading supported products")
        products = self.phemex.get_products()
        exchange_code = 'PHEMEX'
        for product in products['data']:
            symbol = product['symbol']
            base_ccy = product['baseCurrency']
            quote_ccy = product['quoteCurrency']
            price_scale = product['priceScale']
            ul_symbol = f'.M{base_ccy}'

            ccy_pair = self.instrument_cache.get_or_create_cryptocurrency_pair(base_ccy, quote_ccy)
            ul_instr = ccy_pair.get_instrument()
            exchange = self.instrument_cache.get_crypto_exchange(exchange_code)
            self.instrument_cache.get_or_create_exchange_instrument(ul_symbol, ul_instr, exchange)
            future = self.instrument_cache.get_or_create_perpetual_future(ul_instr)
            instr = future.get_instrument()
            exch_instrument = self.instrument_cache.get_or_create_exchange_instrument(symbol, instr, exchange)

            self.logger.info(f'\t{symbol} - [ID #{instr.get_instrument_id()}]')
            self.known_instrument_ids[symbol] = exch_instrument
            self.instruments.append(exch_instrument)
            self.price_scaling[symbol] = price_scale

    def _create_feed(self, instrument: ExchangeInstrument):
        symbol = instrument.get_exchange_instrument_code()
        return Feed(instrument, self.instrument_trades[symbol], self.instrument_order_book_events[symbol],
                    self.instrument_order_books[symbol])

    # noinspection DuplicatedCode
    async def _subscribe_trades_and_quotes(self):
        network = self.scheduler.get_network()

        for instrument in self.get_instruments():
            symbol = instrument.get_exchange_instrument_code()
            if symbol == self.include_symbol or self.include_symbol == '*':
                self.instrument_trades[symbol] = MutableSignal()
                self.instrument_order_book_events[symbol] = MutableSignal()
                self.instrument_order_books[symbol] = OrderBookBuilder(network,
                                                                       self.instrument_order_book_events[symbol])

                # magic: inject the bare Signal into the graph so we can
                # fire events on it without any downstream connections
                network.attach(self.instrument_trades[symbol])
                network.attach(self.instrument_order_book_events[symbol])
                network.attach(self.instrument_order_books[symbol])

                trade_subscribe_msg = {
                    'id': 1,
                    'method': 'trade.subscribe',
                    'params': [symbol]
                }

                trade_messages = MutableSignal()
                trade_json_messages = Map(network, trade_messages, lambda x: json.loads(x))
                trade_incr_messages = Filter(network, trade_json_messages,
                                             lambda x: x.get('type', None) == 'incremental')
                trade_lists = Map(network, trade_incr_messages, lambda x: self.__extract_trades(x))
                trades = FlatMap(self.scheduler, trade_lists)

                class TradeScheduler(Event):
                    # noinspection PyShadowingNames
                    def __init__(self, fh: PhemexFeedHandler, trades: Signal):
                        self.fh = fh
                        self.trades = trades

                    def on_activate(self) -> bool:
                        if self.trades.is_valid():
                            trade = self.trades.get_value()
                            trade_symbol = trade.get_instrument().get_exchange_instrument_code()
                            trade_signal = self.fh.instrument_trades[trade_symbol]
                            self.fh.scheduler.schedule_update(trade_signal, trade)
                            return True
                        else:
                            return False

                network.connect(trades, TradeScheduler(self, trades))

                orderbook_subscribe_msg = {
                    'id': 2,
                    'method': 'orderbook.subscribe',
                    'params': [symbol]
                }

                obe_messages = MutableSignal()
                obe_json_messages = Map(network, obe_messages, lambda x: json.loads(x))
                obe_json_messages = Filter(network, obe_json_messages,
                                           lambda x: x.get('type', None) in ['incremental', 'snapshot'])
                order_book_events = Map(network, obe_json_messages, lambda x: self.__extract_order_book_event(x))

                class OrderBookEventScheduler(Event):
                    # noinspection PyShadowingNames
                    def __init__(self, fh: PhemexFeedHandler, order_book_events: Signal):
                        self.fh = fh
                        self.order_book_events = order_book_events

                    def on_activate(self) -> bool:
                        if self.order_book_events.is_valid():
                            obe = self.order_book_events.get_value()
                            obe_symbol = obe.get_instrument().get_exchange_instrument_code()
                            obe_signal = self.fh.instrument_order_book_events[obe_symbol]
                            self.fh.scheduler.schedule_update(obe_signal, obe)
                            return True
                        else:
                            return False

                network.connect(order_book_events, OrderBookEventScheduler(self, order_book_events))

                asyncio.ensure_future(websocket_subscribe_with_retry(self.ws_uri, self.timeout, self.logger,
                                                                     trade_subscribe_msg, self.scheduler,
                                                                     trade_messages, symbol, 'trade'))
                asyncio.ensure_future(websocket_subscribe_with_retry(self.ws_uri, self.timeout, self.logger,
                                                                     orderbook_subscribe_msg, self.scheduler,
                                                                     obe_messages, symbol, 'order book'))

        # we are now live
        self.scheduler.schedule_update(self.state, FeedHandlerState.LIVE)

    def __extract_trades(self, msg) -> List[Trade]:
        trade_list = []
        symbol = msg['symbol']

        instrument = self.known_instrument_ids[symbol]
        price_scale = self.price_scaling[symbol]

        for trade in msg['trades']:
            trade_id = trade[0]
            if trade[1] == 'Buy':
                side = Side.BUY
            else:
                side = Side.SELL
            price = float(trade[2]) / pow(10, price_scale)
            qty = float(trade[3])

            trade_list.append(Trade(instrument, trade_id, trade_id, side, qty, price))

        return trade_list

    def __extract_order_book_event(self, msg) -> OrderBookEvent:
        symbol = msg['symbol']
        seq_num = msg['sequence']
        msg_type = msg['type']

        instrument = self.known_instrument_ids[symbol]
        price_scale = self.price_scaling[symbol]

        def to_book_level_list(px_qty_list):
            book_levels = []
            for px_qty in px_qty_list:
                px = float(px_qty[0]) / pow(10, price_scale)
                qty = float(px_qty[1])
                book_levels.append(BookLevel(px, qty))
            return book_levels

        book = msg['book']
        if msg_type == 'snapshot':
            self.logger.info('received initial L2 order book snapshot')
            bids = to_book_level_list(book['bids'])
            asks = to_book_level_list(book['asks'])
            return OrderBookSnapshot(instrument, bids, asks, seq_num)
        else:
            bids = to_book_level_list(book['bids'])
            asks = to_book_level_list(book['asks'])
            return OrderBookUpdate(instrument, bids, asks, seq_num)


def create_fh(scheduler: NetworkScheduler, instrument_cache: InstrumentCache, include_symbol: str, instance_id: str):
    """
    Helper function that instantiates a Phemex feedhandler; used in the main method
    """
    return PhemexFeedHandler(scheduler, instrument_cache, include_symbol, instance_id)


def main(instance_id: str = 'prod', include_symbol: str = '*', journal_path: str = '/behemoth/journals/'):
    """
    Command-line entry point used by Fire runner for Phemex feedhandler.
    """
    ws_fh_main(create_fh, PhemexFeedHandler.get_uri_scheme(), instance_id, journal_path, 'PHEMEX',
               include_symbol=include_symbol)


if __name__ == '__main__':
    fire.Fire(main)
