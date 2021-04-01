from abc import ABC, abstractmethod
from enum import Enum, auto
from uuid import uuid1

from serenity.model.exchange import ExchangeInstrument


class Side(Enum):
    """
    Order side -- corresponds to long (buy) and short (sell) position.
    """
    BUY = auto()
    SELL = auto()
    UNKNOWN = auto()


class TimeInForce(Enum):
    """
    Enumeration of supported TIF (time-in-force) values for the exchange.
    """
    DAY = auto()
    GTC = auto()
    IOC = auto()
    FOK = auto()


class ExecInst(Enum):
    """
    Enumeration of possible execution instructions to attach to an Order.
    """
    PARTICIPATE_DONT_INITIATE = auto()
    DO_NOT_INCREASE = auto()


class ExecType(Enum):
    NEW = auto()
    DONE_FOR_DAY = auto()
    CANCELED = auto()
    REPLACE = auto()
    PENDING_CANCEL = auto()
    STOPPED = auto()
    REJECTED = auto()
    SUSPENDED = auto()
    PENDING_NEW = auto()
    CALCULATED = auto()
    EXPIRED = auto()
    RESTATED = auto()
    PENDING_REPLACE = auto()
    TRADE = auto()
    TRADE_CORRECT = auto()
    TRADE_CANCEL = auto()
    ORDER_STATUS = auto()


class OrderStatus(Enum):
    NEW = auto()
    PARTIALLY_FILLED = auto()
    FILLED = auto()
    DONE_FOR_DAY = auto()
    CANCELED = auto()
    PENDING_CANCEL = auto()
    STOPPED = auto()
    REJECTED = auto()
    SUSPENDED = auto()
    PENDING_NEW = auto()
    CALCULATED = auto()
    EXPIRED = auto()
    ACCEPTED_FOR_BIDDING = auto()
    PENDING_REPLACE = auto()


class Order:
    """
    Base type for standard order types (limit and market).
    """
    @abstractmethod
    def __init__(self, qty: float, instrument: ExchangeInstrument, side: Side, account: str):
        self.qty = qty
        self.instrument = instrument
        self.side = side
        self.account = account

        self.cl_ord_id = str(uuid1())
        self.order_id = None
        self.exec_inst = None

    def get_cl_ord_id(self) -> str:
        return self.cl_ord_id

    def get_order_id(self) -> str:
        return self.order_id

    def set_order_id(self, order_id: str):
        self.order_id = order_id

    def get_qty(self) -> float:
        return self.qty

    def get_instrument(self) -> ExchangeInstrument:
        return self.instrument

    def get_side(self) -> Side:
        return self.side

    def get_account(self) -> str:
        return self.account

    def get_exec_inst(self) -> ExecInst:
        return self.exec_inst

    def set_exec_inst(self, exec_inst: ExecInst):
        self.exec_inst = exec_inst

    def get_order_parameter(self, name: str) -> object:
        pass

    def set_order_paramter(self, name: str, value: object):
        pass


class LimitOrder(Order):
    """
    An order with a maximum (buy) or minimum (sell) price to trade.
    """
    def __init__(self, price: float, qty: int, instrument: ExchangeInstrument, side: Side,
                 account: str, time_in_force: TimeInForce = TimeInForce.GTC):
        super().__init__(qty, instrument, side, account)
        self.price = price
        self.time_in_force = time_in_force

    def get_price(self) -> float:
        return self.price

    def get_time_in_force(self) -> TimeInForce:
        return self.time_in_force


class MarketOrder(Order):
    """
    An order that executes at the prevailing market price.
    """
    def __init__(self, qty: int, instrument: ExchangeInstrument, side: Side, account: str):
        super().__init__(qty, instrument, side, account)


class StopOrder(Order):
    """
    An order that executes at the prevailing market price when the price drops below stop_px.
    """
    def __init__(self, qty: int, instrument: ExchangeInstrument, side: Side, account: str, stop_px: float):
        super().__init__(qty, instrument, side, account)
        self.stop_px = stop_px

    def get_stop_px(self):
        return self.stop_px


class OrderFactory:
    """
    Helper factory for creating instances of different order types.
    """

    def __init__(self, account: str):
        self.account = account

    def get_account(self):
        return self.account

    def create_market_order(self, side: Side, qty: int, instrument: ExchangeInstrument) -> MarketOrder:
        return MarketOrder(qty, instrument, side, self.account)

    def create_limit_order(self, side: Side, qty: int, price: float, instrument: ExchangeInstrument,
                           time_in_force: TimeInForce = TimeInForce.GTC) -> LimitOrder:
        return LimitOrder(price, qty, instrument, side, self.account, time_in_force)

    def create_stop_order(self, side: Side, qty: int, stop_px: float, instrument: ExchangeInstrument) -> StopOrder:
        return StopOrder(qty, instrument, side, self.account, stop_px)


class OrderEvent(ABC):
    pass


