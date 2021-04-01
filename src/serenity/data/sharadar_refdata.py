from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DECIMAL
from sqlalchemy.orm import relationship, Session

from serenity.data.sharadar_api import Base


class UnitType(Base):
    __tablename__ = 'unit_type'

    unit_type_id = Column(Integer, primary_key=True)
    unit_type_code = Column(String(32))

    def __init__(self, unit_type_code: str):
        self.unit_type_code = unit_type_code

    @classmethod
    def find_by_code(cls, session: Session, unit_type_code: str):
        return session.query(UnitType).filter(UnitType.unit_type_code == unit_type_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, unit_type_code: str):
        unit_type = UnitType.find_by_code(session, unit_type_code)
        if unit_type is None:
            unit_type = UnitType(unit_type_code)
            session.add(unit_type)
        return unit_type


class Indicator(Base):
    __tablename__ = 'indicators'

    indicator_id = Column(Integer, primary_key=True)
    table_name = Column(String(32))
    indicator = Column(String(32))
    is_filter = Column(Boolean)
    is_primary_key = Column(Boolean)
    title = Column(String(256))
    description = Column(String(2048))
    unit_type_id = Column(Integer, ForeignKey('unit_type.unit_type_id'))
    unit_type = relationship('UnitType', lazy='joined')

    @classmethod
    def find_by_name(cls, session: Session, table_name: str, indicator: str):
        return session.query(Indicator).filter(Indicator.table_name == table_name,
                                               Indicator.indicator == indicator).one_or_none()


class Exchange(Base):
    __tablename__ = 'exchange'

    exchange_id = Column(Integer, primary_key=True)
    exchange_code = Column(String(32))

    @classmethod
    def find_by_code(cls, session: Session, exchange_code: str):
        return session.query(Exchange).filter(Exchange.exchange_code == exchange_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, exchange_code: str):
        if exchange_code is None:
            return None
        else:
            exchange = Exchange.find_by_code(session, exchange_code)
            if exchange is None:
                exchange = Exchange(exchange_code=exchange_code)
                session.add(exchange)
            return exchange


class TickerCategory(Base):
    __tablename__ = 'ticker_category'

    ticker_category_id = Column(Integer, primary_key=True)
    ticker_category_code = Column(String(32))

    @classmethod
    def find_by_code(cls, session: Session, ticker_category_code: str):
        return session.query(TickerCategory).filter(TickerCategory.ticker_category_code
                                                    == ticker_category_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, ticker_category_code: str):
        if ticker_category_code is None:
            return None
        else:
            category = TickerCategory.find_by_code(session, ticker_category_code)
            if category is None:
                category = TickerCategory(ticker_category_code=ticker_category_code)
                session.add(category)
            return category


class SectorCodeType(Base):
    __tablename__ = 'sector_code_type'

    sector_code_type_id = Column(Integer, primary_key=True)
    sector_code_type_code = Column(String(32))

    @classmethod
    def find_by_code(cls, session: Session, sector_code_type_code: str):
        return session.query(SectorCodeType).filter(SectorCodeType.sector_code_type_code ==
                                                    sector_code_type_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, sector_code_type_code: str):
        if sector_code_type_code is None:
            return None
        else:
            sector_code_type = SectorCodeType.find_by_code(session, sector_code_type_code)
            if sector_code_type is None:
                sector_code_type = SectorCodeType(sector_code_type_code=sector_code_type_code)
                session.add(sector_code_type)
            return sector_code_type


