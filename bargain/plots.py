from collections import defaultdict
from datetime import datetime, timedelta, timezone
from operator import attrgetter
import os

import plotly.graph_objs as go
import plotly.plotly as py

from bargain.currency import Currency
from bargain.exchange.bitfinex import Bitfinex


def serverless_handler(event, context):
    exchange = Bitfinex(os.environ['BITFINEX_API_KEY'], os.environ['BITFINEX_API_SECRET'])
    py.sign_in(os.environ['PLOTLY_USERNAME'], os.environ['PLOTLY_API_KEY'])
    plot_portfolio_value(exchange)


def round_to_minute(time):
    return time.replace(second=0, microsecond=0)


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
                for c in candles[-3:]:
                    print('%s: %s' % (c.time, c.close))
            else:
                # Currency was not available yet
                self.cache[pair] = None
                return 0

        return cache[key]


class Portfolio:

    def __init__(self, exchange, prices):
        self.exchange = exchange
        self.prices = prices
        self.balances = exchange.get_wallet_balances()
        self.target = Currency.USD

    @property
    def pairs(self):
        return ((currency, self.target) for currency, balance in self.balances.items()
                if currency != self.target and balance > 0.001)

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
        self.balances[c] += trade.fee_amount

    def get_value(self, time):
        value = self.balances[self.target]

        for pair in self.pairs:
            amount = self.balances[pair[0]]
            price = self.prices.get(pair, time)
            value += amount * price

        return value


def plot_portfolio_value(exchange, history=timedelta(days=30), interval=timedelta(hours=1)):
    until = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    since = until - history

    prices = PriceHistory(exchange, interval)
    portfolio = Portfolio(exchange, prices)
    trades = portfolio.get_trades(since, until)
    series = [(until, portfolio.get_value(until))]

    for time in (until - interval * i for i in range(history // interval)):
        if trades and time <= round_to_minute(trades[0].timestamp):
            portfolio.undo_trade(trades.pop(0))

        series.append((time, portfolio.get_value(time)))
        print('%s: %s' % series[-1])

    scatter = go.Scatter(x=[x for x, _ in series],
                         y=[y for _, y in series])

    data = go.Data([scatter])
    layout = go.Layout(title='Portfolio value', yaxis={
        'title': portfolio.target.name,
        'range': [0, max(scatter.y) * 1.5],
    })

    fig = go.Figure(data=data, layout=layout)
    url = py.plot(fig, filename='bargain', auto_open=False)
    print(url)
