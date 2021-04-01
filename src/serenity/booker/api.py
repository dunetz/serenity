import logging
from abc import ABC, abstractmethod

from serenity.db.api import connect_serenity_db
from serenity.trading.api import Order, ExecutionReport


class TradeBookingService(ABC):
    """
    Service that books OrderEvents to a "golden source" database for books and records.
    """
    @abstractmethod
    def book(self, order: Order, exec_rpt: ExecutionReport):
        pass


class NullTradeBookingService(TradeBookingService):
    """
    No-op trade booking service for use with backtester
    """
    def book(self, order: Order, exec_rpt: ExecutionReport):
        pass


class TimescaleDbTradeBookingService(TradeBookingService):
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.conn = connect_serenity_db()
        self.cur = self.conn.cursor()

    """
    Implementation of a TradeBookingService based on TimescaleDB
    """
    def book(self, order: Order, exec_rpt: ExecutionReport):
        self.logger.info(f'Booking {exec_rpt} for order ID={order.get_order_id()}')
