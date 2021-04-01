import datetime
import logging
from pathlib import Path

import luigi
from luigi.contrib.simulate import RunAnywayTarget

from serenity.marketdata.batch.local_splay import GenerateBehemothSplayFilesTask
from serenity.marketdata.tickstore.api import AzureBlobTickstore, BiTimestamp, LocalTickstore


class AzureBlobUploadTask(luigi.Task):
    logger = logging.getLogger('luigi-interface')

    behemoth_path = luigi.Parameter()
    storage_account = luigi.Parameter()
    db = luigi.Parameter()
    product = luigi.Parameter()
    connect_string = luigi.configuration.get_config().get('azure', 'connect_string', None)
    start_date = luigi.DateParameter(default=datetime.date.today())
    end_date = luigi.DateParameter(default=datetime.date.today())

    def requires(self):
        yield GenerateBehemothSplayFilesTask(behemoth_path=self.behemoth_path,
                                             db=self.db,
                                             product=self.product,
                                             start_date=self.start_date,
                                             end_date=self.end_date)

    def output(self):
        return RunAnywayTarget(self)

    def run(self):
        cloud_tickstore = AzureBlobTickstore(self.connect_string, str(self.db))
        local_tickstore = LocalTickstore(Path(Path(f'{str(self.behemoth_path)}/db/{str(self.db)}')), 'time')

        upload_start_date = datetime.datetime.strptime(str(self.start_date), '%Y-%m-%d').date()
        upload_end_date = datetime.datetime.strptime(str(self.end_date), '%Y-%m-%d').date()
        delta = upload_end_date - upload_start_date

        for i in range(delta.days + 1):
            upload_date = upload_start_date + datetime.timedelta(days=i)
            upload_date_start = datetime.datetime.combine(upload_date, datetime.datetime.min.time())
            upload_date_end = datetime.datetime.combine(upload_date, datetime.time(11, 59, 59))
            df = local_tickstore.select(str(self.product), upload_date_start, upload_date_end)

            cloud_tickstore.insert(str(self.product), BiTimestamp(upload_date), df)
            cloud_tickstore.close()
            self.logger.info(f'inserted {len(df)} {str(self.product)} records in cloud storage')

        # mark complete
        self.output().done()
