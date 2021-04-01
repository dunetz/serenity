from abc import ABC, abstractmethod
from enum import Enum, auto

from tau.core import Signal, NetworkScheduler, Network

from serenity.analytics.api import DataCaptureService
from serenity.db.api import InstrumentCache, TypeCodeCache
from serenity.marketdata.api import MarketdataService
from serenity.pnl.api import MarkService
from serenity.position.api import PositionService, ExchangePositionService
from serenity.trading.oms import OrderPlacerService


class StrategyState(Enum):
    INITIALIZING = auto()
    STOPPED = auto()
    LIVE = auto()
    CANCELLED = auto()


class StrategyContext:
    """
    Environment for a running strategy instance, provided by the engine.
    """

    def __init__(self, scheduler: NetworkScheduler, instrument_cache: InstrumentCache,
                 md_service: MarketdataService, mark_service: MarkService, op_service: OrderPlacerService,
                 position_service: PositionService, xps: ExchangePositionService, dcs: DataCaptureService,
                 env_vars: dict):
        self.scheduler = scheduler
        self.instrument_cache = instrument_cache
        self.md_service = md_service
        self.mark_service = mark_service
        self.op_service = op_service
        self.position_service = position_service
        self.xps = xps
        self.dcs = dcs
        self.env_vars = env_vars

    def get_scheduler(self) -> NetworkScheduler:
        return self.scheduler

    def get_network(self) -> Network:
        return self.get_scheduler().get_network()

    def get_instrument_cache(self) -> InstrumentCache:
        return self.instrument_cache

    def get_typecode_cache(self) -> TypeCodeCache:
        return self.get_instrument_cache().get_type_code_cache()

    def get_marketdata_service(self) -> MarketdataService:
        return self.md_service

    def get_mark_service(self) -> MarkService:
        return self.mark_service

    def get_order_placer_service(self) -> OrderPlacerService:
        return self.op_service

    def get_position_service(self) -> PositionService:
        return self.position_service

    def get_exchange_position_service(self) -> ExchangePositionService:
        return self.xps

    def get_data_capture_service(self) -> DataCaptureService:
        return self.dcs

    def getenv(self, key: str, default_value=None):
        if key in self.env_vars:
            value = self.env_vars[key]
            if value is None or value == '':
                return default_value
            return value
        else:
            return default_value


class Strategy(ABC):
    """
    An abstract trading strategy, offering basic lifecycle hooks so you can plug in
    your own strategies and run them in the engine.
    """
    def get_state(self) -> Signal:
        """
        Gets a stream of updates for this strategy's current state.
        """
        pass

    @abstractmethod
    def init(self, ctx: StrategyContext):
        """
        Callback made once when strategy is loaded into the engine.
        """
        pass

    def start(self):
        """
        Callback made whenever the strategy is started by a command from the engine.
        This call is only valid for states INITIALIZING and STOPPED.
        """
        pass

    def stop(self):
        """
        Callback made whenever the strategy is paused by a command from the engine.
        This call is only valid for the LIVE state.
        """
        pass

    def cancel(self):
        """
        Callback made whenever the strategy is cancelled by a command from the engine.
        This call is valid for all states except CANCELLED. Subsequent to a cancel the
        strategy needs to be re-created or the engine restarted in order to continue trading.
        """
        pass
