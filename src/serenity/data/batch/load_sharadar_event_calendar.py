from serenity.data.batch.load_sharadar_tickers import LoadSharadarTickersTask
from serenity.data.batch.utils import LoadSharadarTableTask, ExportQuandlTableTask
from serenity.data.sharadar_refdata import Ticker, get_indicator_details, EventCode, Event


class LoadEventCalendarTask(LoadSharadarTableTask):
    def requires(self):
        return [
            LoadSharadarTickersTask(start_date=self.start_date, end_date=self.end_date),
            ExportQuandlTableTask(table_name=self.get_workflow_name(), date_column='date',
                                  start_date=self.start_date, end_date=self.end_date)
        ]

    def process_row(self, index, row):
        ticker_code = row['ticker']
        ticker = Ticker.find_by_ticker(self.session, ticker_code)
        event_date = row['date']
        event_codes = row['eventcodes']
        for event_code in event_codes.split('|'):
            indicator = get_indicator_details(self.session, 'EVENTCODES', event_code)
            event_code_entity = EventCode.get_or_create(self.session, int(event_code), indicator.title)
            event = Event.find(self.session, ticker_code, event_date, int(event_code))
            if event is None:
                event = Event(ticker_code=ticker_code, ticker=ticker, event_date=event_date,
                              event_code=event_code_entity)
            else:
                event.ticker = ticker
            self.session.add(event)

    def get_workflow_name(self):
        return 'SHARADAR/EVENTS'
