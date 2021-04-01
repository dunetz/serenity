from serenity.data.batch.load_sharadar_tickers import LoadSharadarTickersTask
from serenity.data.batch.utils import LoadSharadarTableTask, ExportQuandlTableTask
from serenity.data.sharadar_api import clean_nulls
from serenity.data.sharadar_fundamentals import DimensionType, Fundamentals
from serenity.data.sharadar_refdata import Ticker


# noinspection DuplicatedCode
class LoadEquityFundamentalsTask(LoadSharadarTableTask):
    def requires(self):
        return [
            LoadSharadarTickersTask(start_date=self.start_date, end_date=self.end_date),
            ExportQuandlTableTask(table_name=self.get_workflow_name(), date_column='lastupdated',
                                  start_date=self.start_date, end_date=self.end_date)
        ]

    def process_row(self, index, row):
        ticker_code = row['ticker']
        ticker = Ticker.find_by_ticker(self.session, ticker_code)

        dimension_type_code = row['dimension']
        dimension_type = DimensionType.get_or_create(self.session, dimension_type_code)

        calendar_date = row['calendardate']
        date_key = row['datekey']
        report_period = row['reportperiod']
        last_updated = row['lastupdated']

        accoci = clean_nulls(row['accoci'])
        assets = clean_nulls(row['assets'])
        assets_avg = clean_nulls(row['assetsavg'])
        assets_c = clean_nulls(row['assetsc'])
        assets_nc = clean_nulls(row['assetsnc'])
        asset_turnover = clean_nulls(row['assetturnover'])
        bvps = clean_nulls(row['bvps'])
        capex = clean_nulls(row['capex'])
        cash_neq = clean_nulls(row['cashneq'])
        cash_neq_usd = clean_nulls(row['cashnequsd'])
        cor = clean_nulls(row['cor'])
        consol_inc = clean_nulls(row['consolinc'])
        current_ratio = clean_nulls(row['currentratio'])
        de = clean_nulls(row['de'])
        debt = clean_nulls(row['debt'])
        debt_c = clean_nulls(row['debtc'])
        debt_nc = clean_nulls(row['debtnc'])
        debt_usd = clean_nulls(row['debtusd'])
        deferred_rev = clean_nulls(row['deferredrev'])
        dep_amor = clean_nulls(row['depamor'])
        deposits = clean_nulls(row['deposits'])
        div_yield = clean_nulls(row['divyield'])
        dps = clean_nulls(row['dps'])
        ebit = clean_nulls(row['ebit'])
        ebitda = clean_nulls(row['ebitda'])
        ebitda_margin = clean_nulls(row['ebitdamargin'])
        ebitda_usd = clean_nulls(row['ebitdausd'])
        ebit_usd = clean_nulls(row['ebitusd'])
        ebt = clean_nulls(row['ebt'])
        eps = clean_nulls(row['eps'])
        eps_dil = clean_nulls(row['epsdil'])
        eps_usd = clean_nulls(row['epsusd'])
        equity = clean_nulls(row['equity'])
        equity_avg = clean_nulls(row['equityavg'])
        equity_usd = clean_nulls(row['equityusd'])
        ev = clean_nulls(row['ev'])
        ev_ebit = clean_nulls(row['evebit'])
        ev_ebitda = clean_nulls(row['evebitda'])
        fcf = clean_nulls(row['fcf'])
        fcf_ps = clean_nulls(row['fcfps'])
        fx_usd = clean_nulls(row['fxusd'])
        gp = clean_nulls(row['gp'])
        gross_margin = clean_nulls(row['grossmargin'])
        int_exp = clean_nulls(row['intexp'])
        inv_cap = clean_nulls(row['invcap'])
        inv_cap_avg = clean_nulls(row['invcapavg'])
        inventory = clean_nulls(row['inventory'])
        investments = clean_nulls(row['investments'])
        investments_c = clean_nulls(row['investmentsc'])
        investments_nc = clean_nulls(row['investmentsnc'])
        liabilities = clean_nulls(row['liabilities'])
        liabilities_c = clean_nulls(row['liabilitiesc'])
        liabilities_nc = clean_nulls(row['liabilitiesnc'])
        market_cap = clean_nulls(row['marketcap'])
        ncf = clean_nulls(row['ncf'])
        ncf_bus = clean_nulls(row['ncfbus'])
        ncf_common = clean_nulls(row['ncfcommon'])
        ncf_debt = clean_nulls(row['ncfdebt'])
        ncf_div = clean_nulls(row['ncfdiv'])
        ncf_f = clean_nulls(row['ncff'])
        ncf_i = clean_nulls(row['ncfi'])
        ncf_inv = clean_nulls(row['ncfinv'])
        ncf_o = clean_nulls(row['ncfo'])
        ncf_x = clean_nulls(row['ncfx'])
        net_inc = clean_nulls(row['netinc'])
        net_inc_cmn = clean_nulls(row['netinccmn'])
        net_inc_cmn_usd = clean_nulls(row['netinccmnusd'])
        net_inc_dis = clean_nulls(row['netincdis'])
        net_inc_nci = clean_nulls(row['netincnci'])
        net_margin = clean_nulls(row['netmargin'])
        op_ex = clean_nulls(row['opex'])
        op_inc = clean_nulls(row['opinc'])
        payables = clean_nulls(row['payables'])
        payout_ratio = clean_nulls(row['payoutratio'])
        pb = clean_nulls(row['pb'])
        pe = clean_nulls(row['pe'])
        pe1 = clean_nulls(row['pe1'])
        ppne_net = clean_nulls(row['ppnenet'])
        pref_div_is = clean_nulls(row['prefdivis'])
        price = clean_nulls(row['price'])
        ps = clean_nulls(row['ps'])
        ps1 = clean_nulls(row['ps1'])
        receivables = clean_nulls(row['receivables'])
        ret_earn = clean_nulls(row['retearn'])
        revenue = clean_nulls(row['revenue'])
        revenue_usd = clean_nulls(row['revenueusd'])
        rnd = clean_nulls(row['rnd'])
        roa = clean_nulls(row['roa'])
        roe = clean_nulls(row['roe'])
        roic = clean_nulls(row['roic'])
        ros = clean_nulls(row['ros'])
        sb_comp = clean_nulls(row['sbcomp'])
        sgna = clean_nulls(row['sgna'])
        share_factor = clean_nulls(row['sharefactor'])
        shares_bas = clean_nulls(row['sharesbas'])
        shares_wa = clean_nulls(row['shareswa'])
        shares_wa_dil = clean_nulls(row['shareswadil'])
        sps = clean_nulls(row['sps'])
        tangibles = clean_nulls(row['tangibles'])
        tax_assets = clean_nulls(row['taxassets'])
        tax_exp = clean_nulls(row['taxexp'])
        tax_liabilities = clean_nulls(row['taxliabilities'])
        tbvps = clean_nulls(row['tbvps'])
        working_capital = clean_nulls(row['workingcapital'])

        fundamentals = Fundamentals.find(self.session, ticker_code, dimension_type, date_key, report_period)
        if fundamentals is None:
            fundamentals = Fundamentals(ticker_code=ticker_code, ticker=ticker, dimension_type=dimension_type,
                                        calendar_date=calendar_date, date_key=date_key, report_period=report_period,
                                        last_updated=last_updated, accoci=accoci, assets=assets, assets_avg=assets_avg,
                                        assets_c=assets_c, assets_nc=assets_nc, asset_turnover=asset_turnover,
                                        bvps=bvps, capex=capex, cash_neq=cash_neq, cash_neq_usd=cash_neq_usd, cor=cor,
                                        consol_inc=consol_inc, current_ratio=current_ratio, de=de, debt=debt,
                                        debt_c=debt_c, debt_nc=debt_nc, debt_usd=debt_usd, deferred_rev=deferred_rev,
                                        dep_amor=dep_amor, deposits=deposits, div_yield=div_yield, dps=dps, ebit=ebit,
                                        ebitda=ebitda, ebitda_margin=ebitda_margin, ebitda_usd=ebitda_usd,
                                        ebit_usd=ebit_usd, ebt=ebt, eps=eps, eps_dil=eps_dil, eps_usd=eps_usd,
                                        equity=equity, equity_avg=equity_avg, equity_usd=equity_usd, ev=ev,
                                        ev_ebit=ev_ebit, ev_ebitda=ev_ebitda, fcf=fcf, fcf_ps=fcf_ps, fx_usd=fx_usd,
                                        gp=gp, gross_margin=gross_margin, int_exp=int_exp, inv_cap=inv_cap,
                                        inv_cap_avg=inv_cap_avg, inventory=inventory, investments=investments,
                                        investments_c=investments_c, investments_nc=investments_nc,
                                        liabilities=liabilities, liabilities_c=liabilities_c,
                                        liabilities_nc=liabilities_nc, market_cap=market_cap, ncf=ncf, ncf_bus=ncf_bus,
                                        ncf_common=ncf_common, ncf_debt=ncf_debt, ncf_div=ncf_div, ncf_f=ncf_f,
                                        ncf_i=ncf_i, ncf_inv=ncf_inv, ncf_o=ncf_o, ncf_x=ncf_x, net_inc=net_inc,
                                        net_inc_cmn=net_inc_cmn, net_inc_cmn_usd=net_inc_cmn_usd,
                                        net_inc_dis=net_inc_dis, net_inc_nci=net_inc_nci, net_margin=net_margin,
                                        op_ex=op_ex, op_inc=op_inc, payables=payables, payout_ratio=payout_ratio, pb=pb,
                                        pe=pe, pe1=pe1, ppne_net=ppne_net, pref_div_is=pref_div_is, price=price, ps=ps,
                                        ps1=ps1, receivables=receivables, ret_earn=ret_earn, revenue=revenue,
                                        revenue_usd=revenue_usd, rnd=rnd, roa=roa, roe=roe, roic=roic, ros=ros,
                                        sb_comp=sb_comp, sgna=sgna, share_factor=share_factor, shares_bas=shares_bas,
                                        shares_wa=shares_wa, shares_wa_dil=shares_wa_dil, sps=sps, tangibles=tangibles,
                                        tax_assets=tax_assets, tax_exp=tax_exp, tax_liabilities=tax_liabilities,
                                        tbvps=tbvps, working_capital=working_capital)
        else:
            fundamentals.ticker = ticker
            fundamentals.calendar_date = calendar_date
            fundamentals.last_updated = last_updated
            fundamentals.accoci = accoci
            fundamentals.assets = assets
            fundamentals.assets_avg = assets_avg
            fundamentals.assets_c = assets_c
            fundamentals.assets_nc = assets_nc
            fundamentals.asset_turnover = asset_turnover
            fundamentals.bvps = bvps
            fundamentals.capex = capex
            fundamentals.cash_neq = cash_neq
            fundamentals.cash_neq_usd = cash_neq_usd
            fundamentals.cor = cor
            fundamentals.consol_inc = consol_inc
            fundamentals.current_ratio = current_ratio
            fundamentals.de = de
            fundamentals.debt = debt
            fundamentals.debt_c = debt_c
            fundamentals.debt_nc = debt_nc
            fundamentals.debt_usd = debt_usd
            fundamentals.deferred_rev = deferred_rev
            fundamentals.dep_amor = dep_amor
            fundamentals.deposits = deposits
            fundamentals.div_yield = div_yield
            fundamentals.dps = dps
            fundamentals.ebit = ebit
            fundamentals.ebitda = ebitda
            fundamentals.ebitda_margin = ebitda_margin
            fundamentals.ebitda_usd = ebitda_usd
            fundamentals.ebit_usd = ebit_usd
            fundamentals.ebt = ebt
            fundamentals.eps = eps
            fundamentals.eps_dil = eps_dil
            fundamentals.eps_usd = eps_usd
            fundamentals.equity = equity
            fundamentals.equity_avg = equity_avg
            fundamentals.equity_usd = equity_usd
            fundamentals.ev = ev
            fundamentals.ev_ebit = ev_ebit
            fundamentals.ev_ebitda = ev_ebitda
            fundamentals.fcf = fcf
            fundamentals.fcf_ps = fcf_ps
            fundamentals.fx_usd = fx_usd
            fundamentals.gp = gp
            fundamentals.gross_margin = gross_margin
            fundamentals.int_exp = int_exp
            fundamentals.inv_cap = inv_cap
            fundamentals.inv_cap_avg = inv_cap_avg
            fundamentals.inventory = inventory
            fundamentals.investments = investments
            fundamentals.investments_c = investments_c
            fundamentals.investments_nc = investments_nc
            fundamentals.liabilities = liabilities
            fundamentals.liabilities_c = liabilities_c
            fundamentals.liabilities_nc = liabilities_nc
            fundamentals.market_cap = market_cap
            fundamentals.ncf = ncf
            fundamentals.ncf_bus = ncf_bus
            fundamentals.ncf_common = ncf_common
            fundamentals.ncf_debt = ncf_debt
            fundamentals.ncf_div = ncf_div
            fundamentals.ncf_f = ncf_f
            fundamentals.ncf_i = ncf_i
            fundamentals.ncf_inv = ncf_inv
            fundamentals.ncf_o = ncf_o
            fundamentals.ncf_x = ncf_x
            fundamentals.net_inc = net_inc
            fundamentals.net_inc_cmn = net_inc_cmn
            fundamentals.net_inc_cmn_usd = net_inc_cmn_usd
            fundamentals.net_inc_dis = net_inc_dis
            fundamentals.net_inc_nci = net_inc_nci
            fundamentals.net_margin = net_margin
            fundamentals.op_ex = op_ex
            fundamentals.op_inc = op_inc
            fundamentals.payables = payables
            fundamentals.payout_ratio = payout_ratio
            fundamentals.pb = pb
            fundamentals.pe = pe
            fundamentals.pe1 = pe1
            fundamentals.ppne_net = ppne_net
            fundamentals.pref_div_is = pref_div_is
            fundamentals.price = price
            fundamentals.ps = ps
            fundamentals.ps1 = ps1
            fundamentals.receivables = receivables
            fundamentals.ret_earn = ret_earn
            fundamentals.revenue = revenue
            fundamentals.revenue_usd = revenue_usd
            fundamentals.rnd = rnd
            fundamentals.roa = roa
            fundamentals.roe = roe
            fundamentals.roic = roic
            fundamentals.ros = ros
            fundamentals.sb_comp = sb_comp
            fundamentals.sgna = sgna
            fundamentals.share_factor = share_factor
            fundamentals.shares_bas = shares_bas
            fundamentals.shares_wa = shares_wa
            fundamentals.shares_wa_dil = shares_wa_dil
            fundamentals.sps = sps
            fundamentals.tangibles = tangibles
            fundamentals.tax_assets = tax_assets
            fundamentals.tax_exp = tax_exp
            fundamentals.tax_liabilities = tax_liabilities
            fundamentals.tbvps = tbvps
            fundamentals.working_capital = working_capital

        self.session.add(fundamentals)

    def get_workflow_name(self):
        return 'SHARADAR/SF1'
