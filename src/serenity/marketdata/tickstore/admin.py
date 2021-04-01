from pathlib import Path

import fire

from serenity.marketdata.tickstore.api import LocalTickstore, AzureBlobTickstore
from serenity.utils import init_logging


def tickstore_admin(action: str, db: str, staging_dir: str = '/mnt/raid/data/behemoth/db',
                    connect_str: str = None, db_prefix: str = None):
    init_logging()

    if action == 'reindex':
        tickstore = LocalTickstore(Path(f'{staging_dir}/{db}'), timestamp_column='time')
        tickstore.index.reindex()
        tickstore.close()
    if action == 'strip_prefix':
        tickstore = LocalTickstore(Path(f'{staging_dir}/{db}'), timestamp_column='time')
        tickstore.index.strip_prefix(db_prefix)
        tickstore.close()
    elif action == 'list':
        tickstore = LocalTickstore(Path(f'{staging_dir}/{db}'), timestamp_column='time')
        for symbol in tickstore.index.symbols():
            print(symbol)
            for entry in tickstore.index.entries(symbol):
                print(f'\t{entry}')
    elif action == 'cloudsync':
        local_tickstore = LocalTickstore(Path(f'{staging_dir}/{db}'), timestamp_column='time')
        cloud_tickstore = AzureBlobTickstore(connect_str, db)
        for symbol in local_tickstore.index.symbols():
            for entry in local_tickstore.index.entries(symbol):
                logical_path = entry.path
                ticks = local_tickstore.read(logical_path)
                cloud_tickstore.insert(entry.symbol, entry.ts, ticks)

        local_tickstore.close()
        cloud_tickstore.close()
    else:
        raise Exception(f'Unknown action: {action}')


if __name__ == '__main__':
    fire.Fire(tickstore_admin)
