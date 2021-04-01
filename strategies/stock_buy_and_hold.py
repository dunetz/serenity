from decimal import Decimal

from money import Money
from tau.core import NetworkScheduler

from serenity.strategy.api import InvestmentStrategy, RebalanceContext, StrategyContext, TradableUniverse, Portfolio, \
    PriceField, RebalanceSchedule, DividendPolicy, MarketScheduleProvider, TradingContext, PricingContext
from serenity.strategy.core import FixedTradableUniverse, OneShotRebalanceOnCloseSchedule, \
    ReinvestTradableDividendPolicy
from serenity.trading.api import Side


class BuyAndHold(InvestmentStrategy):
    """
    A simple strategy that buys and holds AAPL stock and reinvests dividends.
    """
    def __init__(self):
        self.ctx = None
        self.ticker_id = None
        self.ccy = None
        self.default_account = None
        self.initial_investment = None

    def init(self, ctx: StrategyContext):
        self.ctx = ctx
        self.ticker_id = self.ctx.get_configuration()['universe']['ticker_id']
        self.ccy = self.ctx.get_configuration()['portfolio']['ccy']
        self.default_account = self.ctx.get_configuration()['portfolio']['default_account']
        self.initial_investment = self.ctx.get_configuration()['portfolio']['main']['cash_balance']

    def get_initial_portfolio(self) -> Portfolio:
        portfolio = Portfolio([self.default_account], self.ccy)
        portfolio.get_account(self.default_account).get_cash_balance().deposit(Money(self.initial_investment, self.ccy))
        return portfolio

    def get_tradable_universe(self, base_universe: TradableUniverse):
        tradable = base_universe.lookup(self.ticker_id)
        return FixedTradableUniverse([tradable])

    def get_rebalance_schedule(self, scheduler: NetworkScheduler, universe: TradableUniverse,
                               msp: MarketScheduleProvider) -> RebalanceSchedule:
        return OneShotRebalanceOnCloseSchedule(scheduler, universe, msp)

    def get_dividend_policy(self, trading_ctx: TradingContext, pricing_ctx: PricingContext) -> DividendPolicy:
        return ReinvestTradableDividendPolicy(trading_ctx, pricing_ctx)

    def rebalance(self, rebalance_ctx: RebalanceContext):
        # get the instrument to trade
        tradable = rebalance_ctx.get_tradable_universe().lookup(self.ticker_id)

        # compute how many shares we can afford to buy
        initial_cash = rebalance_ctx.get_portfolio().get_account(self.default_account).get_cash_balance().get_balance()
        px = rebalance_ctx.get_pricing_ctx().price(tradable, rebalance_ctx.get_rebalance_time().date(),
                                                   PriceField.CLOSE)
        qty = Decimal(int(initial_cash / px.amount))
        cost = rebalance_ctx.get_trading_ctx().get_trading_cost_per_qty(Side.BUY, tradable)
        est_total_cost = qty * cost
        remaining_cash = initial_cash - qty * px
        while remaining_cash < est_total_cost:
            qty -= 1
            est_total_cost = qty * cost
            remaining_cash = initial_cash - qty * px

        # execute the buy
        tx = rebalance_ctx.get_trading_ctx().buy(tradable, qty)
        rebalance_ctx.get_portfolio().get_account(self.default_account).apply(tx)
