import asyncio
import logging
import sys
from time import sleep

import asyncpg

from queuebot.bot import Queuebot
from queuebot.config import config_from_file

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


logging.getLogger('discord').setLevel(logging.INFO)
logging.getLogger('queuebot').setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

handler = logging.FileHandler(filename='queuebot.log', encoding='utf-8', mode='a')
handler.setFormatter(formatter)

stream = logging.StreamHandler(stream=sys.stdout)
stream.setFormatter(formatter)

logging.getLogger().addHandler(handler)  # Log everything to queuebot.log.
logging.getLogger().addHandler(stream)   # Log everything to stdout.


async def main():
    config = config_from_file("config.yaml")
    while True:
        try:
            db = await asyncpg.create_pool(**config.pg_credentials)
        except (ConnectionRefusedError, asyncpg.CannotConnectNowError):
            logging.getLogger('run').exception('Cannot connect to Postgres, stalling:')
            await asyncio.sleep(2)
        else:
            break

    bot = Queuebot(
        command_prefix='!',
        fetch_offline_members=False,
        guild_subscriptions=False,
        max_messages=0,
        config=config,
        db=db,
    )


    bot.discover_exts('queuebot/cogs')
    bot.load_extension('jishaku')
    await bot.start(config.token)


sleep(2)  # wait for postgres to start

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
