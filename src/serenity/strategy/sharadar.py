import datetime
from collections import defaultdict
from typing import List, Optional

import pandas as pd
from money import Money
from sqlalchemy.orm import Session

from serenity.data.sharadar_prices import EquityPrice
from serenity.data.sharadar_refdata import Ticker
from serenity.strategy.api import PricingContext, PriceField, Tradable, TradableUniverse, DividendContext, Dividend


class SharadarTradable(Tradable):
    def __init__(self, ticker: Ticker):
        self.ticker = ticker

    def get_ticker_id(self) -> int:
        return self.ticker.ticker_id

    def get_symbol(self) -> str:
        return self.ticker.ticker

    def get_name(self) -> str:
        return self.ticker.name

    def get_currency(self) -> str:
        return self.ticker.currency.currency_code

    def get_market(self) -> str:
        # Sharadar only has U.S. domestic stocks
        return 'NYSE'


class SharadarTradableUniverse(TradableUniverse):
    def __init__(self, session: Session):
        self.session = session

    def lookup(self, ticker_id: int) -> Tradable:
        result = self.session.query(Ticker).filter(Ticker.ticker_id == ticker_id).one()
        return SharadarTradable(result)

    def all(self) -> List[Tradable]:
        results = self.session.query(Ticker).all()
        return [SharadarTradable(result) for result in results]


class SharadarPricingContext(PricingContext):
    def __init__(self, session: Session):
        self.session = session

    def price(self, tradable: Tradable, price_date: datetime.date, price_field: PriceField) -> Money:
        result = self.session.query(EquityPrice)\
            .filter(EquityPrice.ticker_id == tradable.get_ticker_id(),
                    EquityPrice.date == price_date).one_or_none()
        if result is not None:
            return self._to_price(result, price_field)
        else:
            raise ValueError(f'Missing price for {tradable.get_ticker_id()} at {price_date}')

    def get_price_history(self, tradables: List[Tradable], start_date: datetime.date,
                          end_date: datetime.date, price_field: PriceField) -> pd.DataFrame:
        results = self.session.query(EquityPrice) \
            .filter(EquityPrice.ticker_id.in_([tradable.get_ticker_id() for tradable in tradables]),
                    EquityPrice.date >= start_date,
                    EquityPrice.date <= end_date).all()

        prices_by_date = defaultdict(dict)
        for result in results:
            prices_by_date[result.date][result.ticker_id] = \
                pd.to_numeric(self._to_price(result, price_field).amount)

        rows = [self._unpack_price_row(price_date, row) for price_date, row in prices_by_date.items()]
        df = pd.DataFrame(rows)
        if df.empty:
            raise KeyError('no data in price history')
        else:
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
        return df

    @staticmethod
    def _unpack_price_row(price_date: datetime.date, row: dict):
        unpacked = {
            'date': price_date
        }
        for ticker, px in row.items():
            unpacked[ticker] = px
        return unpacked

    @staticmethod
    def _to_price(result: EquityPrice, price_field: PriceField) -> Money:
        if price_field == PriceField.OPEN:
            return result.open_px
        elif price_field == PriceField.CLOSE:
            return result.close_px
        else:
            raise ValueError(f'Unsupported price_field: {price_field}')


class SharadarDividendContext(DividendContext):
    def __init__(self, session: Session):
        self.session = session

    def get_dividend(self, tradable: Tradable, payment_date: datetime.date) -> Optional[Dividend]:
        result = self.session.query(EquityPrice) \
            .filter(EquityPrice.ticker_id == tradable.get_ticker_id(),
                    EquityPrice.date == payment_date).one_or_none()
        if result is not None and result.dividends.amount > 0.0:
            return Dividend(tradable, payment_date, result.dividends)
        else:
            return None

    def get_dividend_streams(self, tradables: List[Tradable], start_date: datetime.date,
                             end_date: datetime.date) -> pd.DataFrame:
        results = self.session.query(EquityPrice) \
            .filter(EquityPrice.ticker_id.in_([tradable.get_ticker_id() for tradable in tradables]),
                    EquityPrice.date >= start_date,
                    EquityPrice.date <= end_date).all()

        divs_by_date = defaultdict(dict)
        for result in results:
            if result.dividends.amount > 0.0:
                divs_by_date[result.date][result.ticker_id] = \
                    pd.to_numeric(result.dividends.amount)

        rows = [self._unpack_dividend_row(price_date, row) for price_date, row in divs_by_date.items()]
        df = pd.DataFrame(rows)
        if df.empty:
            raise KeyError('no data in dividend history')
        else:
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
        return df

    @staticmethod
    def _unpack_dividend_row(price_date: datetime.date, row: dict):
        unpacked = {
            'date': price_date
        }
        for ticker, px in row.items():
            unpacked[ticker] = px
        return unpacked
