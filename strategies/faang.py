from tau.core import NetworkScheduler

from serenity.strategy.api import InvestmentStrategy, StrategyContext, RebalanceContext, TradingContext, \
    PricingContext, DividendPolicy, TradableUniverse, MarketScheduleProvider, RebalanceSchedule, Portfolio


class FAANG(InvestmentStrategy):
    """
    A simple strategy that buys an equal-weighted portfolio of Facebook, Apple, Amazon, Netflix and Google stock and
    reinvests dividends in the portfolio as they accumulate. At the end of every quarter it rebalances to maintain equal
    weights in the portfolio.
    """
    def init(self, ctx: StrategyContext):
        pass

    def get_initial_portfolio(self) -> Portfolio:
        pass

    def get_tradable_universe(self, base_universe: TradableUniverse):
        pass

    def get_rebalance_schedule(self, scheduler: NetworkScheduler, universe: TradableUniverse,
                               msp: MarketScheduleProvider) -> RebalanceSchedule:
        pass

    def get_dividend_policy(self, trading_ctx: TradingContext, pricing_ctx: PricingContext) -> DividendPolicy:
        pass

    def rebalance(self, rebalance_ctx: RebalanceContext):
        pass
