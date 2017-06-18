import hmac
import json
import requests
from datetime import datetime

from bargain.charts import Candle
from bargain.exchange import Exchange
from bargain.utils import dt, ms


class Bitfinex(Exchange):

    _base = 'https://api.bitfinex.com/v2'

    def __init__(self, api_key, api_secret):
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

    def _get(self, path, **kwargs):
        params = kwargs.pop('params', {})

        r = requests.get(self._base + path.format(**kwargs), params=params)
        r.raise_for_status()
        return r.json()

    def _signed_post(self, path, **kwargs):
        params = kwargs.pop('params', {})
        body = kwargs.pop('json', {})
        headers = self._signature_headers(path, body)

        r = requests.post(self._base + path.format(**kwargs), params=params, json=body, headers=headers)
        r.raise_for_status()
        return r.json()

    def _signature_headers(self, path, body, nonce=datetime.utcnow().timestamp()):
        msg = '/api/v2/%s%s%s' % (path.lstrip('/'), nonce, json.dumps(body))
        h = hmac.new(self._api_secret.encode('utf-8'), msg.encode('utf-8'), 'sha384')

        return {
            'Content-Type': 'application/json',
            'bfx-nonce': str(nonce),
            'bfx-apikey': self._api_key,
            'bfx-signature': h.hexdigest()
        }

    def get_candles(self, pair, interval, now, limit):
        history = interval * limit

        raw = self._get('/candles/trade:{interval}:t{symbol_from}{symbol_to}/hist',
                        interval=self._period(interval), symbol_from=pair[0].name, symbol_to=pair[1].name,
                        params={'start': ms(now - history), 'end': ms(now), 'limit': limit, 'sort': 1})

        return [Candle(dt(c[0]), c[1], c[2], c[3], c[4], c[5]) for c in raw]

    def get_orders(self):
        return self._signed_post('/auth/r/orders')
