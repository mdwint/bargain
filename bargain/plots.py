from collections import defaultdict
from datetime import datetime, timedelta, timezone
from operator import attrgetter
import os

import plotly.graph_objs as go
import plotly.plotly as py
import requests

from bargain.currency import Currency
from bargain.exchange.bitfinex import Bitfinex


def serverless_handler(event, context):
    exchange = Bitfinex(os.environ['BITFINEX_API_KEY'], os.environ['BITFINEX_API_SECRET'])
    py.sign_in(os.environ['PLOTLY_USERNAME'], os.environ['PLOTLY_API_KEY'])
    plot_all(exchange)


def round_to_minute(time):
    return time.replace(second=0, microsecond=0)


def get_conversion_rate(base, target):
    r = requests.get('https://api.fixer.io/latest', params={
        'base': base, 'symbols': target
    })

    r.raise_for_status()
    return r.json()['rates'][target]


class PriceHistory:

    def __init__(self, exchange, interval):
        self.exchange = exchange
        self.interval = interval
        self.batch_size = 1000
        self.cache = defaultdict(dict)

    def get(self, pair, time):
        cache = self.cache[pair]
        key = time - self.interval

        if cache is None:
            return 0

        if key not in cache:
            candles = self.exchange.get_candles(pair, self.interval, now=time + self.interval, limit=self.batch_size)

            if candles:
                cache.update({c.time: c.close for c in candles})
                cache[key] = candles[-1].close if candles else 0
            else:
                # Currency was not available yet
                self.cache[pair] = None
                return 0

        return cache[key]


class Portfolio:

    def __init__(self, exchange, prices, target):
        self.exchange = exchange
        self.prices = prices
        self.base = Currency.USD
        self.conversion_rate = get_conversion_rate(self.base.name, target)
        self.balances = exchange.get_wallet_balances()

    @property
    def pairs(self):
        return ((currency, self.base) for currency, balance in self.balances.items()
                if currency != self.base and balance > 0.001)

    def get_trades(self, since, until):
        trades = []

        for pair in self.pairs:
            trades.extend(self.exchange.get_past_trades(pair, since, until))

        return sorted(trades, key=attrgetter('timestamp'), reverse=True)

    def undo_trade(self, trade):
        a, b = trade.pair
        self.balances[a] -= trade.amount
        self.balances[b] += trade.cost

        c = a if trade.is_buy else b
        self.balances[c] += trade.fee

    def get_value(self, time):
        value = self.balances[self.base]

        for pair in self.pairs:
            amount = self.balances[pair[0]]
            price = self.prices.get(pair, time)
            value += amount * price

        return value * self.conversion_rate


def to_scatter(series, **kwargs):
    return go.Scatter(x=[x for x, _ in series],
                      y=[y for _, y in series],
                      **kwargs)


def plot_scatter(title, scatters, unit):
    layout = go.Layout(title=title, yaxis={
        'title': unit,
        'range': [-100, max(scatters[0].y) * 1.5],
    })

    data = go.Data(scatters)
    fig = go.Figure(data=data, layout=layout)

    filename = '-'.join(['bargain'] + title.split()).lower()
    url = py.plot(fig, filename=filename, auto_open=False)
    print(title + ': ' + url)


def plot_all(exchange, unit='EUR', history=timedelta(days=30), interval=timedelta(hours=1)):
    until = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    since = until - history

    prices = PriceHistory(exchange, interval)
    portfolio = Portfolio(exchange, prices, target=unit)
    trades = portfolio.get_trades(since, until)

    def plot_portfolio_value():
        values = [(until, portfolio.get_value(until))]
        buys = []
        sells = []

        for time in (until - interval * i for i in range(history // interval)):
            for trade in (t for t in trades if time <= round_to_minute(t.timestamp)):
                actions = buys if trade.is_buy else sells
                actions.append((trade.timestamp, abs(trade.cost)))

                portfolio.undo_trade(trade)
                trades.remove(trade)

            values.append((time, portfolio.get_value(time)))

        scatters = [
            to_scatter(values, name='Value', showlegend=False),
            to_scatter(buys, name='Buy', mode='markers', marker={'color': 'green'}),
            to_scatter(sells, name='Sell', mode='markers', marker={'color': 'red'}),
        ]

        plot_scatter('Portfolio value', scatters, unit)

    plot_portfolio_value()
