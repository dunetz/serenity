from serenity.data.batch.load_sharadar_tickers import LoadSharadarTickersTask
from serenity.data.batch.utils import LoadSharadarTableTask, ExportQuandlTableTask
from serenity.data.sharadar_api import clean_nulls
from serenity.data.sharadar_refdata import Ticker, CorporateActionType, CorporateAction


class LoadCorporateActionsTask(LoadSharadarTableTask):
    def requires(self):
        return [
            LoadSharadarTickersTask(start_date=self.start_date, end_date=self.end_date),
            ExportQuandlTableTask(table_name=self.get_workflow_name(), date_column='date',
                                  start_date=self.start_date, end_date=self.end_date)
        ]

    def process_row(self, index, row):
        ticker_code = clean_nulls(row['ticker'])
        ticker = Ticker.find_by_ticker(self.session, ticker_code)

        corp_action_date = row['date']
        corp_action_type_code = row['action']
        corp_action_type = CorporateActionType.get_or_create(self.session, corp_action_type_code)

        name = row['name']
        value = clean_nulls(row['value'])
        contra_ticker = clean_nulls(row['contraticker'])
        contra_name = clean_nulls(row['contraname'])

        corp_action = CorporateAction.find(self.session, ticker_code, corp_action_date, corp_action_type_code)
        if corp_action is None:
            corp_action = CorporateAction(corp_action_date=corp_action_date, ticker_code=ticker_code, ticker=ticker,
                                          corp_action_type=corp_action_type, name=name,
                                          value=value, contra_ticker=contra_ticker, contra_name=contra_name)
        else:
            corp_action.ticker = ticker
            corp_action.name = name
            corp_action.value = value
            corp_action.contra_ticker = contra_ticker
            corp_action.contra_name = contra_name

        self.session.add(corp_action)

    def get_workflow_name(self):
        return 'SHARADAR/ACTIONS'
