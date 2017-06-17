import logging


log = logging.getLogger(__name__)


class Bot:

    def __init__(self, exchange, now, interval, history):
        self._exchange = exchange
        self._now = now
        self._interval = interval
        self._history = history

    def trade(self, strategy, pair):
        candles = self._exchange.get_candles(pair, self._interval, self._now, self._history)

        for candle in candles:
            log.debug(candle)

        # TODO
        signal = strategy.emit_signal(candles)
        log.info(signal.name)
