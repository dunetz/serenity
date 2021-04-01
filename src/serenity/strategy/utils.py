import importlib
import logging
import sys

from pathlib import Path


class StrategyLoader:
    logger = logging.getLogger(__name__)

    def __init__(self, strategy_dir: Path):
        sys.path.append(str(strategy_dir))

    def load(self, strategy_module: str, strategy_class: str):
        self.logger.info(f'Dynamically loading strategy: {strategy_module}#{strategy_class}')

        module = importlib.import_module(strategy_module)
        klass = getattr(module, strategy_class)
        strategy_instance = klass()

        return strategy_instance
