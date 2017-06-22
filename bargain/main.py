import argparse
import logging
import os
from collections import namedtuple
from datetime import datetime, timedelta, timezone

import yaml

from bargain.bot import Bot
from bargain.exchange.bitfinex import Bitfinex
from bargain.currency import Currency
from bargain.indicator.ema import EMAC


logging.basicConfig()
log = logging.getLogger()


Config = namedtuple('Config', 'debug, dryrun, interval, now, pair, exchange, trade_ratio, indicator')


def serverless_handler(event, context):
    exchange = Bitfinex(os.environ['BITFINEX_API_KEY'], os.environ['BITFINEX_API_SECRET'])
    pair = (Currency[event['pair'][0]], Currency[event['pair'][1]])

    interval = timedelta(minutes=event['interval'])
    trade_ratio = event.get('trade_ratio', 1)
    indicator = EMAC(**event['indicator']['emac'])

    config = Config(debug=False, dryrun=0, now=datetime.now(timezone.utc),
                    interval=interval, exchange=exchange, pair=pair,
                    trade_ratio=trade_ratio, indicator=indicator)
    main(config)


def cli_handler():
    p = argparse.ArgumentParser('bargain')
    p.add_argument('--debug', action='store_true', help='Show debug output')
    p.add_argument('--dryrun', metavar='N', type=int, default=0, help='Dry run over N intervals')
    p.add_argument('--secrets', metavar='PATH', default=os.path.join('config', 'secrets.yml'), help='Path to secrets.yml')
    p.add_argument('--pair', metavar='SYMBOL', nargs=2, type=lambda s: Currency[s.upper()], required=True, help='Currency pair to trade')
    p.add_argument('--interval', type=int, default=5, help='Trading interval in minutes')
    p.add_argument('--ratio', type=float, default=1, help='Ratio to trade between currencies')
    p.add_argument('--emac-fast', type=int, default=13, help='Length of the short-term moving average')
    p.add_argument('--emac-slow', type=int, default=49, help='Length of the long-term moving average')
    args = p.parse_args()

    with open(args.secrets) as f:
        secrets = yaml.safe_load(f)

    exchange = Bitfinex(**secrets['exchanges']['bitfinex'])
    interval = timedelta(minutes=args.interval)
    indicator = EMAC(args.emac_fast, args.emac_slow)

    config = Config(debug=args.debug, dryrun=args.dryrun, now=datetime.now(timezone.utc),
                    interval=interval, exchange=exchange, pair=args.pair,
                    trade_ratio=args.ratio, indicator=indicator)
    main(config)


def main(config):
    log.setLevel(logging.DEBUG if config.debug else logging.INFO)

    bot = Bot(config.dryrun, config.exchange, config.now, config.interval)
    bot.trade(config.indicator, config.pair, config.trade_ratio)
