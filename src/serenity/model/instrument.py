from abc import ABC
from datetime import datetime
from typing import Optional

from serenity.model.api import TypeCode


class Currency:
    def __init__(self, currency_id: int, currency_code: str):
        self.currency_id = currency_id
        self.currency_code = currency_code

    def get_currency_id(self) -> int:
        return self.currency_id

    def get_currency_code(self) -> str:
        return self.currency_code

    def __str__(self) -> str:
        return self.currency_code


class InstrumentType(TypeCode):
    def __init__(self, type_id: int, type_code: str):
        super().__init__(type_id, type_code)


class ProductEconomics:
    # forward declaration
    pass


class Instrument:
    def __init__(self, instrument_id: int, instrument_type: InstrumentType, instrument_code: str):
        self.instrument_id = instrument_id
        self.instrument_type = instrument_type
        self.instrument_code = instrument_code
        self.economics = None

    def get_instrument_id(self) -> int:
        return self.instrument_id

    def get_instrument_code(self) -> str:
        return self.instrument_code

    def get_instrument_type(self) -> InstrumentType:
        return self.instrument_type

    def get_economics(self) -> ProductEconomics:
        return self.economics

    def set_economics(self, economics: ProductEconomics):
        self.economics = economics


# noinspection PyRedeclaration
class ProductEconomics(ABC):
    def __init__(self, instrument: Instrument):
        self.instrument = instrument

    def get_instrument(self) -> Instrument:
        return self.instrument


class CashInstrument(ProductEconomics):
    def __init__(self, cash_instrument_id: int, instrument: Instrument, currency: Currency):
        super().__init__(instrument)
        self.cash_instrument_id = cash_instrument_id
        self.currency = currency

    def get_cash_instrument_id(self) -> int:
        return self.cash_instrument_id

    def get_currency(self) -> Currency:
        return self.currency


class CurrencyPair(ProductEconomics):
    def __init__(self, currency_pair_id: int, instrument: Instrument, base_currency: Currency,
                 quote_currency: Currency):
        super().__init__(instrument)
        self.currency_pair_id = currency_pair_id
        self.base_currency = base_currency
        self.quote_currency = quote_currency

    def get_currency_pair_id(self) -> int:
        return self.currency_pair_id

    def get_base_currency(self) -> Currency:
        return self.base_currency

    def get_quote_currency(self) -> Currency:
        return self.quote_currency


class FutureContract(ProductEconomics):
    def __init__(self, future_contract_id: int, instrument: Instrument, underlier: Instrument, contract_size: int,
                 expiry: Optional[datetime] = None):
        super().__init__(instrument)
        self.future_contract_id = future_contract_id
        self.underlier = underlier
        self.contract_size = contract_size
        self.expiry = expiry

    def get_future_contract_id(self) -> int:
        return self.future_contract_id

    def get_underlier(self) -> Instrument:
        return self.underlier

    def get_contract_size(self) -> int:
        return self.contract_size

    def get_expiry(self) -> Optional[datetime]:
        return self.expiry


class Equity(ProductEconomics):
    def __init__(self, equity_id: int, instrument: Instrument, calendar: str, tz: str):
        super().__init__(instrument)
        self.equity_id = equity_id
        self.calendar = calendar
        self.tz = tz

    def get_equity_id(self) -> int:
        return self.equity_id

    def get_calendar(self) -> str:
        return self.calendar

    def get_tz(self) -> str:
        return self.tz
