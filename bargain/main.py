import argparse
import logging
import os
from datetime import datetime, timedelta, timezone

import ccxt
import yaml

from bargain.currency import Currency
from bargain.exchange.bitfinex import Bitfinex
from bargain.indicator import Indicator
from bargain.plots import plot_all
from bargain.strategy.marketmaker import MarketMaker
from bargain.strategy.technical import TechnicalTrader


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
    p.add_argument('--plot', action='store_true', help='Plot portfolio value over time')
    args = p.parse_args()

    with open(args.secrets) as f:
        secrets = yaml.safe_load(f)

    with open(args.schedule) as f:
        schedule = yaml.safe_load(f)

    exchange = ccxt.bitfinex(secrets['exchanges']['bitfinex'])

    if args.plot:
        plot_all(exchange)
    else:
        event = schedule['trades'][args.trade]['schedule']['input']
        main(exchange, event, args.debug, args.dryrun)


def main(exchange, event, debug=False, dryrun=0):
    log.setLevel(logging.DEBUG if debug else logging.INFO)

    now = datetime.now(timezone.utc)
    interval = timedelta(minutes=event['interval'])
    pair = tuple(Currency[s] for s in event['pair'])

    if 'market_maker' in event:
        m = event['market_maker']
        strategy = MarketMaker(dryrun, exchange, now, interval)
        strategy.trade(pair, m['trade_amount'], m['profit_pct'], m['buydown_pct'])
    elif 'indicator' in event:
        indicator = Indicator.from_args(event['indicator'])
        strategy = TechnicalTrader(dryrun, exchange, now, interval)
        strategy.trade(indicator, pair, event.get('trade_ratio', 1))
    else:
        raise ValueError('Invalid event: %s' % event)
