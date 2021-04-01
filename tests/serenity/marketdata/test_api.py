from pytest_mock import MockFixture
from tau.core import HistoricNetworkScheduler

from serenity.marketdata.api import RoutingMarketdataService, CompositeRoutingRule, ExchangeRoutingRule, \
    MarketdataService
from serenity.model.exchange import Exchange, ExchangeInstrument, VenueType
from serenity.model.instrument import InstrumentType, Instrument


def test_routing_marketdata_service(mocker: MockFixture):
    scheduler = HistoricNetworkScheduler(0, 1000)
    mds1 = mocker.MagicMock(MarketdataService)
    mds2 = mocker.MagicMock(MarketdataService)
    rules = CompositeRoutingRule([ExchangeRoutingRule('POLYGON', mds1),
                                  ExchangeRoutingRule('PHEMEX', mds2)])
    router = RoutingMarketdataService(scheduler.get_network(), rules)

    # noinspection DuplicatedCode
    venue_type = VenueType(-1, 'DataAggregator')
    exch1 = Exchange(-1, venue_type, 'POLYGON', 'Polygon.io')
    instr_type1 = InstrumentType(-1, 'ETF')
    instr1 = Instrument(-1, instr_type1, 'SPY')
    xinstr1 = ExchangeInstrument(-1, exch1, instr1, 'SPY')

    venue_type = VenueType(-1, 'CryptoExchange')
    exch2 = Exchange(-1, venue_type, 'PHEMEX', 'Phemex')
    instr_type2 = InstrumentType(-1, 'CurrencyPair')
    instr2 = Instrument(-1, instr_type2, 'BTCUSD')
    xinstr2 = ExchangeInstrument(-1, exch2, instr2, 'BTCUSD')

    assert router.get_subscribed_instruments() is not None

    assert router.get_order_book_events(xinstr1) is mds1.get_order_book_events()
    assert router.get_order_book_events(xinstr2) is mds2.get_order_book_events()

    assert router.get_order_books(xinstr1) is mds1.get_order_books()
    assert router.get_order_books(xinstr2) is mds2.get_order_books()

    assert router.get_trades(xinstr1) is mds1.get_trades()
    assert router.get_trades(xinstr2) is mds2.get_trades()

    scheduler.run()
