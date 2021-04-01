from uuid import uuid1

from tau.core import NetworkScheduler, MutableSignal, Event, Signal

from serenity.booker.api import TradeBookingService, NullTradeBookingService
from serenity.trading.api import ExecutionReport, Order, Reject, OrderState, OrderStatus, ExecType, CancelReject, \
    OrderPlacer


class OrderManagerService:
    def __init__(self, scheduler: NetworkScheduler, booker: TradeBookingService = NullTradeBookingService()):
        self.scheduler = scheduler
        self.order_state_by_cl_ord_id = {}
        self.order_by_cl_ord_id = {}
        self.order_events = MutableSignal()
        self.orders = MutableSignal()

        self.scheduler.get_network().attach(self.orders)
        self.scheduler.get_network().attach(self.order_events)

        class OnBookingEvent(Event):
            def __init__(self, oms: OrderManagerService):
                self.oms = oms

            def on_activate(self) -> bool:
                if self.oms.order_events.is_valid():
                    order_event = self.oms.order_events.get_value()
                    if isinstance(order_event, ExecutionReport):
                        cl_ord_id = order_event.get_cl_ord_id()
                        order = self.oms.get_order_by_cl_ord_id(cl_ord_id)
                        booker.book(order, order_event)
                return False

        self.scheduler.get_network().connect(self.order_events, OnBookingEvent(self))

    def get_order_events(self) -> Signal:
        return self.order_events

    def get_orders(self) -> Signal:
        return self.orders

    def get_order_by_cl_ord_id(self, cl_ord_id) -> Order:
        return self.order_by_cl_ord_id.get(cl_ord_id, None)

    def track_order(self, order: Order):
        cl_ord_id = order.get_cl_ord_id()
        pending_state = OrderState(order)
        if cl_ord_id is not None:
            self.order_by_cl_ord_id[cl_ord_id] = order
            self.order_state_by_cl_ord_id[cl_ord_id] = pending_state
        return pending_state

    def pending_new(self, order: Order):
        pending_state = self.track_order(order)
        self.scheduler.schedule_update(self.order_events, pending_state.create_execution_report(str(uuid1())))
        self.scheduler.schedule_update(self.orders, order)

    def new(self, order: Order, exec_id: str):
        cl_ord_id = order.get_cl_ord_id()
        if cl_ord_id is None:
            self.scheduler.schedule_update(self.order_events, Reject('Order missing cl_ord_id'))
            return

        order_state = self.order_state_by_cl_ord_id[cl_ord_id]
        new_state = order_state.transition(OrderStatus.NEW, ExecType.NEW)
        self.order_state_by_cl_ord_id[cl_ord_id] = new_state
        self.scheduler.schedule_update(self.order_events, new_state.create_execution_report(exec_id))

    def pending_cancel(self, order: Order):
        cl_ord_id = order.get_cl_ord_id()
        if cl_ord_id is None:
            self.scheduler.schedule_update(self.order_events, Reject('Order missing cl_ord_id'))
            return

        order_state = self.order_state_by_cl_ord_id[cl_ord_id]
        if order_state is None:
            self.scheduler.schedule_update(self.order_events, CancelReject(cl_ord_id, cl_ord_id,
                                                                           'Attempt to pending cancel unknown order'))
        elif order_state.is_terminal():
            self.scheduler.schedule_update(self.order_events, CancelReject(cl_ord_id, cl_ord_id,
                                                                           'Attempt to pending cancel terminal order'))
        else:
            pending_state = order_state.transition(OrderStatus.PENDING_CANCEL, ExecType.PENDING_CANCEL)
            self.order_state_by_cl_ord_id[cl_ord_id] = pending_state
            self.scheduler.schedule_update(self.order_events, pending_state.create_execution_report(str(uuid1())))

    def apply_cancel(self, order: Order, exec_id: str):
        cl_ord_id = order.get_cl_ord_id()
        if cl_ord_id is None:
            self.scheduler.schedule_update(self.order_events, Reject('Order missing cl_ord_id'))
            return

        order_state = self.order_state_by_cl_ord_id[cl_ord_id]
        ord_status = order_state.get_ord_status()
        if order_state.is_terminal():
            self.scheduler.schedule_update(self.order_events, CancelReject(cl_ord_id, cl_ord_id,
                                                                           'Attempt to apply cancel to terminal order'))
        elif ord_status == OrderStatus.PENDING_CANCEL:
            cancel_state = order_state.transition(OrderStatus.CANCELED, ExecType.CANCELED)
            self.order_state_by_cl_ord_id[cl_ord_id] = cancel_state
            self.scheduler.schedule_update(self.order_events, cancel_state.create_execution_report(exec_id))
        else:
            self.scheduler.schedule_update(self.order_events, CancelReject(cl_ord_id, cl_ord_id,
                                                                           'Attempt to apply cancel when not pending'))

    def apply_fill(self, order: Order, fill_qty: float, fill_px: float, exec_id: str):
        cl_ord_id = order.get_cl_ord_id()
        if cl_ord_id is None:
            self.scheduler.schedule_update(self.order_events, Reject('Order missing cl_ord_id'))
            return

        order_state = self.order_state_by_cl_ord_id[cl_ord_id]
        ord_status = order_state.get_ord_status()
        if ord_status in [OrderStatus.FILLED]:
            self.scheduler.schedule_update(self.order_events, Reject('Order fully filled'))
        elif ord_status in [OrderStatus.CANCELED]:
            self.scheduler.schedule_update(self.order_events, Reject('Order canceled'))
        elif ord_status in [OrderStatus.EXPIRED]:
            self.scheduler.schedule_update(self.order_events, Reject('Order expired'))
        elif ord_status in [OrderStatus.DONE_FOR_DAY]:
            self.scheduler.schedule_update(self.order_events, Reject('Order done for day'))
        elif ord_status in [OrderStatus.REJECTED]:
            self.scheduler.schedule_update(self.order_events, Reject('Order rejected'))
        elif order_state.apply_fill(fill_qty, fill_px):
            if order_state.is_fully_filled():
                fill_state = order_state.transition(OrderStatus.FILLED, ExecType.TRADE)
            else:
                fill_state = order_state.transition(OrderStatus.PARTIALLY_FILLED, ExecType.TRADE)
            self.order_state_by_cl_ord_id[cl_ord_id] = fill_state
            self.scheduler.schedule_update(self.order_events, fill_state.create_execution_report(exec_id))

    def reject(self, order, msg: str):
        cl_ord_id = order.get_cl_ord_id()
        if cl_ord_id is not None:
            order_state = self.order_state_by_cl_ord_id[cl_ord_id]
            order_state = order_state.transition(OrderStatus.REJECTED, ExecType.REJECTED)
            self.order_state_by_cl_ord_id[cl_ord_id] = order_state
        else:
            msg = f'{msg}; WARNING: missing order_id'

        self.scheduler.schedule_update(self.order_events, Reject(msg))

    def is_terminal(self, cl_ord_id) -> bool:
        return self.order_state_by_cl_ord_id[cl_ord_id].is_terminal()


class OrderPlacerService:
    def __init__(self, scheduler: NetworkScheduler, oms: OrderManagerService):
        self.scheduler = scheduler
        self.oms = oms
        self.order_placers = {}

    def get_order_manager_service(self) -> OrderManagerService:
        return self.oms

    def get_order_placer(self, uri: str) -> OrderPlacer:
        return self.order_placers.get(uri)

    def register_order_placer(self, uri: str, order_placer: OrderPlacer):
        self.order_placers[uri] = order_placer
