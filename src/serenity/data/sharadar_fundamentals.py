from datetime import datetime

from sqlalchemy import Column, Integer, Date, ForeignKey, String, DECIMAL
from sqlalchemy.orm import relationship, Session

from serenity.data.sharadar_api import Base, USD


class DimensionType(Base):
    __tablename__ = 'dimension_type'

    dimension_type_id = Column(Integer, primary_key=True)
    dimension_type_code = Column(String(16))

    @classmethod
    def find_by_code(cls, session: Session, dimension_type_code: str):
        return session.query(DimensionType).filter(DimensionType.dimension_type_code ==
                                                   dimension_type_code).one_or_none()

    @classmethod
    def get_or_create(cls, session: Session, dimension_type_code: str):
        dimension_type = DimensionType.find_by_code(session, dimension_type_code)
        if dimension_type is None:
            dimension_type = DimensionType(dimension_type_code=dimension_type_code)
            session.add(dimension_type)
        return dimension_type


class Fundamentals(Base):
    __tablename__ = 'fundamentals'

    fundamentals_id = Column(Integer, primary_key=True)
    ticker_code = Column(String(16), name='ticker')
    ticker_id = Column(Integer, ForeignKey('ticker.ticker_id'))
    ticker = relationship('serenity.equity.sharadar_refdata.Ticker', lazy='joined')
    dimension_type_id = Column(Integer, ForeignKey('dimension_type.dimension_type_id'))
    dimension_type = relationship('DimensionType')
    calendar_date = Column(Date)
    date_key = Column(Date)
    report_period = Column(Date)
    last_updated = Column(Date)
    accoci = Column(USD)
    assets = Column(USD)
    assets_avg = Column(USD)
    assets_c = Column(USD)
    assets_nc = Column(USD)
    asset_turnover = Column(DECIMAL)
    bvps = Column(USD)
    capex = Column(USD)
    cash_neq = Column(USD)
    cash_neq_usd = Column(USD)
    cor = Column(USD)
    consol_inc = Column(USD)
    current_ratio = Column(DECIMAL)
    de = Column(DECIMAL)
    debt = Column(USD)
    debt_c = Column(USD)
    debt_nc = Column(USD)
    debt_usd = Column(USD)
    deferred_rev = Column(USD)
    dep_amor = Column(USD)
    deposits = Column(USD)
    div_yield = Column(DECIMAL)
    dps = Column(USD)
    ebit = Column(USD)
    ebitda = Column(USD)
    ebitda_margin = Column(DECIMAL)
    ebitda_usd = Column(USD)
    ebit_usd = Column(USD)
    ebt = Column(USD)
    eps = Column(USD)
    eps_dil = Column(USD)
    eps_usd = Column(USD)
    equity = Column(USD)
    equity_avg = Column(USD)
    equity_usd = Column(USD)
    ev = Column(USD)
    ev_ebit = Column(DECIMAL)
    ev_ebitda = Column(DECIMAL)
    fcf = Column(USD)
    fcf_ps = Column(USD)
    fx_usd = Column(USD)
    gp = Column(USD)
    gross_margin = Column(DECIMAL)
    int_exp = Column(USD)
    inv_cap = Column(USD)
    inv_cap_avg = Column(USD)
    inventory = Column(USD)
    investments = Column(USD)
    investments_c = Column(USD)
    investments_nc = Column(USD)
    liabilities = Column(USD)
    liabilities_c = Column(USD)
    liabilities_nc = Column(USD)
    market_cap = Column(USD)
    ncf = Column(USD)
    ncf_bus = Column(USD)
    ncf_common = Column(USD)
    ncf_debt = Column(USD)
    ncf_div = Column(USD)
    ncf_f = Column(USD)
    ncf_i = Column(USD)
    ncf_inv = Column(USD)
    ncf_o = Column(USD)
    ncf_x = Column(USD)
    net_inc = Column(USD)
    net_inc_cmn = Column(USD)
    net_inc_cmn_usd = Column(USD)
    net_inc_dis = Column(USD)
    net_inc_nci = Column(USD)
    net_margin = Column(DECIMAL)
    op_ex = Column(USD)
    op_inc = Column(USD)
    payables = Column(USD)
    payout_ratio = Column(DECIMAL)
    pb = Column(DECIMAL)
    pe = Column(DECIMAL)
    pe1 = Column(DECIMAL)
    ppne_net = Column(USD)
    pref_div_is = Column(USD)
    price = Column(USD)
    ps = Column(DECIMAL)
    ps1 = Column(DECIMAL)
    receivables = Column(USD)
    ret_earn = Column(USD)
    revenue = Column(USD)
    revenue_usd = Column(USD)
    rnd = Column(USD)
    roa = Column(DECIMAL)
    roe = Column(DECIMAL)
    roic = Column(DECIMAL)
    ros = Column(DECIMAL)
    sb_comp = Column(USD)
    sgna = Column(USD)
    share_factor = Column(DECIMAL)
    shares_bas = Column(Integer)
    shares_wa = Column(Integer)
    shares_wa_dil = Column(Integer)
    sps = Column(USD)
    tangibles = Column(USD)
    tax_assets = Column(USD)
    tax_exp = Column(USD)
    tax_liabilities = Column(USD)
    tbvps = Column(USD)
    working_capital = Column(USD)

    @classmethod
    def find(cls, session: Session, ticker: str, dimension_type: DimensionType, date_key: datetime.date,
             report_period: datetime.date):
        return session.query(Fundamentals).join(DimensionType) \
            .filter(Fundamentals.ticker_code == ticker,
                    DimensionType.dimension_type_code == dimension_type.dimension_type_code,
                    Fundamentals.report_period == report_period,
                    Fundamentals.date_key == date_key).one_or_none()
