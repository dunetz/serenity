from serenity.data.batch.load_sharadar_tickers import LoadSharadarTickersTask
from serenity.data.batch.utils import LoadSharadarTableTask, ExportQuandlTableTask
from serenity.data.sharadar_api import clean_nulls
from serenity.data.sharadar_holdings import InstitutionalInvestor, SecurityType, InstitutionalHoldings
from serenity.data.sharadar_refdata import Ticker


class LoadInstitutionalHoldingsTask(LoadSharadarTableTask):
    def requires(self):
        return [
            LoadSharadarTickersTask(start_date=self.start_date, end_date=self.end_date),
            ExportQuandlTableTask(table_name=self.get_workflow_name(), date_column='calendardate',
                                  start_date=self.start_date, end_date=self.end_date)
        ]

    def process_row(self, index, row):
        ticker_code = row['ticker']
        ticker = Ticker.find_by_ticker(self.session, ticker_code)

        investor_name = row['investorname']
        investor = InstitutionalInvestor.get_or_create(self.session, investor_name)

        security_type_code = row['securitytype']
        security_type = SecurityType.get_or_create(self.session, security_type_code)

        calendar_date = row['calendardate']
        value = row['value']
        units = row['units']
        price = clean_nulls(row['price'])

        holdings = InstitutionalHoldings.find(self.session, ticker_code, investor, security_type, calendar_date)
        if holdings is None:
            holdings = InstitutionalHoldings(ticker=ticker, investor=investor, security_type=security_type,
                                             calendar_date=calendar_date, value=value, units=units, price=price)
        else:
            holdings.value = value
            holdings.units = units
            holdings.price = price

        self.session.add(holdings)

    def get_workflow_name(self):
        return 'SHARADAR/SF3'
