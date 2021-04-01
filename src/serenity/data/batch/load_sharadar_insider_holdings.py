from serenity.data.batch.load_sharadar_tickers import LoadSharadarTickersTask
from serenity.data.batch.utils import LoadSharadarTableTask, ExportQuandlTableTask
from serenity.data.sharadar_api import clean_nulls, yes_no_to_bool
from serenity.data.sharadar_holdings import FormType, SecurityAdType, TransactionType, SecurityTitleType, \
    InsiderHoldings
from serenity.data.sharadar_refdata import Ticker


# noinspection DuplicatedCode
class LoadInsiderHoldingsTask(LoadSharadarTableTask):
    def requires(self):
        return [
            LoadSharadarTickersTask(start_date=self.start_date, end_date=self.end_date),
            ExportQuandlTableTask(table_name=self.get_workflow_name(), date_column='filingdate',
                                  start_date=self.start_date, end_date=self.end_date)
        ]

    def process_row(self, index, row):
        ticker_code = row['ticker']
        ticker = Ticker.find_by_ticker(self.session, ticker_code)
        filing_date = row['filingdate']

        form_type_code = row['formtype']
        form_type = FormType.get_or_create(self.session, form_type_code)

        issuer_name = row['issuername']
        owner_name = row['ownername']
        officer_title = row['officertitle']
        is_director = yes_no_to_bool(row['isdirector'])
        is_officer = yes_no_to_bool(row['isofficer'])
        is_ten_percent_owner = yes_no_to_bool(row['istenpercentowner'])
        transaction_date = clean_nulls(row['transactiondate'])

        security_ad_type_code = clean_nulls(row['securityadcode'])
        security_ad_type = SecurityAdType.get_or_create(self.session, security_ad_type_code)

        transaction_type_code = clean_nulls(row['transactioncode'])
        transaction_type = TransactionType.get_or_create(self.session, transaction_type_code)

        shares_owned_before_transaction = clean_nulls(row['sharesownedbeforetransaction'])
        transaction_shares = clean_nulls(row['transactionshares'])
        shares_owned_following_transaction = clean_nulls(row['sharesownedfollowingtransaction'])
        transaction_price_per_share = clean_nulls(row['transactionpricepershare'])
        transaction_value = clean_nulls(row['transactionvalue'])

        security_title_type_code = clean_nulls(row['securitytitle'])
        security_title_type = SecurityTitleType.get_or_create(self.session, security_title_type_code)

        direct_or_indirect = clean_nulls(row['directorindirect'])
        nature_of_ownership = clean_nulls(row['natureofownership'])
        date_exercisable = clean_nulls(row['dateexercisable'])
        price_exercisable = clean_nulls(row['priceexercisable'])
        expiration_date = clean_nulls(row['expirationdate'])
        row_num = row['rownum']

        holdings = InsiderHoldings.find(self.session, ticker_code, filing_date, owner_name, form_type, row_num)
        if holdings is None:
            holdings = InsiderHoldings(ticker_code=ticker_code, ticker=ticker, filing_date=filing_date,
                                       form_type=form_type, issuer_name=issuer_name, owner_name=owner_name,
                                       officer_title=officer_title, is_director=is_director, is_officer=is_officer,
                                       is_ten_percent_owner=is_ten_percent_owner, transaction_date=transaction_date,
                                       security_ad_type=security_ad_type, transaction_type=transaction_type,
                                       shares_owned_before_transaction=shares_owned_before_transaction,
                                       transaction_shares=transaction_shares,
                                       shares_owned_following_transaction=shares_owned_following_transaction,
                                       transaction_price_per_share=transaction_price_per_share,
                                       transaction_value=transaction_value, security_title_type=security_title_type,
                                       direct_or_indirect=direct_or_indirect, nature_of_ownership=nature_of_ownership,
                                       date_exercisable=date_exercisable, price_exercisable=price_exercisable,
                                       expiration_date=expiration_date, row_num=row_num)
        else:
            holdings.ticker = ticker
            holdings.issuer_name = issuer_name
            holdings.officer_title = officer_title
            holdings.is_director = is_director
            holdings.is_officer = is_officer
            holdings.is_ten_percent_owner = is_ten_percent_owner
            holdings.transaction_date = transaction_date
            holdings.shares_owned_before_transaction = shares_owned_before_transaction
            holdings.transaction_shares = transaction_shares
            holdings.shares_owned_following_transaction = shares_owned_following_transaction
            holdings.transaction_price_per_share = transaction_price_per_share
            holdings.transaction_value = transaction_value
            holdings.security_title_type = security_title_type
            holdings.direct_or_indirect = direct_or_indirect
            holdings.nature_of_ownership = nature_of_ownership
            holdings.date_exercisable = date_exercisable
            holdings.price_exercisable = price_exercisable
            holdings.expiration_date = expiration_date

        self.session.add(holdings)

    def get_workflow_name(self):
        return 'SHARADAR/SF2'
