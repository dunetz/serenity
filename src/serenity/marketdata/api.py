from abc import ABC, abstractmethod
from typing import List, Optional

from tau.core import Signal, Network
from tau.signal import Function

from serenity.model.exchange import ExchangeInstrument
from serenity.trading.api import Side


class Trade:
    def __init__(self, instrument: ExchangeInstrument, sequence_id: int, trade_id: int, side: Side,
                 qty: float, price: float):
        self.instrument = instrument
        self.sequence_id = sequence_id
        self.trade_id = trade_id
        self.side = side
        self.qty = qty
        self.price = price

    def get_instrument(self) -> ExchangeInstrument:
        return self.instrument

    def get_sequence_id(self) -> int:
        return self.sequence_id

    def get_trade_id(self) -> int:
        return self.trade_id

    def get_side(self) -> Side:
        return self.side

    def get_qty(self) -> float:
        return self.qty

    def get_price(self) -> float:
        return self.price

    def __str__(self):
        return f'{self.instrument} - {self.side} {self.qty}@{self.price} (ID: {self.trade_id})'


class BookLevel:
    __slots__ = ['px', 'qty']

    def __init__(self, px: float, qty: float):
        self.px = px
        self.qty = qty

    def get_px(self) -> float:
        return self.px

    def get_qty(self) -> float:
        return self.qty

    def __str__(self):
        return f'{self.qty}@{self.px}'


class OrderBookEvent(ABC):
    __slots__ = ['instrument', 'seq_num']

    def __init__(self, instrument: ExchangeInstrument, seq_num: int):
        self.instrument = instrument
        self.seq_num = seq_num

    def get_instrument(self) -> ExchangeInstrument:
        return self.instrument

    def get_sequence_num(self) -> int:
        return self.seq_num


class OrderBookSnapshot(OrderBookEvent):
    def __init__(self, instrument: ExchangeInstrument, bids: List[BookLevel], asks: List[BookLevel], seq_num: int):
        super().__init__(instrument, seq_num)
        self.bids = bids
        self.asks = asks

    def get_bids(self) -> List[BookLevel]:
        return self.bids

    def get_asks(self) -> List[BookLevel]:
        return self.asks


class OrderBookUpdate(OrderBookEvent):
    __slots__ = ['bids', 'asks']

    def __init__(self, instrument: ExchangeInstrument, bids: List[BookLevel], asks: List[BookLevel], seq_num: int):
        super().__init__(instrument, seq_num)
        self.bids = bids
        self.asks = asks

    def get_updated_bids(self) -> List[BookLevel]:
        return self.bids

    def get_updated_asks(self) -> List[BookLevel]:
        return self.asks


class OrderBook:
    __slots__ = ['bids', 'asks', 'bid_px_map', 'ask_px_map']

    def __init__(self, bids: List[BookLevel], asks: List[BookLevel]):
        self.bids = sorted(bids, key=lambda level: level.get_px(), reverse=True)
        self.asks = sorted(asks, key=lambda level: level.get_px())
        self.bid_px_map = {x.get_px(): x for x in bids}
        self.ask_px_map = {x.get_px(): x for x in asks}

    def get_mid(self) -> Optional[float]:
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid is not None and best_ask is not None:
            return (best_bid.get_px() + best_ask.get_px()) / 2
        else:
            return None

    def get_best_bid(self) -> Optional[BookLevel]:
        if len(self.bids) > 0:
            return self.bids[0]
        else:
            return None

    def get_best_ask(self) -> Optional[BookLevel]:
        if len(self.asks) > 0:
            return self.asks[0]
        else:
            return None

    def get_bid_qty(self, px: float) -> float:
        return self.bid_px_map[px]

    def get_ask_qty(self, px: float) -> float:
        return self.ask_px_map[px]

    def get_bids(self) -> List[BookLevel]:
        return self.bids

    def get_asks(self) -> List[BookLevel]:
        return self.asks

    def is_empty(self) -> bool:
        return len(self.bids) == 0 and len(self.asks) == 0

    def apply_order_book_update(self, update: OrderBookUpdate):
        for bid in update.get_updated_bids():
            if bid.get_qty() == 0:
                if bid.get_px() in self.bid_px_map:
                    del self.bid_px_map[bid.get_px()]
            else:
                self.bid_px_map[bid.get_px()] = bid

        for ask in update.get_updated_asks():
            if ask.get_qty() == 0:
                if ask.get_px() in self.ask_px_map:
                    del self.ask_px_map[ask.get_px()]
            else:
                self.ask_px_map[ask.get_px()] = ask

        self.bids = sorted(self.bid_px_map.values(), key=lambda level: level.get_px(), reverse=True)
        self.asks = sorted(self.ask_px_map.values(), key=lambda level: level.get_px())


