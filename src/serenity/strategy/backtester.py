import logging
from pathlib import Path

import fire
import toml
from tau.core import HistoricNetworkScheduler, Event

from serenity.data.sharadar_api import create_sharadar_session
from serenity.strategy.api import PriceField, InvestmentStrategy, Portfolio
from serenity.strategy.core import TradableUniversePricingContext, DefaultRebalanceContext, \
    ZeroCommissionTradingCostCalculator, PandasMarketCalendarMarketScheduleProvider, TradableUniverseDividendContext, \
    DailyProcessingSchedule
from serenity.strategy.historical import BacktestStrategyContext, MarketOnCloseTradingSimulator
from serenity.strategy.sharadar import SharadarTradableUniverse, SharadarPricingContext, SharadarDividendContext
from serenity.strategy.utils import StrategyLoader
from serenity.utils import init_logging


class InvestmentStrategyBacktester:
    """"
    Serenity investment strategy backtester.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, scheduler: HistoricNetworkScheduler):
        self.logger.info('Serenity investment strategy backtester starting up')
        self.scheduler = scheduler

    def run(self, strategy_instance: InvestmentStrategy, config: dict) -> Portfolio:
        session = create_sharadar_session()
        base_universe = SharadarTradableUniverse(session)

        strategy_ctx = BacktestStrategyContext(self.scheduler, config)
        strategy_instance.init(strategy_ctx)
        universe = strategy_instance.get_tradable_universe(base_universe)

        portfolio = strategy_instance.get_initial_portfolio()

        base_pricing_ctx = SharadarPricingContext(session)
        pricing_ctx = TradableUniversePricingContext(strategy_ctx, universe, base_pricing_ctx, PriceField.CLOSE)

        base_div_ctx = SharadarDividendContext(session)
        div_ctx = TradableUniverseDividendContext(strategy_ctx, universe, base_div_ctx)

        tc_calc = ZeroCommissionTradingCostCalculator()
        trading_ctx = MarketOnCloseTradingSimulator(tc_calc, self.scheduler, pricing_ctx)

        rebalance_ctx = DefaultRebalanceContext(self.scheduler, portfolio, universe, pricing_ctx, div_ctx, trading_ctx)

        class DailyProcessingAction(Event):
            def __init__(self, backtester: InvestmentStrategyBacktester):
                self.backtester = backtester

            def on_activate(self) -> bool:
                today = self.backtester.scheduler.get_clock().get_time()
                self.backtester.logger.info(f'Performing daily bookkeeping for {today.date()}')

                # process dividends
                div_policy = strategy_instance.get_dividend_policy(trading_ctx, pricing_ctx)
                for account in portfolio.get_accounts():
                    for position in account.get_positions():
                        div = div_ctx.get_dividend(position.get_tradable(), rebalance_ctx.get_rebalance_time().date())
                        if div is not None:
                            self.backtester.logger.info(f'Dividend paid on {position.get_tradable().get_symbol()}'
                                                        f': {div}')
                            div_policy.apply(div, rebalance_ctx.get_portfolio())

                # mark positions
                portfolio.mark(today.date(), pricing_ctx)

                return True

        class RebalanceAction(Event):
            def __init__(self, backtester: InvestmentStrategyBacktester):
                self.backtester = backtester

            def on_activate(self) -> bool:
                self.backtester.logger.info(f'Rebalancing at {rebalance_ctx.get_rebalance_time()}')
                strategy_instance.rebalance(rebalance_ctx)
                return True

        msp = PandasMarketCalendarMarketScheduleProvider(self.scheduler, 'US/Eastern')
        rebalance_event = strategy_instance.get_rebalance_schedule(self.scheduler, universe, msp).get_rebalance_event()
        daily_close_event = DailyProcessingSchedule(universe, msp).get_market_close_event()
        self.scheduler.get_network().connect(rebalance_event, RebalanceAction(self))
        self.scheduler.get_network().connect(daily_close_event, DailyProcessingAction(self))

        return portfolio


def main(config_path: str, strategy_dir: str, start_time: str, end_time: str):
    init_logging()

    config = toml.load(config_path)
    strategy_module = config['strategy']['module']
    strategy_class = config['strategy']['class']
    loader = StrategyLoader(Path(strategy_dir))
    strategy_instance = loader.load(strategy_module, strategy_class)

    scheduler = HistoricNetworkScheduler.new_instance(start_time, end_time)
    backtester = InvestmentStrategyBacktester(scheduler)
    portfolio = backtester.run(strategy_instance, config)
    scheduler.run()

    for account in portfolio.get_accounts():
        print(f'Account: [{account.get_name()}]')
        print(f'\tcash: {account.get_cash_balance().get_balance()}')
        for position in account.get_positions():
            print(f'\t{position.get_tradable().get_symbol()}: {position.get_qty()} shares ({position.get_notional()})')


if __name__ == '__main__':
    fire.Fire(main)
