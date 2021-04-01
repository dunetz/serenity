import datetime
import logging
from decimal import Decimal
from typing import Optional

from money import Money
from tau.core import HistoricNetworkScheduler, NetworkScheduler

from serenity.strategy.api import StrategyContext, TradingContext, Tradable, Transaction, TradingCostCalculator, \
    PricingContext, PriceField
from serenity.trading.api import Side


class BacktestStrategyContext(StrategyContext):
    def __init__(self, scheduler: HistoricNetworkScheduler, config: dict):
        self.scheduler = scheduler
        self.config = config

    def get_start_time(self) -> datetime.datetime:
        return self.scheduler.get_clock().get_start_time()

    def get_end_time(self) -> Optional[datetime.datetime]:
        return self.scheduler.get_clock().get_end_time()

    def get_configuration(self) -> dict:
        return self.config


class MarketOnCloseTradingSimulator(TradingContext):
    logger = logging.getLogger(__name__)

    def __init__(self, tc_calc: TradingCostCalculator, scheduler: NetworkScheduler, pricing_ctx: PricingContext):
        super().__init__(tc_calc)
        self.scheduler = scheduler
        self.pricing_ctx = pricing_ctx

    def buy(self, tradable: Tradable, qty: Decimal, limit_px: Optional[Decimal] = None) -> Transaction:
        side = Side.BUY
        return self._execute_market_on_close(side, tradable, qty)

    def sell(self, tradable: Tradable, qty: Decimal, limit_px: Optional[Decimal] = None) -> Transaction:
        side = Side.SELL
        return self._execute_market_on_close(side, tradable, qty)

    def _execute_market_on_close(self, side: Side, tradable: Tradable, qty: Decimal) -> Transaction:
        execution_time = self.scheduler.get_clock().get_time()
        executed_price = self.pricing_ctx.price(tradable, execution_time.date(), PriceField.CLOSE)
        executed_cost_per_qty = self.get_trading_cost_per_qty(side, tradable)
        executed_cost = Money(executed_cost_per_qty.amount * qty, executed_cost_per_qty.currency)
        tx = Transaction(side, tradable, qty, qty, executed_price, executed_cost)
        self.logger.info(f'executing MOC transaction: {tx}')
        return tx