class ExecutionReport(OrderEvent):
    def __init__(self, order_id: str, cl_ord_id: str, exec_id: str, exec_type: ExecType,
                 order_status: OrderStatus, cum_qty: float, leaves_qty: float, last_px: float,
                 last_qty: float):
        self.order_id = order_id
        self.cl_ord_id = cl_ord_id
        self.exec_id = exec_id
        self.exec_type = exec_type
        self.order_status = order_status
        self.cum_qty = cum_qty
        self.leaves_qty = leaves_qty
        self.last_px = last_px
        self.last_qty = last_qty

    def get_order_id(self) -> str:
        return self.order_id

    def get_cl_ord_id(self) -> str:
        return self.cl_ord_id

    def get_exec_id(self) -> str:
        return self.exec_id

    def get_exec_type(self) -> ExecType:
        return self.exec_type

    def get_order_status(self) -> OrderStatus:
        return self.order_status

    def get_cum_qty(self) -> float:
        return self.cum_qty

    def get_leaves_qty(self) -> float:
        return self.leaves_qty

    def get_last_px(self) -> float:
        return self.last_px

    def get_last_qty(self) -> float:
        return self.last_qty

    def is_fill(self) -> bool:
        return self.order_status in [OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED]

    def __str__(self) -> str:
        return f'ExecutionReport[exec_type={self.exec_type}, order_status={self.order_status}, ' \
               f'leaves_qty={self.leaves_qty}, last_qty={self.last_qty}, last_px={self.last_px}]'


class OrderPlacer(ABC):
    """
    Abstraction for the trading connection to the exchange.
    """

    def __init__(self, order_factory: OrderFactory):
        self.order_factory = order_factory

    def get_order_factory(self) -> OrderFactory:
        """"
        :return: the associated order factory object for this OrderPlacer
        """
        return self.order_factory

    @abstractmethod
    def submit(self, order: Order):
        """
        Places the given Order on the exchange
        :param order: order details
        """
        pass

    @abstractmethod
    def cancel(self, order: Order):
        """
        Cancels the referenced order.
        :param order: order to cancel
        """
        pass


class OrderState:
    # forward declaration
    def create_execution_report(self, exec_id: str) -> ExecutionReport:
        pass


# noinspection PyRedeclaration
class OrderState:
    def __init__(self, order: Order, ord_status: OrderStatus = OrderStatus.PENDING_NEW,
                 exec_type: ExecType = ExecType.TRADE):
        self.order = order
        self.ord_status = ord_status
        self.exec_type = exec_type
        self.cum_qty = 0
        self.last_qty = 0
        self.last_px = 0

    def get_order(self) -> Order:
        return self.order

    def get_ord_status(self) -> OrderStatus:
        return self.ord_status

    def get_exec_type(self) -> ExecType:
        return self.exec_type

    def get_cum_qty(self) -> float:
        return self.cum_qty

    def get_last_qty(self) -> float:
        return self.last_qty

    def get_last_px(self) -> float:
        return self.last_px

    def get_leaves_qty(self) -> float:
        if self.is_terminal():
            return 0
        else:
            return self.order.get_qty() - self.cum_qty

    def is_terminal(self) -> bool:
        return self.ord_status in [OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.EXPIRED,
                                   OrderStatus.DONE_FOR_DAY, OrderStatus.REJECTED]

    def transition(self, ord_status: OrderStatus, exec_type: ExecType) -> OrderState:
        new_state = OrderState(self.order, ord_status, exec_type)
        new_state.cum_qty = self.cum_qty
        new_state.last_qty = self.last_qty
        new_state.last_px = self.last_px
        return new_state

    def apply_fill(self, fill_qty: float, fill_px: float) -> bool:
        new_cum_qty = self.cum_qty + fill_qty
        self.last_qty = fill_qty
        self.last_px = fill_px
        if new_cum_qty > self.order.get_qty():
            return False
        else:
            self.cum_qty = new_cum_qty
            return True

    def is_fully_filled(self):
        return self.cum_qty == self.order.get_qty()

    def create_execution_report(self, exec_id: str) -> ExecutionReport:
        return ExecutionReport(self.order.get_order_id(), self.order.get_cl_ord_id(), exec_id,
                               self.get_exec_type(), self.get_ord_status(), self.get_cum_qty(), self.get_leaves_qty(),
                               self.get_last_px(), self.get_last_qty())


class Reject(OrderEvent):
    def __init__(self, message: str):
        self.message = message

    def get_message(self) -> str:
        return self.message

    def __str__(self):
        return f'Reject[message={self.message}]'


class CancelReject(OrderEvent):
    def __init__(self, cl_ord_id: str, orig_cl_ord_id: str, message: str):
        self.cl_ord_id = cl_ord_id
        self.orig_cl_ord_id = orig_cl_ord_id
        self.message = message

    def get_cl_ord_id(self) -> str:
        return self.cl_ord_id

    def get_orig_cl_ord_id(self) -> str:
        return self.orig_cl_ord_id

    def get_message(self) -> str:
        return self.message

    def __str__(self):
        return f'CancelReject[message={self.message}]'
