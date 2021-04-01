import datetime
from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum, auto
from typing import Optional, List

import pandas as pd
from money import Money
from tau.core import Event, NetworkScheduler

from serenity.trading.api import Side


class Tradable(ABC):
    """
    Abstraction for any tradable financial instrument. Positions are managed based on Tradables, and execution
    through the Trading API is done through them as well.
    """

    @abstractmethod
    def get_ticker_id(self) -> int:
        """
        Stable integer identifier for this tradable instrument. This is meant to stay constant even if
        the listed ticker symbol for the instrument changes, and should be used in all data structures.
        """
        pass

    @abstractmethod
    def get_symbol(self) -> str:
        """
        Current standard symbol used for referencing this instrument for trading.
        """

    @abstractmethod
    def get_market(self) -> str:
        """
        Primary market where this financial instrument trades
        """

    @abstractmethod
    def get_name(self) -> str:
        """
        Friendly short name for this financial instrument.
        """
        pass

    @abstractmethod
    def get_currency(self) -> str:
        """
        Settlement and reporting currency for this financial instrument.
        """
        pass


class TradableUniverse(ABC):
    """
    The universe of all known Tradable instruments. Typically these objects are nested, with a base
    universe representing all defined Tradables and a derived one restricting that universe to a
    much smaller set which the investment strategy is allowed to trade.
    """

    @abstractmethod
    def lookup(self, ticker_id: int) -> Tradable:
        """
        Looks up a Tradable by its unique ticker ID, or raises an Error if not found; this call should never return None
        as the value so it can be safely chained.
        """
        pass

    @abstractmethod
    def all(self) -> List[Tradable]:
        """
        Gets a list of all supported Tradables in this universe, or the empty list if nothing supported.
        """
        pass


class PriceField(Enum):
    """
    Key for determining which time of day's price is used when pricing an object. This can be extended if needed
    to cover mid, bid, ask, various VWAP prices, etc., but we're keeping it simple for now and limiting to open & close
    prices for the instrument.
    """
    OPEN = auto()
    CLOSE = auto()


class PricingContext(ABC):
    """
    Plugin point for providing prices (both as-of and historical) for Tradable objects. Note that this API
    uses date objects, not datetime, as the time is implied by the chosen PriceField.
    """

    @abstractmethod
    def price(self, tradable: Tradable, price_date: datetime.date, price_field: PriceField) -> Money:
        """
        Looks up the price as of the given date and logical time (open vs. close), and raises an error if not found.
        """
        pass

    @abstractmethod
    def get_price_history(self, tradables: List[Tradable], start_date: datetime.date,
                          end_date: datetime.date, price_field: PriceField) -> pd.DataFrame:
        """
        For the given date range and list of tradables returns a matrix with dates as rows
        and Tradable ticker ID's as columns, and the selected PriceField as values, and raises
        an implementation-specific error if no matches.
        """
        pass


class Transaction:
    """
    Snapshot of revelant inforamtion about a single trade of a financial instrument.
    """

    def __init__(self, side: Side, tradable: Tradable, qty: Decimal, executed_qty: Decimal,
                 executed_price: Money, executed_cost: Money):
        self.side = side
        self.tradable = tradable
        self.qty = qty
        self.executed_qty = executed_qty
        self.executed_price = executed_price
        self.executed_cost = executed_cost
        self.executed_notional = Money(self.executed_qty * self.executed_price.amount, self.executed_price.currency)

    def get_side(self) -> Side:
        """
        Gets the executed side of the tranasction.
        """
        return self.side

    def get_tradable(self) -> Tradable:
        """
        Gets the instrument traded.
        """
        return self.tradable

    def get_qty(self) -> Decimal:
        """
        Gets the (potentially fractional, depending on instrument) quantity the strategy attemped to trade.
        """
        return self.qty

    def get_executed_qty(self) -> Decimal:
        """
        Gets the (potentially fractional, depending on instrument) actual quantity executed.
        """
        return self.executed_qty

    def get_executed_price(self) -> Money:
        """
        Gets the average price at which the quantity was executed.
        """
        return self.executed_price

    def get_executed_cost(self) -> Money:
        """
        Gets the total cost of the transaction.
        """
        return self.executed_cost

    def get_executed_notional(self) -> Money:
        """
        Gets the monetary value of the transaction executed.
        """
        return self.executed_notional

    def __str__(self):
        return f'{self.side} {self.qty} @ {self.executed_price} (cost={self.executed_cost})'


