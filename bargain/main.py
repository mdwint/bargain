import logging
from collections import namedtuple
from datetime import datetime, timedelta

from bargain.bot import Bot
from bargain.exchange.bitfinex import Bitfinex
from bargain.currency import Currency
from bargain.strategy.ema import EMAC


logging.basicConfig()
log = logging.getLogger()


Config = namedtuple('Config', 'debug, interval, history, now, pair, exchange, strategy')

# TODO: Remove
_default_config = Config(debug=True, interval=timedelta(minutes=15), history=timedelta(hours=24),
                         now=datetime.utcnow(), pair=(Currency.ETH, Currency.USD),
                         exchange=Bitfinex(), strategy=EMAC(13, 49))


def serverless_handler(event, context):
    # TODO: Parse event
    main(_default_config)


def cli_handler():
    # TODO: Parse CLI arguments
    main(_default_config)


def main(config):
    log.setLevel(logging.DEBUG if config.debug else logging.INFO)

    bot = Bot(config.exchange, config.now, config.interval, config.history)
    bot.trade(config.strategy, config.pair)
