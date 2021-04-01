import coinbasepro
from phemex import PublicCredentials

from serenity.exchange.gemini import GeminiConnection
from serenity.exchange.phemex import get_phemex_connection

from serenity.db.api import connect_serenity_db, InstrumentCache, TypeCodeCache, ExchangeEntityService

if __name__ == '__main__':
    conn = connect_serenity_db()
    conn.autocommit = True
    cur = conn.cursor()

    type_code_cache = TypeCodeCache(cur)
    instrument_cache = InstrumentCache(cur, type_code_cache)
    exch_service = ExchangeEntityService(cur, type_code_cache, instrument_cache)

    # map all Gemini products to exchange_instrument table
    gemini_client = GeminiConnection()
    gemini = exch_service.instrument_cache.get_crypto_exchange("GEMINI")
    for symbol in gemini_client.get_products():
        base_ccy = symbol[0:3].upper()
        quote_ccy = symbol[3:].upper()
        currency_pair = instrument_cache.get_or_create_cryptocurrency_pair(base_ccy, quote_ccy)
        instrument_cache.get_or_create_exchange_instrument(symbol, currency_pair.get_instrument(), gemini)

    # map all Coinbase Pro products to exchange_instrument table
    cbp_client = coinbasepro.PublicClient()
    cbp = exch_service.instrument_cache.get_crypto_exchange("COINBASEPRO")
    for product in cbp_client.get_products():
        symbol = product['id']
        base_ccy = product['base_currency']
        quote_ccy = product['quote_currency']
        currency_pair = instrument_cache.get_or_create_cryptocurrency_pair(base_ccy, quote_ccy)
        instrument_cache.get_or_create_exchange_instrument(symbol, currency_pair.get_instrument(), cbp)

    # map all Phemex products to exchange_instrument table
    (phemex, ws_uri) = get_phemex_connection(PublicCredentials())
    products = phemex.get_products()
    exchange_code = 'PHEMEX'
    for product in products['data']:
        symbol = product['symbol']
        base_ccy = product['baseCurrency']
        quote_ccy = product['quoteCurrency']
        price_scale = product['priceScale']
        ul_symbol = f'.M{base_ccy}'
        ccy_pair = instrument_cache.get_or_create_cryptocurrency_pair(base_ccy, quote_ccy)
        ul_instr = ccy_pair.get_instrument()
        exchange = instrument_cache.get_crypto_exchange(exchange_code)
        instrument_cache.get_or_create_exchange_instrument(ul_symbol, ul_instr, exchange)
        future = instrument_cache.get_or_create_perpetual_future(ul_instr)
        instr = future.get_instrument()
        exch_instrument = instrument_cache.get_or_create_exchange_instrument(symbol, instr, exchange)