class CashBalance:
    """
    Object representing the cash position in an account.
    """
    def __init__(self, ccy: str):
        self.balance = Money(0, ccy)

    def get_balance(self) -> Money:
        """
        Gets the cash amount held in the account.
        """
        return self.balance

    def deposit(self, money: Money):
        """
        Adds the given amount of money to the cash position.
        """
        self.balance += money

    def withdraw(self, money: Money):
        """
        Removes the given amount of money from the cash position.
        """
        self.balance -= money


class Position:
    """
    Object representing the portfolio's holdings of a financial instrument.
    """
    def __init__(self, tradable: Tradable):
        self.tradable = tradable
        self.qty = Decimal(0.0)
        self.px = Money(0.0, tradable.get_currency())

    def get_tradable(self) -> Tradable:
        """
        Gets the financial instrument held in this position.
        """
        return self.tradable

    def get_qty(self) -> Decimal:
        """
        Gets the (possibly fractional) quantity of the instrument held.
        """
        return self.qty

    def get_notional(self) -> Money:
        """
        Gets the monetary value of this position. Note that the price used is based on the most recent mark,
        or zero if the position has never been marked.
        """
        return Money(self.px.amount * self.qty, self.px.currency)

    def apply(self, tx: Transaction, cash: CashBalance):
        """
        Applies the executed trade to this position and to the associated CashBalance.
        """
        if tx.get_side() == Side.BUY:
            self.qty += tx.get_qty()
            cash.withdraw(tx.get_executed_cost())
            cash.withdraw(tx.get_executed_notional())
        elif tx.get_side() == Side.SELL:
            self.qty -= tx.get_qty()
            cash.withdraw(tx.get_executed_cost())
            cash.deposit(tx.get_executed_notional())
        else:
            raise ValueError(f'Side not handled: {tx.get_side()}')

    def mark(self, mark_date: datetime.date, pricing_ctx: PricingContext):
        """
        Marks this position to market as of the given mark date and using the given pricer.
        """
        self.px = pricing_ctx.price(self.tradable, mark_date, PriceField.CLOSE)


class Account:
    """
    A logical entry in the portfolio of holdings. Portfolios hold accounts; accounts hold cash & positions.
    Note we do not at this time support multi-currency accounts; if you need this facility it can be done
    with multiple accounts with different currencies for their cash positions, but without integrated FX data
    and ability to execute FX transactions it's not very useful.
    """
    def __init__(self, name: str, ccy: str):
        self.name = name
        self.cash_balance = CashBalance(ccy)
        self.positions = {}

    def get_name(self) -> str:
        """
        Gets the logical name for this account. By convention this should be lowercase and all one word, but can
        be any string.
        """
        return self.name

    def get_cash_balance(self) -> CashBalance:
        """
        Gets the associated cash position for this account.
        """
        return self.cash_balance

    def get_position(self, tradable: Tradable) -> Position:
        """
        Gets and if necedssary creates a position in the given Tradable.
        """
        position = self.positions.get(tradable.get_ticker_id(), None)
        if position is None:
            position = Position(tradable)
            self.positions[tradable.get_ticker_id()] = position
        return position

    def get_positions(self) -> List[Position]:
        """
        Gets all created positions in this account.
        """
        return list(self.positions.values())

    def apply(self, tx: Transaction):
        """
        Applies the given Transaction to the Position for the same Tradable object.
        """
        self.get_position(tx.get_tradable()).apply(tx, self.get_cash_balance())

    def mark(self, mark_date: datetime.date, pricing_ctx: PricingContext):
        """
        Marks all positions to market as of the given mark_date.
        """
        for position in self.positions.values():
            position.mark(mark_date, pricing_ctx)


class Portfolio:
    """
    A logical representation of the holdings for a strategy. Portfolios are broken down into accounts which in
    turn hold cash and Tradable positions.
    """
    def __init__(self, account_names: List[str], ccy: str):
        self.accounts = {account_name: Account(account_name, ccy) for account_name in account_names}
        self.ccy = ccy

    def get_account(self, name: str) -> Account:
        """
        Looks up the given account by name.
        """
        return self.accounts[name]

    def get_accounts(self) -> List[Account]:
        """
        Gets all accounts in this portfolio.
        """
        return list(self.accounts.values())

    def mark(self, mark_date: datetime.date, pricing_ctx: PricingContext):
        """
        Marks all accounts to market as of the given mark_date.
        """
        for account in self.accounts.values():
            account.mark(mark_date, pricing_ctx)


