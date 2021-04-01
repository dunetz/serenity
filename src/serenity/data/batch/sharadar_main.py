import datetime

import fire
import luigi

from serenity.data.batch.load_sharadar_corp_actions import LoadCorporateActionsTask
from serenity.data.batch.load_sharadar_event_calendar import LoadEventCalendarTask
from serenity.data.batch.load_sharadar_fundamentals import LoadEquityFundamentalsTask
from serenity.data.batch.load_sharadar_insider_holdings import LoadInsiderHoldingsTask
from serenity.data.batch.load_sharadar_institutional_holdings import LoadInstitutionalHoldingsTask
from serenity.data.batch.load_sharadar_meta import LoadSharadarMetaTask
from serenity.data.batch.load_sharadar_prices import LoadEquityPricesTask


class SharadarDownloadTask(luigi.WrapperTask):
    start_date = luigi.DateParameter(default=datetime.date.today())
    end_date = luigi.DateParameter(default=datetime.date.today())

    def requires(self):
        yield LoadSharadarMetaTask()
        yield LoadCorporateActionsTask(start_date=self.start_date, end_date=self.end_date)
        yield LoadEventCalendarTask(start_date=self.start_date, end_date=self.end_date)
        yield LoadEquityPricesTask(start_date=self.start_date, end_date=self.end_date)
        yield LoadEquityFundamentalsTask(start_date=self.start_date, end_date=self.end_date)
        yield LoadInsiderHoldingsTask(start_date=self.start_date, end_date=self.end_date)
        yield LoadInstitutionalHoldingsTask(start_date=self.start_date, end_date=self.end_date)


def run_luigi_task(mode: str, workers: int = 1):
    if mode == 'BACKFILL':
        task = SharadarDownloadTask(start_date=None, end_date=None)
    elif mode == 'DAILY':
        task = SharadarDownloadTask()
    else:
        raise ValueError(f'unknown mode: {mode}')

    luigi.build([task], workers=workers, local_scheduler=True)


if __name__ == '__main__':
    fire.Fire(run_luigi_task)
