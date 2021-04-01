import datetime
import logging
from pathlib import Path

import luigi
import pandas as pd

from luigi.contrib.simulate import RunAnywayTarget

from serenity.marketdata.tickstore.api import BiTimestamp, LocalTickstore
from serenity.marketdata.tickstore.journal import Journal


class GenerateBehemothSplayFilesTask(luigi.Task):
    logger = logging.getLogger('luigi-interface')

    behemoth_path = luigi.Parameter()
    db = luigi.Parameter()
    product = luigi.Parameter()
    start_date = luigi.DateParameter(default=datetime.date.today())
    end_date = luigi.DateParameter(default=datetime.date.today())

    def output(self):
        return RunAnywayTarget(self)

    def run(self):
        # this is a bit perverse, but Luigi's magic conversion of DateParameter to datetime.date under
        # the covers confuses the heck out of PyCharm
        upload_start_date = datetime.datetime.strptime(str(self.start_date), '%Y-%m-%d').date()
        upload_end_date = datetime.datetime.strptime(str(self.end_date), '%Y-%m-%d').date()
        delta = upload_end_date - upload_start_date

        for i in range(delta.days + 1):
            upload_date = upload_start_date + datetime.timedelta(days=i)

            # this is not very pretty, but the journal format differs by database type and so
            # we need to look at the database name to figure out which one to use
            if str(self.db).endswith('_BOOKS'):
                self.__splay_books_db(upload_date)
            elif str(self.db).endswith('_TRADES'):
                self.__splay_trades_db(upload_date)
            else:
                raise ValueError(f'Unsupported database type: {str(self.db)}')

        # mark as complete
        self.output().done()

    def __splay_books_db(self, upload_date: datetime.date):
        books_db = str(self.db)
        books_path = Path(f'{str(self.behemoth_path)}/journals/{books_db}/{str(self.product)}')
        books_journal = Journal(books_path)
        reader = books_journal.create_reader(upload_date)

        length = reader.get_length()
        records = []
        while reader.get_pos() < length:
            time = reader.read_double()

            best_bid_qty = reader.read_long()
            best_bid_px = reader.read_double()
            best_ask_qty = reader.read_long()
            best_ask_px = reader.read_double()

            record = {
                'time': datetime.datetime.fromtimestamp(time),
                'best_bid_qty': best_bid_qty,
                'best_bid_px': best_bid_px,
                'best_ask_qty': best_ask_qty,
                'best_ask_px': best_ask_px
            }
            records.append(record)

        if len(records) > 0:
            self.logger.info(
                f'uploading journaled {str(self.db)}/{str(self.product)} books to Behemoth for UTC date '
                f'{str(upload_date)}')
            df = pd.DataFrame(records)
            df.set_index('time', inplace=True)
            self.logger.info(f'extracted {len(df)} {str(self.product)} order books')
            tickstore = LocalTickstore(Path(Path(f'{str(self.behemoth_path)}/db/{books_db}')), 'time')
            tickstore.insert(str(self.product), BiTimestamp(upload_date), df)
            tickstore.close()
            self.logger.info(f'inserted {len(df)} {str(self.product)} order book records on local disk')
        else:
            self.logger.info(f'zero {str(self.db)}/{str(self.product)} books for UTC date {str(upload_date)}')
            tickstore = LocalTickstore(Path(Path(f'{str(self.behemoth_path)}/db/{books_db}')), 'time')
            tickstore.close()

    def __splay_trades_db(self, upload_date: datetime.date):
        pass
