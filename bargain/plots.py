from datetime import datetime, timedelta, timezone
from operator import attrgetter

import plotly
import plotly.plotly as py
import plotly.graph_objs as go

from bargain.currency import Currency


def plot_wallet_balance(exchange, pairs, secrets, currency=Currency.USD, history=timedelta(days=28)):
    plotly.tools.set_credentials_file(**secrets)
    now = datetime.now(timezone.utc)
    since = now - history

    balances = exchange.get_wallet_balances()
    series = [(now, balances[currency])]

    trades = []
    for pair in pairs:
        trades.extend(exchange.get_past_trades(pair, since, now))

    for t in sorted(trades, key=attrgetter('timestamp'), reverse=True):
        a, b = t.pair
        balances[a] -= t.amount
        balances[b] += t.cost

        f = a if t.is_buy else b
        balances[f] += t.fee_amount

        series.append((t.timestamp, balances[currency]))

    scatter = go.Scatter(x=[x for x, _ in series],
                         y=[y for _, y in series])

    data = go.Data([scatter])
    layout = go.Layout(yaxis={'title': currency.name})
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='bargain')
