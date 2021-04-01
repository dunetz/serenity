import os
from datetime import datetime

import pandas as pd
import quandl

from money import Money

from sqlalchemy import create_engine, TypeDecorator, Column, Integer, String, Date, Boolean
from sqlalchemy.dialects.postgresql import MONEY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


def create_sharadar_session(hostname: str = os.getenv('TIMESCALEDB_NODEPORT_SERVICE_HOST', 'localhost'),
                            port: int = os.getenv('TIMESCALEDB_NODEPORT_SERVICE_PORT', '5432'),
                            username: str = os.getenv('POSTGRES_SHARADAR_USER', 'sharadar'),
                            password: str = os.getenv('POSTGRES_SHARADAR_PASSWORD', None)) -> Session:
    engine = create_engine(f'postgresql://{username}:{password}@{hostname}:{port}/')
    session = sessionmaker(bind=engine)
    return session()


def init_quandl(quandl_api_key: str = os.getenv('QUANDL_API_KEY')):
    quandl.ApiConfig.api_key = quandl_api_key


def clean_nulls(value):
    if pd.isnull(value):
        return None
    else:
        return value


def yes_no_to_bool(yes_no: str) -> bool:
    return yes_no == 'Y'


class USD(TypeDecorator):
    impl = MONEY

    @property
    def python_type(self):
        raise Money

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(MONEY())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        else:
            return str(value)

    def process_literal_param(self, value, dialect):
        raise NotImplementedError()

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return Money(value.replace(',', '').replace('$', ''), 'USD')


class BatchStatus(Base):
    __tablename__ = 'batch_status'

    batch_status_id = Column(Integer, primary_key=True)
    workflow_name = Column(String(64))
    start_date = Column(Date)
    end_date = Column(Date)
    md5_checksum = Column(String(32))
    is_pending = Column(Boolean)

    @classmethod
    def find(cls, session: Session, workflow_name: str, start_date: datetime.date, end_date: datetime.date):
        return session.query(BatchStatus).filter(
            BatchStatus.workflow_name == workflow_name,
            BatchStatus.start_date == start_date,
            BatchStatus.end_date == end_date
        ).one_or_none()
