import logging
from collections import namedtuple
from datetime import datetime, timedelta

from bargain.bot import Bot
from bargain.exchange.bitfinex import Bitfinex
from bargain.currency import Currency
from bargain.strategy import MovingAverage


logging.basicConfig()
log = logging.getLogger()


Config = namedtuple('Config', 'debug, interval, history, pair')


def _get_config(event):
    # TODO: Parse event
    return Config(debug=True, interval=timedelta(minutes=5), history=timedelta(hours=24),
                  pair=(Currency.ETH, Currency.USD))


def trade(event, context):
    config = _get_config(event)
    log.setLevel(logging.DEBUG if config.debug else logging.INFO)

    exchange = Bitfinex()
    strategy = MovingAverage()

    bot = Bot(exchange, datetime.utcnow(), config.interval, config.history)
    bot.trade(strategy, config.pair)
