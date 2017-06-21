import hmac
import json
import requests
from base64 import b64encode
from datetime import datetime

from bargain.charts import Candle
from bargain.currency import Currency
from bargain.exchange import Exchange, Ticker, Trade
from bargain.indicator import Signal
from bargain.utils import dt, ms


class Bitfinex(Exchange):

    _base = 'https://api.bitfinex.com'

    def __init__(self, api_key=None, api_secret=None):
        self._api_key = api_key
        self._api_secret = api_secret

    @staticmethod
    def _period(interval):
        return {
            60: '1m',
            300: '5m',
            900: '15m',
            1800: '30m',
            3600: '1h',
        }.get(interval.total_seconds())

    @staticmethod
    def _symbol(pair):
        return ''.join(c.name for c in pair)

    @staticmethod
    def _raise_or_return(r):
        try:
            r.raise_for_status()
        except:
            raise RuntimeError(r.text)
        return r.json()

    def _get(self, path, **kwargs):
        params = kwargs.pop('params', {})

        r = requests.get(self._base + path.format(**kwargs), params=params)
        return self._raise_or_return(r)

    def _signed_post(self, path, **kwargs):
        params = kwargs.pop('params', {})
        form = kwargs.pop('data', {})
        body = kwargs.pop('json', {})
        nonce = datetime.utcnow().timestamp()

        if path.startswith('/v1'):
            headers = self._sign_v1(path, form, nonce)
        elif path.startswith('/v2'):
            headers = self._sign_v2(path, body, nonce)
        else:
            raise ValueError('Invalid path: %s' % path)

        r = requests.post(self._base + path.format(**kwargs), params=params, data=form, json=body, headers=headers)
        return self._raise_or_return(r)

    def _sign_v1(self, path, form, nonce):
        body = {
            'request': path,
            'nonce': str(nonce)
        }

        body.update(form)
        payload = b64encode(json.dumps(body).encode('utf-8'))
        h = hmac.new(self._api_secret.encode('utf-8'), payload, 'sha384')

        return {
            'X-BFX-APIKEY': self._api_key,
            'X-BFX-PAYLOAD': payload,
            'X-BFX-SIGNATURE': h.hexdigest()
        }

    def _sign_v2(self, path, body, nonce):
        payload = '/api%s%s%s' % (path, nonce, json.dumps(body))
        h = hmac.new(self._api_secret.encode('utf-8'), payload.encode('utf-8'), 'sha384')

        return {
            'bfx-nonce': str(nonce),
            'bfx-apikey': self._api_key,
            'bfx-signature': h.hexdigest()
        }

    def get_candles(self, pair, interval, now, limit):
        history = interval * limit

        raw = self._get('/v2/candles/trade:{interval}:t{symbol}/hist',
                        interval=self._period(interval), symbol=self._symbol(pair),
                        params={'start': ms(now - history), 'end': ms(now), 'limit': limit, 'sort': 1})

        return [Candle(dt(c[0]), c[1], c[2], c[3], c[4], c[5]) for c in raw]

    def get_ticker(self, pair):
        raw = self._get('/v2/ticker/t{symbol}', symbol=self._symbol(pair))

        return Ticker(bid=raw[0], ask=raw[2])

    def get_past_trades(self, pair, since, until, limit):
        raw = self._signed_post('/v1/mytrades', data={
            'symbol': self._symbol(pair),
            'timestamp': str(since.timestamp()),
            'until': str(until.timestamp()),
            'limit_trades': limit
        })

        return [Trade(t['timestamp'], Signal[t['type'].upper()], t['price'], t['amount']) for t in raw]

    def get_wallet_balances(self):
        raw = self._signed_post('/v1/balances')
        return {Currency[b['currency'].upper()]: float(b['amount']) for b in raw}

    def place_order(self, pair, signal, amount, price):
        return self._signed_post('/v1/order/new', data={
            'exchange': 'bitfinex',
            'symbol': ''.join(s.name.lower() for s in pair),
            'side': signal.name.lower(),
            'amount': str(amount),
            'type': 'exchange limit',
            'price': str(price)
        })
