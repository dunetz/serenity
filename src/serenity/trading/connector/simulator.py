from uuid import uuid1

from tau.core import Signal, NetworkScheduler, Event

from serenity.marketdata.api import MarketdataService
from serenity.trading.api import OrderPlacer, Order, OrderFactory, Side, StopOrder, LimitOrder, MarketOrder
from serenity.trading.oms import OrderManagerService


class AutoFillOrderPlacer(OrderPlacer):
    def __init__(self, scheduler: NetworkScheduler, oms: OrderManagerService, mds: MarketdataService, account: str):
        super().__init__(OrderFactory(account))
        self.scheduler = scheduler
        self.oms = oms
        self.mds = mds

    def submit(self, order: Order):
        order.set_order_id(str(uuid1()))
        self.oms.pending_new(order)
        self.oms.new(order, str(uuid1()))

        class FillScheduler(Event):
            # noinspection PyShadowingNames
            def __init__(self, order_placer: AutoFillOrderPlacer, trades: Signal, order_books: Signal):
                self.order_placer = order_placer
                self.trades = trades
                self.order_books = order_books
                self.fired = False

            def on_activate(self) -> bool:
                if self.fired or self.order_placer.oms.is_terminal(order.get_cl_ord_id()):
                    return False

                if self.order_placer.scheduler.get_network().has_activated(self.trades):
                    if isinstance(order, StopOrder):
                        if self.trades.get_value().get_price() <= order.get_stop_px():
                            self.__apply_fill_at_market_px(order)
                            self.fired = True
                elif self.order_placer.scheduler.get_network().has_activated(self.order_books):
                    if isinstance(order, LimitOrder) or isinstance(order, MarketOrder):
                        self.__apply_fill_at_market_px(order)
                        self.fired = True

                return True

            # noinspection PyShadowingNames
            def __apply_fill_at_market_px(self, order: Order):
                if order.get_side() == Side.BUY:
                    fill_px = self.order_books.get_value().get_best_ask().get_px()
                    fill_qty_at_touch = self.order_books.get_value().get_best_ask().get_qty()
                else:
                    fill_px = self.order_books.get_value().get_best_bid().get_px()
                    fill_qty_at_touch = self.order_books.get_value().get_best_bid().get_qty()

                if order.get_qty() > fill_qty_at_touch:
                    self.order_placer.oms.apply_fill(order, fill_qty_at_touch, fill_px, str(uuid1()))
                    self.order_placer.oms.apply_fill(order, order.get_qty() - fill_qty_at_touch, fill_px, str(uuid1()))
                else:
                    self.order_placer.oms.apply_fill(order, order.get_qty(), fill_px, str(uuid1()))
                self.fired = True

        trades = self.mds.get_trades(order.get_instrument())
        order_books = self.mds.get_order_books(order.get_instrument())

        fill_scheduler = FillScheduler(self, trades, order_books)
        self.scheduler.get_network().connect(trades, fill_scheduler)
        self.scheduler.get_network().connect(order_books, fill_scheduler)

    def cancel(self, order):
        self.oms.pending_cancel(order)
        self.oms.apply_cancel(order, str(uuid1()))
