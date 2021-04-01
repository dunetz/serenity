import asyncio
import importlib
import logging
import signal
import sys

import fire
import yaml
from phemex import AuthCredentials
from tau.core import RealtimeNetworkScheduler

from serenity.algo.api import StrategyContext
from serenity.analytics.api import HDF5DataCaptureService, Mode
from serenity.booker.api import TimescaleDbTradeBookingService
from serenity.db.api import InstrumentCache, connect_serenity_db, TypeCodeCache
from serenity.marketdata.fh.binance_fh import BinanceFeedHandler
from serenity.marketdata.fh.coinbasepro_fh import CoinbaseProFeedHandler
from serenity.marketdata.fh.feedhandler import FeedHandlerRegistry, FeedHandlerMarketdataService
from serenity.marketdata.fh.phemex_fh import PhemexFeedHandler
from serenity.pnl.phemex import PhemexMarkService
from serenity.position.api import PositionService
from serenity.trading.oms import OrderManagerService, OrderPlacerService
from serenity.trading.connector.phemex_api import PhemexOrderPlacer, PhemexExchangePositionService
from serenity.utils import init_logging, custom_asyncio_error_handler, Environment


class AlgoEngine:
    """"
    Algorithmic trading engine.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, config_path: str, strategy_dir: str):
        sys.path.append(strategy_dir)

        with open(config_path, 'r') as config_yaml:
            logger = logging.getLogger(__name__)

            logger.info('Serenity starting up')
            config = yaml.safe_load(config_yaml)
            api_version = config['api-version']
            if api_version != 'v1Beta':
                raise ValueError(f'Unsupported API version: {api_version}')

            self.engine_env = Environment(config['environment'])
            instance_id = self.engine_env.getenv('EXCHANGE_INSTANCE', 'prod')
            self.fh_registry = FeedHandlerRegistry()

            account = self.engine_env.getenv('EXCHANGE_ACCOUNT', 'Main')

            logger.info('Connecting to Serenity database')
            conn = connect_serenity_db()
            conn.autocommit = True
            cur = conn.cursor()

            scheduler = RealtimeNetworkScheduler()
            instrument_cache = InstrumentCache(cur, TypeCodeCache(cur))
            if 'feedhandlers' in config:
                logger.info('Registering feedhandlers')
                for feedhandler in config['feedhandlers']:
                    fh_name = feedhandler['exchange']
                    include_symbol = feedhandler.get('include_symbol', '*')
                    if fh_name == 'Phemex':
                        self.fh_registry.register(PhemexFeedHandler(scheduler, instrument_cache, include_symbol,
                                                                    instance_id))
                    elif fh_name == 'Binance':
                        self.fh_registry.register(BinanceFeedHandler(scheduler, instrument_cache, instance_id))
                    elif fh_name == 'CoinbasePro':
                        self.fh_registry.register(CoinbaseProFeedHandler(scheduler, instrument_cache, instance_id))
                    else:
                        raise ValueError(f'Unsupported feedhandler type: {fh_name}')

            oms = OrderManagerService(scheduler, TimescaleDbTradeBookingService())
            op_service = OrderPlacerService(scheduler, oms)
            md_service = FeedHandlerMarketdataService(scheduler, self.fh_registry, instance_id)
            mark_service = PhemexMarkService(scheduler, instrument_cache, instance_id)
            self.xps = None

            extra_outputs_txt = self.engine_env.getenv('EXTRA_OUTPUTS')
            if extra_outputs_txt is None:
                extra_outputs = []
            else:
                extra_outputs = extra_outputs_txt.split(',')
            self.dcs = HDF5DataCaptureService(Mode.LIVE, scheduler, extra_outputs)

            if 'order_placers' in config:
                logger.info('Registering OrderPlacers')
                for order_placer in config['order_placers']:
                    op_name = order_placer['exchange']
                    if op_name == 'Phemex':
                        api_key = self.engine_env.getenv('PHEMEX_API_KEY')
                        api_secret = self.engine_env.getenv('PHEMEX_API_SECRET')
                        if not api_key:
                            raise ValueError('missing PHEMEX_API_KEY')
                        if not api_secret:
                            raise ValueError('missing PHEMEX_API_SECRET')

                        credentials = AuthCredentials(api_key, api_secret)
                        op_service.register_order_placer(f'phemex:{instance_id}',
                                                         PhemexOrderPlacer(credentials, scheduler, oms, account,
                                                                           instance_id))

                        self.xps = PhemexExchangePositionService(credentials, scheduler, instrument_cache, account,
                                                                 instance_id)
                        self.ps = PositionService(scheduler, oms)
                    else:
                        raise ValueError(f'Unsupported order placer: {op_name}')

            self.strategies = []
            self.strategy_names = []
            for strategy in config['strategies']:
                strategy_name = strategy['name']
                self.strategy_names.append(strategy_name)
                self.logger.info(f'Loading strategy: {strategy_name}')
                module = strategy['module']
                strategy_class = strategy['strategy-class']
                env = Environment(strategy['environment'], parent=self.engine_env)

                module = importlib.import_module(module)
                klass = getattr(module, strategy_class)
                strategy_instance = klass()
                ctx = StrategyContext(scheduler, instrument_cache, md_service, mark_service, op_service, self.ps,
                                      self.xps, self.dcs, env.values)
                self.strategies.append((strategy_instance, ctx))

    def start(self):
        # start the live feeds
        for feedhandler in self.fh_registry.get_feedhandlers():
            asyncio.ensure_future(feedhandler.start())

        # subscribe to exchange positions
        self.xps.subscribe()

        def start_strategies():
            for (strategy, ctx) in self.strategies:
                strategy.init(ctx)
                strategy.start()

        asyncio.get_event_loop().call_later(5, start_strategies)
        self.logger.info('<READY FOR TRADING>')

        # crash out on any exception
        asyncio.get_event_loop().set_exception_handler(custom_asyncio_error_handler)

        # store output after event loop shuts down, right before exit
        # noinspection PyUnusedLocal
        def signal_handler(sig, frame):
            for strategy_name in self.strategy_names:
                snapshot_id = self.dcs.store_snapshot(strategy_name)
                self.logger.info(f'stored snapshot: {snapshot_id}')
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # go!
        asyncio.get_event_loop().run_forever()


def main(config_path: str, strategy_dir='.'):
    init_logging()
    engine = AlgoEngine(config_path, strategy_dir)
    engine.start()


if __name__ == '__main__':
    fire.Fire(main)