class Sector(Base):
    __tablename__ = 'sector_map'

    sector_map_id = Column(Integer, primary_key=True)
    sector_code_type_id = Column(Integer, ForeignKey('sector_code_type.sector_code_type_id'))
    sector_code_type = relationship('SectorCodeType')
    sector_code = Column(Integer)
    sector = Column(String(64))
    industry = Column(String(64))

    @classmethod
    def find_by_sector_industry_and_type(cls, session: Session, sector_code_type: SectorCodeType, sector: str,
                                         industry: str):
        return session.query(Sector).filter(Sector.sector == sector, Sector.industry == industry,
                                            Sector.sector_code_type_id ==
                                            sector_code_type.sector_code_type_id).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, sector_code_type_code: str, sector_code: Optional[int], sector: str,
                      industry: str):
        if sector is None and industry is None:
            return None

        sector_code_type = SectorCodeType.get_or_create(session, sector_code_type_code)
        sector_entity = Sector.find_by_sector_industry_and_type(session, sector_code_type, sector, industry)
        if sector_entity is None:
            sector_entity = Sector(sector_code_type=sector_code_type, sector_code=sector_code, sector=sector,
                                   industry=industry)
            session.add(sector_entity)
        return sector_entity


class Scale(Base):
    __tablename__ = 'scale'

    scale_id = Column(Integer, primary_key=True)
    scale_code = Column(String(32))

    @classmethod
    def find_by_code(cls, session: Session, scale_code: str):
        return session.query(Scale).filter(Scale.scale_code == scale_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, scale_code: str):
        if scale_code is None:
            return None
        else:
            scale = Scale.find_by_code(session, scale_code)
            if scale is None:
                scale = Scale(scale_code=scale_code)
                session.add(scale)
            return scale


class Currency(Base):
    __tablename__ = 'currency'

    currency_id = Column(Integer, primary_key=True)
    currency_code = Column(String(8))

    @classmethod
    def find_by_code(cls, session: Session, currency_code: str):
        return session.query(Currency).filter(Currency.currency_code == currency_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, currency_code: str):
        if currency_code is None:
            return None
        else:
            ccy = Currency.find_by_code(session, currency_code)
            if ccy is None:
                ccy = Currency(currency_code=currency_code)
                session.add(ccy)
            return ccy


class Ticker(Base):
    __tablename__ = 'ticker'

    ticker_id = Column(Integer, primary_key=True)
    table_name = Column(String(32))
    perma_ticker_id = Column(Integer)
    ticker = Column(String(16))
    name = Column(String(256))
    exchange_id = Column(Integer, ForeignKey('exchange.exchange_id'))
    exchange = relationship('Exchange', lazy='joined')
    is_delisted = Column(Boolean)
    ticker_category_id = Column(Integer, ForeignKey('ticker_category.ticker_category_id'))
    ticker_category = relationship('TickerCategory', lazy='joined')
    cusips = Column(String(256))
    sic_sector_id = Column(Integer, ForeignKey('sector_map.sector_map_id'))
    sic_sector = relationship('Sector', foreign_keys=sic_sector_id, lazy='joined')
    fama_sector_id = Column(Integer, ForeignKey('sector_map.sector_map_id'))
    fama_sector = relationship('Sector', foreign_keys=fama_sector_id, lazy='joined')
    sector_id = Column(Integer, ForeignKey('sector_map.sector_map_id'))
    sector = relationship('Sector', foreign_keys=sector_id, lazy='joined')
    market_cap_scale_id = Column(Integer, ForeignKey('scale.scale_id'))
    market_cap_scale = relationship('Scale', foreign_keys=market_cap_scale_id, lazy='joined')
    revenue_scale_id = Column(Integer, ForeignKey('scale.scale_id'))
    revenue_scale = relationship('Scale', foreign_keys=revenue_scale_id, lazy='joined')
    related_tickers = Column(String(256))
    currency_id = Column(Integer, ForeignKey('currency.currency_id'))
    currency = relationship('Currency', lazy='joined')
    location = Column(String(64))
    last_updated = Column(Date)
    first_added = Column(Date)
    first_price_date = Column(Date)
    last_price_date = Column(Date)
    first_quarter = Column(Date)
    last_quarter = Column(Date)
    secfilings = Column(String(256))
    company_site = Column(String(256))

    @classmethod
    def find_by_perma_id(cls, session: Session, perma_ticker_id: int):
        return session.query(Ticker).filter(Ticker.perma_ticker_id == perma_ticker_id).one_or_none()

    @classmethod
    def find_by_ticker(cls, session: Session, ticker: str):
        if ticker is None:
            return None
        return session.query(Ticker).filter(Ticker.ticker == ticker).one_or_none()


