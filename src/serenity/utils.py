import asyncio
import json
import logging
import os
import socket

import toml
import websockets
from tau.core import MutableSignal, NetworkScheduler

defaults = dict()


def init_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(logging.WARNING)
    console_logger = logging.StreamHandler()
    if os.getenv('DEBUG'):
        console_logger.setLevel(logging.DEBUG)
    else:
        console_logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(threadName)s] - %(name)s - %(levelname)s - %(message)s')
    console_logger.setFormatter(formatter)
    logger.addHandler(console_logger)


def init_defaults():
    global defaults
    config_path = os.path.join(os.path.dirname(__file__), 'defaults.cfg')
    defaults = toml.load(config_path)


def get_global_defaults() -> dict:
    if len(defaults) == 0:
        init_defaults()
    return defaults


def custom_asyncio_error_handler(loop, context):
    # first, handle with default handler
    loop.default_exception_handler(context)

    # force shutdown
    loop.stop()


async def websocket_subscribe_with_retry(ws_uri, timeout: int, logger: logging.Logger, subscribe_msg: dict,
                                         scheduler: NetworkScheduler, messages: MutableSignal, subscription_desc: str,
                                         msg_type: str):
    while True:
        try:
            async with websockets.connect(ws_uri) as sock:
                subscribe_msg_txt = json.dumps(subscribe_msg)
                logger.info(f'sending {msg_type} subscription request for {subscription_desc}')
                await sock.send(subscribe_msg_txt)
                while True:
                    try:
                        scheduler.schedule_update(messages, await sock.recv())
                    except BaseException as error:
                        logger.error(f'disconnected; attempting to reconnect after {timeout} '
                                     f'seconds: {error}')
                        await asyncio.sleep(timeout)

                        # exit inner loop
                        break
        except socket.gaierror as error:
            logger.error(f'failed with socket error; attempting to reconnect after {timeout} '
                         f'seconds: {error}')
            await asyncio.sleep(timeout)
            continue
        except ConnectionRefusedError as error:
            logger.error(f'connection refused; attempting to reconnect after {timeout} '
                         f'seconds: {error}')
            await asyncio.sleep(timeout)
            continue
        except BaseException as error:
            logger.error(f'unknown connection error; attempting to reconnect after {timeout} '
                         f'seconds: {error}')
            await asyncio.sleep(timeout)
            continue


class Environment:
    def __init__(self, config_yaml, parent=None):
        self.values = parent.values if parent is not None else {}
        for entry in config_yaml:
            key = entry['key']
            value = None
            if 'value' in entry:
                value = entry['value']
            elif 'value-source' in entry:
                source = entry['value-source']
                if source == 'SYSTEM_ENV':
                    value = os.getenv(key)
            else:
                raise ValueError(f'Unsupported value type in Environment entry: {entry}')

            self.values[key] = value

    def getenv(self, key: str, default_val: str = None) -> str:
        if key in self.values:
            value = self.values[key]
            if value is None or value == '':
                return default_val
            else:
                return value
        else:
            return default_val
