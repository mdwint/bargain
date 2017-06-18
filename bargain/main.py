import argparse
import logging
from collections import namedtuple
from datetime import datetime, timedelta

import yaml

from bargain.bot import Bot
from bargain.exchange.bitfinex import Bitfinex
from bargain.currency import Currency
from bargain.strategy.ema import EMAC


logging.basicConfig()
log = logging.getLogger()


Config = namedtuple('Config', 'debug, dryrun, interval, now, pair, exchange, trade_ratio, strategy')


def serverless_handler(event, context):
    # TODO: Parse event
    config = Config(debug=True, dryrun=False, interval=timedelta(minutes=15),
                    now=datetime.utcnow(), pair=(Currency.XRP, Currency.USD),
                    exchange=Bitfinex(), strategy=EMAC(13, 49))
    main(config)


def cli_handler():
    p = argparse.ArgumentParser('bargain')
    p.add_argument('--debug', action='store_true', help='Show debug output')
    p.add_argument('--dryrun', metavar='N', type=int, default=0, help='Dry run over N intervals')
    p.add_argument('--secrets', metavar='PATH', default='secrets.yml', help='Path to secrets.yml')
    p.add_argument('--pair', metavar='SYMBOL', nargs=2, type=lambda s: Currency[s.upper()], required=True, help='Currency pair to trade')
    p.add_argument('--ratio', type=float, default=0.95, help='Ratio to trade between currencies')
    args = p.parse_args()

    with open(args.secrets) as f:
        secrets = yaml.safe_load(f)

    exchange = Bitfinex(**secrets['exchanges']['bitfinex'])
    interval = timedelta(minutes=5)
    strategy = EMAC(13, 49)

    config = Config(debug=args.debug, dryrun=args.dryrun,
                    interval=interval, now=datetime.utcnow(), exchange=exchange,
                    pair=args.pair, trade_ratio=args.ratio, strategy=strategy)
    main(config)


def main(config):
    log.setLevel(logging.DEBUG if config.debug else logging.INFO)

    bot = Bot(config.dryrun, config.exchange, config.now, config.interval)
    bot.trade(config.strategy, config.pair, config.trade_ratio)
