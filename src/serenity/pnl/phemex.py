import asyncio
import json
import logging

from phemex import PublicCredentials
from serenity.db.api import InstrumentCache
from tau.core import Signal, MutableSignal, NetworkScheduler
from tau.signal import Map, Filter, Pipe

from serenity.exchange.phemex import get_phemex_connection
from serenity.model.exchange import ExchangeInstrument
from serenity.model.instrument import FutureContract, CurrencyPair, Instrument
from serenity.pnl.api import MarkService, Mark
from serenity.utils import websocket_subscribe_with_retry


class PhemexMarkService(MarkService):
    logger = logging.getLogger(__name__)

    def __init__(self, scheduler: NetworkScheduler, instrument_cache: InstrumentCache, instance_id: str = 'prod'):
        self.scheduler = scheduler
        self.instrument_cache = instrument_cache
        (self.phemex, self.ws_uri) = get_phemex_connection(PublicCredentials(), instance_id)
        self.instrument_marks = {}

        # timeout in seconds
        self.timeout = 60

    def get_marks(self, instrument: ExchangeInstrument) -> Signal:
        economics = instrument.get_instrument().get_economics()
        if isinstance(economics, FutureContract):
            economics = economics.get_underlier().get_economics()
        if isinstance(economics, CurrencyPair):
            ccy_code = economics.get_base_currency().get_currency_code()
            symbol = f'.M{ccy_code}'
            cash_instrument = self.instrument_cache.get_or_create_cash_instrument(ccy_code)
        else:
            raise ValueError('Unable to get marks: expected CurrencyPair or FutureContract on CurrencyPair')

        network = self.scheduler.get_network()
        marks = self.instrument_marks.get(symbol)
        if marks is None:
            marks = MutableSignal()
            network.attach(marks)
            self.instrument_marks[symbol] = marks

            subscribe_msg = {
                'id': 1,
                'method': 'tick.subscribe',
                'params': [symbol]
            }

            messages = MutableSignal()
            json_messages = Map(network, messages, lambda x: json.loads(x))
            tick_messages = Filter(network, json_messages, lambda x: 'tick' in x)
            ticks = Map(network, tick_messages, lambda x: self.__extract_tick(x, cash_instrument.get_instrument()))
            Pipe(self.scheduler, ticks, marks)

            asyncio.ensure_future(websocket_subscribe_with_retry(self.ws_uri, self.timeout, self.logger,
                                                                 subscribe_msg, self.scheduler, messages,
                                                                 symbol, 'ticks'))
        return marks

    @staticmethod
    def __extract_tick(msg: json, instrument: Instrument):
        px = int(msg['tick']['last']) / pow(10, int(msg['tick']['scale']))
        return Mark(instrument, px)
