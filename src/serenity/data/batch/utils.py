import datetime
import hashlib
import logging
from abc import ABC, abstractmethod


import luigi
import pandas as pd
import quandl
from luigi import Target, LocalTarget
from sqlalchemy.orm import Session

from serenity.data.sharadar_api import create_sharadar_session, BatchStatus


class ExportQuandlTableTask(luigi.Task):
    logger = logging.getLogger('luigi-interface')

    table_name = luigi.Parameter()
    date_column = luigi.Parameter(default='')
    start_date = luigi.DateParameter(default=None)
    end_date = luigi.DateParameter(default=None)
    api_key = luigi.configuration.get_config().get('quandl', 'api_key', None)
    data_dir = luigi.configuration.get_config().get('storage', 'storage_root', None)

    def output(self):
        if self.start_date is None and self.end_date is None:
            return luigi.LocalTarget(f'{self.data_dir}/{str(self.table_name).replace("/", "-")}_quandl_data.zip')
        else:
            end_date_txt = str(self.end_date)
            if self.end_date is None:
                end_date_txt = 'LATEST'
            date_range = f'{self.start_date}-{end_date_txt}'
            return luigi.LocalTarget(f'{self.data_dir}/{str(self.table_name).replace("/", "-")}_'
                                     f'{date_range}_quandl_data.zip')

    def run(self):
        quandl.ApiConfig.api_key = str(self.api_key)
        with self.output().temporary_path() as path:
            self.logger.info(f'downloading {self.table_name} to {path}')
            if self.date_column == '':
                kwargs = {
                    'filename': path
                }
            else:
                kwargs = {
                    'filename': path,
                    str(self.date_column): {'gte': self.start_date, 'lte': self.end_date}
                }
            quandl.export_table(str(self.table_name), **kwargs)


class BatchStatusTarget(Target):
    def __init__(self, session: Session, workflow_name: str, start_date: datetime.date, end_date: datetime.date,
                 local_file: LocalTarget):
        self.session = session
        self.workflow_name = workflow_name
        self.start_date = start_date
        self.end_date = end_date
        self.local_file = local_file

    def exists(self):
        if not self.local_file.exists():
            return False

        md5_checksum = hashlib.md5(open(self.local_file.path, 'rb').read()).hexdigest()
        batch_status = BatchStatus.find(self.session, self.workflow_name, self.start_date, self.end_date)
        if batch_status is None:
            batch_status = BatchStatus(workflow_name=self.workflow_name,
                                       start_date=self.start_date,
                                       end_date=self.end_date,
                                       md5_checksum=md5_checksum,
                                       is_pending=True)
            self.session.add(batch_status)
            exists = False
        else:
            exists = (not batch_status.is_pending) and (batch_status.md5_checksum == md5_checksum)
            if batch_status.md5_checksum != md5_checksum:
                batch_status.md5_checksum = md5_checksum
                self.session.add(batch_status)
        return exists

    def done(self):
        batch_status = BatchStatus.find(self.session, self.workflow_name, self.start_date, self.end_date)
        if batch_status is not None and batch_status.is_pending:
            batch_status.is_pending = False
            self.session.add(batch_status)
        elif batch_status is None:
            md5_checksum = hashlib.md5(open(self.local_file.path, 'rb').read()).hexdigest()
            batch_status = BatchStatus(workflow_name=self.workflow_name,
                                       start_date=self.start_date,
                                       end_date=self.end_date,
                                       md5_checksum=md5_checksum,
                                       is_pending=False)
            self.session.add(batch_status)
        self.session.commit()


class LoadSharadarTableTask(ABC, luigi.Task):
    logger = logging.getLogger('luigi-interface')
    session = create_sharadar_session()

    start_date = luigi.DateParameter(default=datetime.date.today())
    end_date = luigi.DateParameter(default=datetime.date.today())

    def run(self):
        input_value = self.input()
        input_value = [input_value] if type(input_value) is LocalTarget else input_value
        for table_in in input_value:
            if isinstance(table_in, LocalTarget):
                in_file = table_in.path
                df = pd.read_csv(in_file)
                self.logger.info(f'loaded {len(df)} rows of CSV data from {in_file}')

                row_count = 0
                for index, row in df.iterrows():
                    self.process_row(index, row)
                    if row_count > 0 and row_count % 1000 == 0:
                        self.logger.info(f'{row_count} rows loaded; flushing next 1000 rows to database')
                        self.session.commit()
                    row_count += 1

                self.session.commit()

        self.output().done()

    def output(self):
        target = None
        input_value = self.input()
        input_value = [input_value] if type(input_value) is LocalTarget else input_value
        for table_in in input_value:
            if isinstance(table_in, LocalTarget):
                # noinspection PyTypeChecker
                target = BatchStatusTarget(self.session, self.get_workflow_name(),
                                           self.start_date, self.end_date, table_in)

        return target

    @abstractmethod
    def process_row(self, index, row):
        pass

    @abstractmethod
    def get_workflow_name(self):
        pass
