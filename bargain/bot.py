import logging

from bargain.charts import emac_chart
from bargain.indicator import Signal


log = logging.getLogger(__name__)


class Bot:

    def __init__(self, dryrun, exchange, now, interval):
        self._dryrun = dryrun
        self._exchange = exchange
        self._now = now
        self._interval = interval

    def trade(self, indicator, pair, ratio):
        backtrack = self._dryrun + indicator.backtrack
        candles = self._exchange.get_candles(pair, self._interval, self._now, backtrack)
        signal = None

        for candle in candles:
            for signal in indicator.advance(candle):
                signal_time, signal_price = candle.time, candle.close
                log.debug('{2} {0} @ {1} {2}'.format(signal.name, signal_price, '#' * 14))

        if signal:
            past_trades = self._exchange.get_past_trades(pair, since=signal_time, until=self._now, limit=1)

            if past_trades and past_trades[-1].signal == signal:
                log.debug('Already traded since %s: %s', signal_time, past_trades[-1])
            else:
                order = self._order(pair, signal, ratio)
                if order: log.info(order)

        if self._dryrun:
            # TODO: Refactor
            emac_chart(candles, indicator._plot_ema_fast, indicator._plot_ema_slow)

    def _order(self, pair, signal, ratio):
        ticker = self._exchange.get_ticker(pair)
        balances = self._exchange.get_wallet_balances()

        if signal == Signal.BUY:
            price = ticker.ask
            max_amount = balances.get(pair[1], 0) * price
        elif signal == Signal.SELL:
            price = ticker.bid
            max_amount = balances.get(pair[0], 0)

        amount = max_amount * ratio

        log.info('%s %.5g %s for %.5g %s', signal.name, amount, pair[0].name, price, pair[1].name)
        if self._dryrun:
            log.info('Skipping order (dry run)')
            return

        return self._exchange.place_order(pair, signal, amount, price)
