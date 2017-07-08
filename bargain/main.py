import argparse
import logging
import os
from datetime import datetime, timedelta, timezone

import yaml

from bargain.exchange.bitfinex import Bitfinex
from bargain.currency import Currency
from bargain.strategy.marketmaker import MarketMaker


logging.basicConfig()
log = logging.getLogger()


def serverless_handler(event, context):
    exchange = Bitfinex(os.environ['BITFINEX_API_KEY'], os.environ['BITFINEX_API_SECRET'])
    main(exchange, event)


def cli_handler():
    p = argparse.ArgumentParser('bargain')
    p.add_argument('--debug', action='store_true', help='Show debug output')
    p.add_argument('--dryrun', metavar='N', type=int, default=0, help='Dry run over N intervals')
    p.add_argument('--secrets', metavar='PATH', default=os.path.join('config', 'secrets.yml'), help='Path to secrets.yml')
    p.add_argument('--schedule', metavar='PATH', default=os.path.join('config', 'schedule.yml'), help='Path to schedule.yml')
    p.add_argument('--trade', metavar='I', type=int, default=0, help='Index of trade in schedule.yml')
    args = p.parse_args()

    with open(args.secrets) as f:
        secrets = yaml.safe_load(f)

    with open(args.schedule) as f:
        schedule = yaml.safe_load(f)

    exchange = Bitfinex(**secrets['exchanges']['bitfinex'])
    event = schedule['trades'][args.trade]['schedule']['input']

    main(exchange, event, args.debug, args.dryrun)


def main(exchange, event, debug=False, dryrun=0):
    log.setLevel(logging.DEBUG if debug else logging.INFO)

    now = datetime.now(timezone.utc)
    interval = timedelta(minutes=event['interval'])

    pair = tuple(Currency[s] for s in event['pair'])
    m = event['market_maker']

    strategy = MarketMaker(dryrun, exchange, now, interval)
    strategy.trade(pair, m['trade_amount'], m['profit_pct'], m['buydown_pct'])
