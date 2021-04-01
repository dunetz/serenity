from uuid import uuid1

from tau.core import HistoricNetworkScheduler
from tau.event import Do

from serenity.model.exchange import ExchangeInstrument
from serenity.trading.api import MarketOrder, Side, OrderStatus, Reject, CancelReject
from serenity.trading.oms import OrderManagerService

from pytest_mock import MockFixture


# noinspection DuplicatedCode
def test_oms_regular_sequence(mocker: MockFixture):
    scheduler = HistoricNetworkScheduler(0, 1000)
    oms = OrderManagerService(scheduler)
    order_statuses = []
    Do(scheduler.get_network(), oms.get_order_events(),
       lambda: order_statuses.append(oms.get_order_events().get_value().get_order_status()))
    instrument = mocker.MagicMock(ExchangeInstrument)
    order = MarketOrder(10, instrument, Side.BUY, 'Main')
    order.set_order_id(str(uuid1()))
    oms.pending_new(order)
    oms.new(order, str(uuid1()))
    oms.apply_fill(order, 1, 10_000, str(uuid1()))
    oms.pending_cancel(order)
    oms.apply_cancel(order, str(uuid1()))
    scheduler.run()
    assert(order_statuses == [OrderStatus.PENDING_NEW, OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED,
                              OrderStatus.PENDING_CANCEL, OrderStatus.CANCELED])


# noinspection DuplicatedCode
def test_oms_late_fill(mocker: MockFixture):
    scheduler = HistoricNetworkScheduler(0, 1000)
    oms = OrderManagerService(scheduler)
    order_events = []
    Do(scheduler.get_network(), oms.get_order_events(), lambda: order_events.append(oms.get_order_events().get_value()))
    instrument = mocker.MagicMock(ExchangeInstrument)
    order = MarketOrder(10, instrument, Side.BUY, 'Main')
    order.set_order_id(str(uuid1()))
    oms.pending_new(order)
    oms.new(order, str(uuid1()))
    oms.pending_cancel(order)
    oms.apply_cancel(order, str(uuid1()))
    oms.apply_fill(order, 1, 10_000, str(uuid1()))
    scheduler.run()
    assert(isinstance(order_events[4], Reject))
    assert(order_events[4].get_message() == 'Order canceled')


# noinspection DuplicatedCode
def test_oms_cancel_not_pending(mocker: MockFixture):
    scheduler = HistoricNetworkScheduler(0, 1000)
    oms = OrderManagerService(scheduler)
    order_events = []
    Do(scheduler.get_network(), oms.get_order_events(), lambda: order_events.append(oms.get_order_events().get_value()))
    instrument = mocker.MagicMock(ExchangeInstrument)
    order = MarketOrder(10, instrument, Side.BUY, 'Main')
    order.set_order_id(str(uuid1()))
    oms.pending_new(order)
    oms.new(order, str(uuid1()))
    oms.apply_cancel(order, str(uuid1()))
    scheduler.run()
    assert(isinstance(order_events[2], CancelReject))
    assert(order_events[2].get_message() == 'Attempt to apply cancel when not pending')
