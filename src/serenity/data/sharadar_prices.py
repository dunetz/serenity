from datetime import datetime

import pandas as pd

from sqlalchemy import Column, Integer, Date, ForeignKey, String
from sqlalchemy.orm import relationship, Session

from serenity.data.sharadar_api import Base, USD


class EquityPrice(Base):
    __tablename__ = 'equity_price'

    equity_price_id = Column(Integer, primary_key=True)
    ticker_code = Column(String(16), name='ticker')
    ticker_id = Column(Integer, ForeignKey('ticker.ticker_id'))
    ticker = relationship('serenity.equity.sharadar_refdata.Ticker', lazy='joined')
    date = Column(Date, name='price_date')
    open_px = Column(USD, name='open')
    high_px = Column(USD, name='high')
    low_px = Column(USD, name='low')
    close_px = Column(USD, name='close')
    volume = Column(Integer)
    dividends = Column(USD)
    close_unadj = Column(USD)
    last_updated = Column(Date)

    @classmethod
    def find(cls, session: Session, ticker: str, price_date: datetime.date):
        return session.query(EquityPrice) \
            .filter(EquityPrice.ticker_code == ticker,
                    EquityPrice.date == price_date).one_or_none()


def get_equity_prices(session: Session, ticker: str) -> pd.DataFrame:
    results = session.query(EquityPrice) \
        .filter(EquityPrice.ticker_code == ticker).all()
    df = pd.DataFrame([{
        'date': result.date,
        'open': pd.to_numeric(result.open_px.amount),
        'high': pd.to_numeric(result.high_px.amount),
        'low': pd.to_numeric(result.low_px.amount),
        'close': pd.to_numeric(result.close_px.amount),
        'volume': result.volume
    } for result in results])
    if df.empty:
        raise KeyError(f'no data for ticker: {ticker}')
    else:
        df.set_index('date', inplace=True)
    return df