class EventCode(Base):
    __tablename__ = 'event_code'

    event_code_id = Column(Integer, primary_key=True)
    event_code = Column(Integer)
    event_description = Column(String(256))

    @classmethod
    def find_by_code(cls, session: Session, event_code: int):
        return session.query(EventCode).filter(EventCode.event_code == event_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, event_code: int, event_description: str):
        if event_code is None:
            return None
        else:
            ccy = EventCode.find_by_code(session, event_code)
            if ccy is None:
                ccy = EventCode(event_code=event_code, event_description=event_description)
                session.add(ccy)
            return ccy


class Event(Base):
    __tablename__ = 'event'

    event_id = Column(Integer, primary_key=True)
    ticker_code = Column(String(16), name='ticker')
    ticker_id = Column(Integer, ForeignKey('ticker.ticker_id'))
    ticker = relationship('Ticker', lazy='joined')
    event_date = Column(Date)
    event_code_id = Column(Integer, ForeignKey('event_code.event_code_id'))
    event_code = relationship('EventCode', lazy='joined')

    @classmethod
    def find(cls, session: Session, ticker: str, event_date: datetime.date, event_code: int):
        return session.query(Event).join(EventCode).filter(Event.ticker_code == ticker,
                                                           Event.event_date == event_date,
                                                           EventCode.event_code == event_code)\
            .one_or_none()


class CorporateActionType(Base):
    __tablename__ = 'corp_action_type'

    corp_action_type_id = Column(Integer, primary_key=True)
    corp_action_type_code = Column(String(8))

    @classmethod
    def find_by_code(cls, session: Session, corp_action_type_code: str):
        return session.query(CorporateActionType)\
            .filter(CorporateActionType.corp_action_type_code == corp_action_type_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, corp_action_type_code: str):
        if corp_action_type_code is None:
            return None
        else:
            ccy = CorporateActionType.find_by_code(session, corp_action_type_code)
            if ccy is None:
                ccy = CorporateActionType(corp_action_type_code=corp_action_type_code)
                session.add(ccy)
            return ccy


class CorporateAction(Base):
    __tablename__ = 'corp_action'

    corp_action_id = Column(Integer, primary_key=True)
    corp_action_date = Column(Date)
    ticker_code = Column(String(16), name='ticker')
    ticker_id = Column(Integer, ForeignKey('ticker.ticker_id'))
    ticker = relationship('Ticker', lazy='joined')
    corp_action_type_id = Column(Integer, ForeignKey('corp_action_type.corp_action_type_id'))
    corp_action_type = relationship('CorporateActionType', lazy='joined')
    name = Column(String(128))
    value = Column(DECIMAL)
    contra_ticker = Column(String(16))
    contra_name = Column(String(128))

    @classmethod
    def find(cls, session: Session, ticker: str, corp_action_date: datetime.date, corp_action_type_code: str):
        return session.query(CorporateAction).join(CorporateActionType)\
            .filter(CorporateAction.ticker_code == ticker,
                    CorporateAction.corp_action_date == corp_action_date,
                    CorporateActionType.corp_action_type_code == corp_action_type_code).one_or_none()


def get_indicator_details(session: Session, table_name: str, indicator: str):
    """
    Helper method that gets the description & units for a table column or other metadata given (pseudo) table name
    and the column name / type code.
    """
    return session.query(Indicator).filter(Indicator.table_name == table_name,
                                           Indicator.indicator == indicator).one_or_none()
