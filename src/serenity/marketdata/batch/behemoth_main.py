import datetime

import fire
import luigi

from serenity.marketdata.batch.cloud_upload import AzureBlobUploadTask


class BehemothDailyTask(luigi.WrapperTask):
    """
    Master task that coordinates the daily Behemoth tick database ETL jobs.
    """
    behemoth_path = luigi.Parameter()
    storage_account = luigi.Parameter()
    start_date = luigi.DateParameter(default=datetime.date.today())
    end_date = luigi.DateParameter(default=datetime.date.today())

    def requires(self):
        exchanges = {
            'PHEMEX': {'db_prefix': 'PHEMEX', 'supported_products': {'BTCUSD'}},
            'COINBASEPRO': {'db_prefix': 'COINBASE_PRO', 'supported_products': {'BTC-USD'}}
        }
        for exchange in exchanges.keys():
            db_prefix = exchanges[exchange]['db_prefix']
            supported_products = exchanges[exchange]['supported_products']
            for db in ['BOOKS', 'TRADES']:
                for product in supported_products:
                    yield AzureBlobUploadTask(behemoth_path=self.behemoth_path,
                                              storage_account=self.storage_account,
                                              db=f'{db_prefix}_{db}',
                                              product=product,
                                              start_date=self.start_date,
                                              end_date=self.end_date)


def run_luigi_task(behemoth_path: str = '/behemoth', storage_account: str = 'cloudwall', days_back: int = 1,
                   upload_start_date: str = None, upload_end_date: str = None, workers: int = 1):
    """
    Function called by Fire which takes care of processing command line arguments and invokes Luigi.
    """

    if upload_start_date is not None and upload_end_date is not None:
        upload_start_date = datetime.datetime.strptime(upload_start_date, '%Y-%m-%d').date()
        upload_end_date = datetime.datetime.strptime(upload_end_date, '%Y-%m-%d').date()
    else:
        upload_date = datetime.datetime.utcnow().date() - datetime.timedelta(days_back)
        upload_start_date = upload_date
        upload_end_date = upload_date

    task = BehemothDailyTask(behemoth_path=behemoth_path, storage_account=storage_account, start_date=upload_start_date,
                             end_date=upload_end_date)
    luigi.build([task], workers=workers, local_scheduler=True)


if __name__ == '__main__':
    fire.Fire(run_luigi_task)