class Dividend:
    """
    Basic representation of a cash dividend. Stock dividends are not handled, nor are corporate actions like stock
    splits. The assumption at this time is that the underlying equity research database makes these adjustments,
    as is done by Sharadar today.
    """
    def __init__(self, tradable: Tradable, payment_date: datetime.date, amount: Money):
        self.tradable = tradable
        self.payment_date = payment_date
        self.amount = amount

    def get_tradable(self) -> Tradable:
        """
        Gets the instrument on which the dividend has been paid.
        """
        return self.tradable

    def get_payment_date(self) -> datetime.date:
        """
        Gets the date on which the dividend was paid.
        """
        return self.payment_date

    def get_amount(self) -> Money:
        """
        Gets the cash value of the dividend.
        """
        return self.amount

    def __str__(self) -> str:
        return f'{self.amount} paid on {self.payment_date}'


class DividendPolicy(ABC):
    """
    Plugin point that lets the strategy author determine what gets done with dividends, e.g. whether to collect
    cash or to the reinvest the dividends and if so how.
    """
    @abstractmethod
    def apply(self, div: Dividend, pf: Portfolio):
        """
        Applies the given dividend to the portfolio according to the strategy's trading rules.
        """
        pass


class TradingCostCalculator(ABC):
    """
    Plugin point that lets the strategy engine compute expected trading costs per quantity traded.
    """
    @abstractmethod
    def get_trading_cost_per_qty(self, side: Side, tradable: Tradable):
        """
        Gets the unit trading cost per quantity for the given Tradable and side. Note this does not given
        flexibility for all possible policies for execution costs like sliding schedules based on qty traded
        or costs dependent on executed price, so this may need extension in future.
        """
        pass


class TradingContext(ABC):
    """
    Abstraction for the exchange connector or trading simulator used to execute Transactions.
    """
    def __init__(self, tc_calc: TradingCostCalculator):
        self.tc_calc = tc_calc

    def get_trading_cost_per_qty(self, side: Side, tradable: Tradable):
        """
        Pre-computes the expected trading cost per quantity using the provided TradingCostCalculator.
        """
        return self.tc_calc.get_trading_cost_per_qty(side, tradable)

    @abstractmethod
    def buy(self, tradable: Tradable, qty: Decimal, limit_px: Optional[Decimal] = None) -> Transaction:
        """
        Executes a buy transaction, optionally specifying a limit price.
        """
        pass

    @abstractmethod
    def sell(self, tradable: Tradable, qty: Decimal, limit_px: Optional[Decimal] = None) -> Transaction:
        """
        Executes a sell transaction, optionally specifying a limit price.
        """
        pass


class DividendContext(ABC):
    """
    Plugin point for providing the data for dividend histories.
    """

    @abstractmethod
    def get_dividend(self, tradable: Tradable, payment_date: datetime.date) -> Optional[Dividend]:
        """
        Gets the dividend, if any, due to be paid on the given payment_date for the given financial instrument.
        """
        pass

    @abstractmethod
    def get_dividend_streams(self, tradables: List[Tradable], start_date: datetime.date,
                             end_date: datetime.date) -> pd.DataFrame:
        """
        Gets the dividend history for all the given instruments as a matrix, with the ticker ID of the tradable
        as columns and the dates as rows. If a given tuple of (ticker, date) does not have a dividend the value is NaN.
        """
        pass


class StrategyContext(ABC):
    """
    Base environment that any strategy type executes in.
    """

    @abstractmethod
    def get_start_time(self) -> datetime.datetime:
        """
        Gets the time the strategy run started, or the start range for the backtest.
        """
        pass

    @abstractmethod
    def get_end_time(self) -> Optional[datetime.datetime]:
        """
        Gets the ending time of the strategy run or backtest, or None if running in real-time mode.
        """
        pass

    @abstractmethod
    def get_configuration(self) -> dict:
        """
        Gets a configuration based on the TOML file provided to the strategy runner or backtester in the
        form of nested dictionaries.
        """
        pass


class Strategy(ABC):
    """
    Base abstraction for any strategy, whether a tick-by-tick strategy or close-on-close investment strategy.
    """

    @abstractmethod
    def init(self, ctx: StrategyContext):
        """
        Initialization method called to provide the strategy with its environment. Called exactly once.
        """
        pass


