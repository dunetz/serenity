from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import Session, relationship

from serenity.data.sharadar_api import Base, USD
from serenity.data.sharadar_refdata import Ticker


class SecurityType(Base):
    __tablename__ = 'security_type'

    security_type_id = Column(Integer, primary_key=True)
    security_type_code = Column(String(8))

    @classmethod
    def find_by_code(cls, session: Session, security_type_code: str):
        return session.query(SecurityType).filter(SecurityType.security_type_code == security_type_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, security_type_code: str):
        if security_type_code is None:
            return None
        else:
            entity = SecurityType.find_by_code(session, security_type_code)
            if entity is None:
                entity = SecurityType(security_type_code=security_type_code)
                session.add(entity)
            return entity


class InstitutionalInvestor(Base):
    __tablename__ = 'institutional_investor'

    institutional_investor_id = Column(Integer, primary_key=True)
    institutional_investor_name = Column(String(128))

    @classmethod
    def find_by_name(cls, session: Session, institutional_investor_name: str):
        return session.query(InstitutionalInvestor).filter(InstitutionalInvestor.institutional_investor_name ==
                                                           institutional_investor_name).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, institutional_investor_name: str):
        if institutional_investor_name is None:
            return None
        else:
            entity = InstitutionalInvestor.find_by_name(session, institutional_investor_name)
            if entity is None:
                entity = InstitutionalInvestor(institutional_investor_name=institutional_investor_name)
                session.add(entity)
            return entity


class TransactionType(Base):
    __tablename__ = 'transaction_type'

    transaction_type_id = Column(Integer, primary_key=True)
    transaction_type_code = Column(String(8))

    @classmethod
    def find_by_code(cls, session: Session, transaction_type_code: str):
        return session.query(TransactionType).filter(TransactionType.transaction_type_code ==
                                                     transaction_type_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, transaction_type_code: str):
        if transaction_type_code is None:
            return None
        else:
            entity = TransactionType.find_by_code(session, transaction_type_code)
            if entity is None:
                entity = TransactionType(transaction_type_code=transaction_type_code)
                session.add(entity)
            return entity


class SecurityAdType(Base):
    __tablename__ = 'security_ad_type'

    security_ad_type_id = Column(Integer, primary_key=True)
    security_ad_type_code = Column(String(8))

    @classmethod
    def find_by_code(cls, session: Session, security_ad_type_code: str):
        return session.query(SecurityAdType).filter(SecurityAdType.security_ad_type_code ==
                                                    security_ad_type_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, security_ad_type_code: str):
        if security_ad_type_code is None:
            return None
        else:
            entity = SecurityAdType.find_by_code(session, security_ad_type_code)
            if entity is None:
                entity = SecurityAdType(security_ad_type_code=security_ad_type_code)
                session.add(entity)
            return entity


class FormType(Base):
    __tablename__ = 'form_type'

    form_type_id = Column(Integer, primary_key=True)
    form_type_code = Column(String(8))

    @classmethod
    def find_by_code(cls, session: Session, form_type_code: str):
        return session.query(FormType).filter(FormType.form_type_code == form_type_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, form_type_code: str):
        if form_type_code is None:
            return None
        else:
            entity = FormType.find_by_code(session, form_type_code)
            if entity is None:
                entity = FormType(form_type_code=form_type_code)
                session.add(entity)
            return entity


class SecurityTitleType(Base):
    __tablename__ = 'security_title_type'

    security_title_type_id = Column(Integer, primary_key=True)
    security_title_type_code = Column(String(32))

    @classmethod
    def find_by_code(cls, session: Session, security_title_type_code: str):
        return session.query(SecurityTitleType).filter(SecurityTitleType.security_title_type_code ==
                                                       security_title_type_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, security_title_type_code: str):
        if security_title_type_code is None:
            return None
        else:
            entity = SecurityTitleType.find_by_code(session, security_title_type_code)
            if entity is None:
                entity = SecurityTitleType(security_title_type_code=security_title_type_code)
                session.add(entity)
            return entity


class InstitutionalHoldings(Base):
    __tablename__ = 'institutional_holdings'

    institutional_holdings_id = Column(Integer, primary_key=True)
    ticker_code = Column(String(16), name='ticker')
    ticker_id = Column(Integer, ForeignKey('ticker.ticker_id'))
    ticker = relationship('serenity.equity.sharadar_refdata.Ticker', lazy='joined')
    institutional_investor_id = Column(Integer, ForeignKey('institutional_investor.institutional_investor_id'))
    investor = relationship('InstitutionalInvestor', lazy='joined')
    security_type_id = Column(Integer, ForeignKey('security_type.security_type_id'))
    security_type = relationship('SecurityType', lazy='joined')
    calendar_date = Column(Date)
    value = Column(USD)
    units = Column(Integer)
    price = Column(USD)

    @classmethod
    def find(cls, session: Session, ticker: Ticker, investor: InstitutionalInvestor,
             security_type: SecurityType, calendar_date: datetime.date):
        return session.query(InstitutionalHoldings).join(InstitutionalInvestor).join(SecurityType) \
                .filter(InstitutionalHoldings.ticker_code == ticker,
                        InstitutionalInvestor.institutional_investor_name == investor.institutional_investor_name,
                        SecurityType.security_type_code == security_type.security_type_code,
                        InstitutionalHoldings.calendar_date == calendar_date).one_or_none()


class InsiderHoldings(Base):
    __tablename__ = 'insider_holdings'

    insider_holdings_id = Column(Integer, primary_key=True)
    ticker_code = Column(String(16), name='ticker')
    ticker_id = Column(Integer, ForeignKey('ticker.ticker_id'))
    ticker = relationship('serenity.equity.sharadar_refdata.Ticker', lazy='joined')
    filing_date = Column(Date)
    form_type_id = Column(Integer, ForeignKey('form_type.form_type_id'))
    form_type = relationship('FormType', lazy='joined')
    issuer_name = Column(String(128))
    owner_name = Column(String(64))
    officer_title = Column(String(64))
    is_director = Column(Boolean)
    is_officer = Column(Boolean)
    is_ten_percent_owner = Column(Boolean)
    transaction_date = Column(Date)
    security_ad_type_id = Column(Integer, ForeignKey('security_ad_type.security_ad_type_id'))
    security_ad_type = relationship('SecurityAdType', lazy='joined')
    transaction_type_id = Column(Integer, ForeignKey('transaction_type.transaction_type_id'))
    transaction_type = relationship('TransactionType', lazy='joined')
    shares_owned_before_transaction = Column(Integer)
    transaction_shares = Column(Integer)
    shares_owned_following_transaction = Column(Integer)
    transaction_price_per_share = Column(USD)
    transaction_value = Column(USD)
    security_title_type_id = Column(Integer, ForeignKey('security_title_type.security_title_type_id'))
    security_title_type = relationship('SecurityTitleType', lazy='joined')
    direct_or_indirect = Column(String(1))
    nature_of_ownership = Column(String(128))
    date_exercisable = Column(Date)
    price_exercisable = Column(USD)
    expiration_date = Column(Date)
    row_num = Column(Integer)

    @classmethod
    def find(cls, session: Session, ticker: str, filing_date: datetime.date, owner_name: str,
             form_type: FormType, row_num: int):
        return session.query(InsiderHoldings).join(FormType) \
                .filter(InsiderHoldings.ticker_code == ticker,
                        InsiderHoldings.filing_date == filing_date,
                        InsiderHoldings.owner_name == owner_name,
                        FormType.form_type_code == form_type.form_type_code,
                        InsiderHoldings.row_num == row_num).one_or_none()
