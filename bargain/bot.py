import logging
from functools import partial


log = logging.getLogger(__name__)


class Bot:

    def __init__(self, exchange, now, interval, history):
        self._exchange = exchange
        self._now = now
        self._interval = interval
        self._history = history

    def trade(self, strategy, pair):
        get_candles = partial(self._exchange.get_candles, pair, self._interval, self._now)

        signal = strategy.emit_signal(get_candles)
        log.info('%s signal emitted' % (signal.name if signal else 'No'))
