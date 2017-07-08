import logging

from bargain.exchange import Order
from bargain.strategy import Strategy


log = logging.getLogger(__name__)


class MarketMaker(Strategy):

    def __init__(self, dryrun, exchange, now, interval):
        self._dryrun = dryrun
        self._exchange = exchange
        self._now = now
        self._interval = interval

    def trade(self, pair, trade_amount, profit_pct, buydown_pct):
        orders = self._exchange.get_active_orders(pair)
        price = self._exchange.get_ticker(pair).ask

        sell_orders = [o for o in orders if o.is_sell]
        buy_orders = [o for o in orders if o.is_buy]

        cancel_orders = []
        new_orders = []

        def place_order(*args, **kwargs):
            order = Order(*args, **kwargs)
            new_orders.append(order)
            return order

        def place_market_buy():
            return place_order(pair, trade_amount, price)

        if not sell_orders:
            buy = place_market_buy()
        elif not buy_orders:
            buy = self._get_last_buy(pair) or place_market_buy()
        else:
            buy = None

        if buy:
            # Place sell limit order with profit
            place_order(pair, -trade_amount, buy.price * ((100 + profit_pct) / 100))
            price = buy.price

        # (Re)place buydown limit order to maintain straddle
        cancel_orders.extend(buy_orders)
        place_order(pair, trade_amount, price * ((100 - buydown_pct) / 100))

        if cancel_orders:
            log.info('Cancel orders: %s', cancel_orders)
        log.info('Place orders: %s', new_orders)

        if self._dryrun:
            log.info('Skipping orders (dry run)')
            return

        if cancel_orders:
            self._exchange.cancel_orders(cancel_orders)

        for order in new_orders:
            self._exchange.place_order(order)

    def _get_last_buy(self, pair):
        until = self._now
        since = until - self._interval * 2
        past_trades = self._exchange.get_past_trades(pair, since, until)
        log.debug('Past trades: %s', past_trades)

        try:
            return [t for t in past_trades if t.is_buy][-1]
        except IndexError:
            return None
