from abc import ABC
from enum import Enum, auto

from tau.core import Signal, Network
from tau.signal import Map

from serenity.marketdata.api import MarketdataService
from serenity.model.exchange import ExchangeInstrument
from serenity.model.instrument import Instrument


class Mark:
    def __init__(self, instrument: Instrument, px: float):
        self.instrument = instrument
        self.px = px

    def get_instrument(self) -> Instrument:
        return self.instrument

    def get_px(self) -> float:
        return self.px

    def __repr__(self) -> str:
        return f'Mark[instrument={self.instrument.get_instrument_code()}, px={self.px}]'


class MarkService(ABC):
    """
    Service providing a "fair" mark price for P&L calculation purposes.
    """
    def get_marks(self, instrument: ExchangeInstrument) -> Signal:
        """
        :return: a signal with Mark values
        """
        pass


class MarkType(Enum):
    LAST = auto()
    MID = auto()


class MarketdataMarkService(MarkService):
    """
    Utility implementation of the MarkService which uses different marketdata fields as "fair" price.
    """
    def __init__(self, network: Network, mds: MarketdataService, mark_type: MarkType = MarkType.MID):
        self.network = network
        self.mds = mds
        self.mark_type = mark_type

    def get_marks(self, instrument: ExchangeInstrument) -> Signal:
        if self.mark_type == MarkType.LAST:
            trades = self.mds.get_trades(instrument)
            return Map(self.network, trades, lambda x: Mark(instrument.get_instrument(), x.get_price()))
        else:
            books = self.mds.get_order_books(instrument)
            return Map(self.network, books, lambda x: Mark(instrument.get_instrument(), x.get_mid()))
