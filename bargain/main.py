import argparse
import logging
from collections import namedtuple
from datetime import datetime, timedelta

from bargain.bot import Bot
from bargain.exchange.bitfinex import Bitfinex
from bargain.currency import Currency
from bargain.strategy.ema import EMAC


logging.basicConfig()
log = logging.getLogger()


Config = namedtuple('Config', 'debug, chart, interval, backtrack, now, pair, exchange, strategy')


def serverless_handler(event, context):
    # TODO: Parse event
    config = Config(debug=True, interval=timedelta(minutes=15), backtrack=1,
                    now=datetime.utcnow(), pair=(Currency.XRP, Currency.USD),
                    exchange=Bitfinex(), strategy=EMAC(13, 49), chart=False)
    main(config)


def cli_handler():
    p = argparse.ArgumentParser('bargain')
    p.add_argument('--debug', action='store_true', help='Show debug output')
    p.add_argument('--chart', action='store_true', help='Show chart')
    p.add_argument('--backtrack', type=int, default=0, help='Number of intervals to backtrack')
    args = p.parse_args()

    # TODO: Parse CLI arguments
    config = Config(debug=args.debug, chart=args.chart, backtrack=args.backtrack,
                    interval=timedelta(minutes=5), now=datetime.utcnow(),
                    pair=(Currency.ETH, Currency.USD), exchange=Bitfinex(),
                    strategy=EMAC(13, 49))
    main(config)


def main(config):
    log.setLevel(logging.DEBUG if config.debug else logging.INFO)

    bot = Bot(config.exchange, config.now, config.interval, config.backtrack)
    bot.trade(config.strategy, config.pair, config.chart)