class MarketdataService(ABC):
    """
    Base service interface for getting access to live or historical marketdata
    """

    @abstractmethod
    def get_subscribed_instruments(self) -> Signal:
        pass

    @abstractmethod
    def get_order_book_events(self, instrument: ExchangeInstrument) -> Signal:
        pass

    @abstractmethod
    def get_order_books(self, instrument: ExchangeInstrument) -> Signal:
        pass

    @abstractmethod
    def get_trades(self, instrument: ExchangeInstrument) -> Signal:
        pass


class RoutingRule(ABC):
    def __init__(self, targets: List[MarketdataService]):
        self.targets = targets

    def get_targets(self):
        """
        Gets the routed MarketdataService(s)
        """
        return self.targets

    @abstractmethod
    def route(self, instrument: ExchangeInstrument) -> Optional[MarketdataService]:
        """
        Returns the target MDS instance or None if not routeable.
        """
        pass


class ExchangeRoutingRule(RoutingRule):
    """
    Routing rule based on exchange code.
    """

    def __init__(self, exchange_code, mds: MarketdataService):
        super().__init__([mds])
        self.exchange_code = exchange_code
        self.mds = mds

    def route(self, instrument: ExchangeInstrument) -> Optional[MarketdataService]:
        if instrument.get_exchange().get_exchange_code() == self.exchange_code:
            return self.mds
        else:
            return None


class CompositeRoutingRule(RoutingRule):
    """
    Routing rule based on a Chain of Responsibility: it checks each
    of the configured rules until it finds a match.
    """

    def __init__(self, rules: List[RoutingRule]):
        targets = set()
        for rule in rules:
            for target in rule.get_targets():
                targets.add(target)

        super().__init__(list(targets))
        self.rules = rules

    def route(self, instrument: ExchangeInstrument) -> Optional[MarketdataService]:
        for rule in self.rules:
            route = rule.route(instrument)
            if route is not None:
                return route
        return None


class RoutingMarketdataService(MarketdataService):
    """
    Convenience implementation of MarketdataService which routes requests
    to N other MarketdataService instances according to a ruleset.
    """

    def __init__(self, network: Network, rules: RoutingRule):
        self.rules = rules

        class SubscribedInstruments(Function):
            def __init__(self, signals: List[Signal]):
                super().__init__(network, signals)
                self.network = network

            def _call(self):
                for parameter in self.parameters:
                    if self.network.has_activated(parameter):
                        self._update(parameter.get_value())

        subs = []
        for target in rules.get_targets():
            target_subs = target.get_subscribed_instruments()
            subs.append(target_subs)

        self.subscribed_instruments = SubscribedInstruments(subs)
        network.attach(self.subscribed_instruments)

    def get_subscribed_instruments(self) -> Signal:
        return self.subscribed_instruments

    def get_order_book_events(self, instrument: ExchangeInstrument) -> Optional[Signal]:
        route = self.rules.route(instrument)
        if route is not None:
            return route.get_order_book_events(instrument)
        else:
            return None

    def get_order_books(self, instrument: ExchangeInstrument) -> Optional[Signal]:
        route = self.rules.route(instrument)
        if route is not None:
            return route.get_order_books(instrument)
        else:
            return None

    def get_trades(self, instrument: ExchangeInstrument) -> Optional[Signal]:
        route = self.rules.route(instrument)
        if route is not None:
            return route.get_trades(instrument)
        else:
            return None
