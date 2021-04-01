from abc import ABC, abstractmethod

from tau.core import NetworkScheduler, Event, MutableSignal

from serenity.model.exchange import ExchangeInstrument
from serenity.model.instrument import Currency
from serenity.trading.api import ExecutionReport, Side
from serenity.trading.oms import OrderManagerService


class ExchangePosition:
    def __init__(self, account: str, currency: Currency, qty: float = 0):
        self.account = account
        self.currency = currency
        self.qty = qty

    def get_account(self) -> str:
        return self.account

    def get_currency(self) -> Currency:
        return self.currency

    def get_qty(self) -> float:
        return self.qty

    def __str__(self):
        return f'ExchangePosition[account={self.account}, currency={self.currency}, qty={self.qty}]'


class Position:
    # forward declaration
    pass


# noinspection PyRedeclaration
class Position:
    def __init__(self, account: str, instrument: ExchangeInstrument, qty: float = 0):
        self.account = account
        self.instrument = instrument
        self.qty = qty

    def get_account(self) -> str:
        return self.account

    def get_instrument(self) -> ExchangeInstrument:
        return self.instrument

    def get_qty(self) -> float:
        return self.qty

    def apply_qty(self, qty: float) -> Position:
        return Position(self.account, self.instrument, self.qty + qty)

    def __str__(self):
        return f'Position[account={self.account}, instrument={self.instrument}, qty={self.qty}]'


class ExchangePositionService(ABC):
    def __init__(self, scheduler: NetworkScheduler):
        self.scheduler = scheduler
        self.exchange_positions = MutableSignal()
        self.scheduler.get_network().attach(self.exchange_positions)

    def get_exchange_positions(self):
        return self.exchange_positions

    @abstractmethod
    def subscribe(self):
        pass


class NullExchangePositionService(ExchangePositionService):
    def __init__(self, scheduler: NetworkScheduler):
        super().__init__(scheduler)

    def subscribe(self):
        pass


class PositionService(Event):
    def __init__(self, scheduler: NetworkScheduler, oms: OrderManagerService):
        self.scheduler = scheduler
        self.oms = oms
        self.positions = {}

        self.scheduler.get_network().connect(oms.get_order_events(), self)

    def get_position(self, account: str, instrument: ExchangeInstrument) -> MutableSignal:
        position = self.positions.get((account, instrument), None)
        if position is None:
            position = MutableSignal(Position(account, instrument))
            self.positions[(account, instrument)] = position
            self.scheduler.get_network().attach(position)
        return position

    def on_activate(self) -> bool:
        if self.scheduler.get_network().has_activated(self.oms.get_order_events()):
            order_events = self.oms.get_order_events()
            order_event = order_events.get_value()
            if isinstance(order_event, ExecutionReport) and order_event.is_fill():
                order = self.oms.get_order_by_cl_ord_id(order_event.get_cl_ord_id())
                account = order.get_account()
                last_qty = order_event.get_last_qty()
                if order.get_side() == Side.SELL:
                    last_qty *= -1
                position = self.get_position(account, order.get_instrument())
                self.scheduler.schedule_update(position, lambda: position.get_value().apply_qty(last_qty))
        return False