class RebalanceContext(ABC):
    """
    Context object injected into the rebalance function for an investment strategy which provides all the
    needful objects for executing a rebalance.
    """

    def __init__(self, portfolio: Portfolio, tradable_universe: TradableUniverse,
                 pricing_ctx: PricingContext, dividend_ctx: DividendContext,
                 trading_ctx: TradingContext):
        self.portfolio = portfolio
        self.tradable_universe = tradable_universe
        self.pricing_ctx = pricing_ctx
        self.dividend_ctx = dividend_ctx
        self.trading_ctx = trading_ctx

    @abstractmethod
    def get_rebalance_time(self) -> datetime.datetime:
        """
        Gets the time at which the rebalance is being executed. This time is determined by the RebalanceSchedule
        provided by the strategy, so it's not an arbitrary date & time.
        """
        pass

    def get_portfolio(self) -> Portfolio:
        """
        Gets the current state of the portfolio being managed by this strategy, or the initial portfolio image
        if it's the very first rebalance.
        """
        return self.portfolio

    def get_tradable_universe(self) -> TradableUniverse:
        """
        Gets the resolved universe of instruments that the strategy is allowed to trade.
        """
        return self.tradable_universe

    def get_pricing_ctx(self) -> PricingContext:
        """
        Gets the pricer provided by the strategy engine or backtester.
        """
        return self.pricing_ctx

    def get_dividend_ctx(self) -> DividendContext:
        """
        Gets the dividend database API provided by the strategy engine or backtester.
        """
        return self.dividend_ctx

    def get_trading_ctx(self) -> TradingContext:
        """
        Gets the exchange connectivity API or simulator provided by the strategy engine or backtester.
        """
        return self.trading_ctx


class MarketSchedule:
    """
    Real-time or historical calendar of times the market opens and closes. In the case of 24 hour exchanges like
    cryptocurrency or FX the Event objects given will never fire and the calendar will be empty.
    """

    def __init__(self, schedule_df: pd.DataFrame, market_open_event: Event, market_close_event: Event):
        self.schedule_df = schedule_df
        self.market_open_event = market_open_event
        self.market_close_event = market_close_event

    def get_schedule(self) -> pd.DataFrame:
        """
        A matrix of dates and market_open and market_close datetimes accounting for market holidays, if any.
        """
        return self.schedule_df

    def get_market_open_event(self) -> Event:
        """
        A Tau event that fires when the market opens.
        """
        return self.market_open_event

    def get_market_close_event(self) -> Event:
        """
        A Tau event that fires when the market closes.
        """
        return self.market_close_event


class MarketScheduleProvider:
    """
    Plugin point that wraps around the exchange calendar database.
    """

    @abstractmethod
    def get_market_schedule(self, market: str) -> MarketSchedule:
        """
        Gets the market schedule including callbacks for open & close times for the given market ID, e.g. NYSE.
        """
        pass


class RebalanceSchedule(ABC):
    """
    Policy object provided by the strategy which emits a callback when the strategy wants to rebalance. This can
    be as simple as a one-shot event for a buy and hold strategy or as complex as a calendar which rebalances
    daily except for the union of holidays applicable to the markets on which the TradableUniverse trades.
    """
    @abstractmethod
    def get_rebalance_event(self) -> Event:
        """
        A Tau event that fires every time a rebalance is desired.
        """
        pass


class InvestmentStrategy(Strategy):
    """
    A more sophisticated strategy oriented toward close-on-close backtesting and strategy execution.
    """

    @abstractmethod
    def get_initial_portfolio(self) -> Portfolio:
        """
        Gets the initial image of the portfolio -- normally used to provide a starting cash balance and to
        create the desired account structure in advance.
        """
        pass

    @abstractmethod
    def get_tradable_universe(self, base_universe: TradableUniverse):
        """
        Given a broader universe of known instruments supported by the strategy engine or backtester, return a proper
        subset of the universe containing just those instruments the strategy is allowed to trade.
        """
        pass

    @abstractmethod
    def get_rebalance_schedule(self, scheduler: NetworkScheduler, universe: TradableUniverse,
                               msp: MarketScheduleProvider) -> RebalanceSchedule:
        """
        Gets the strategy's policy for rebalancing, e.g. daily, monthly, quarterly, etc..
        """
        pass

    @abstractmethod
    def get_dividend_policy(self, trading_ctx: TradingContext, pricing_ctx: PricingContext) -> DividendPolicy:
        """
        Gets the strategy's policy for collecting or reinvesting dividends. Only applicable for strategies that
        are trading equity-type Tradables.
        """
        pass

    @abstractmethod
    def rebalance(self, rebalance_ctx: RebalanceContext):
        """
        Callback made for every tick of the RebalanceSchedule which rebalances the portfolio according to the strategy.
        This function represents the core trading logic of the strategy.
        """
        pass
