import logging

from bargain.strategy import Strategy


log = logging.getLogger(__name__)


class MarketMaker(Strategy):

    def __init__(self, exchange, now, interval):
        self._exchange = exchange
        self._now = now
        self._interval = interval

    def trade(self, pair, trade_amount, profit_margin, buydown_margin):
        price = self._exchange.get_price(pair)
        orders = self._exchange.get_orders(pair)

        sell_orders = [o for o in orders if o.is_sell]
        buy_orders = [o for o in orders if o.is_buy]
        buy = None

        if not sell_orders:
            # Place market buy order
            buy = self._exchange.place_order(pair, trade_amount, price)
        elif not buy_orders:
            buy = self._get_last_buy_order(pair)
        else:
            self._exchange.cancel_orders(buy_orders)

        if buy:
            # Place limit sell order
            self._exchange.place_order(pair, -trade_amount, buy.price * (1 + profit_margin))
            price = buy.price

        # Place limit buydown order
        self._exchange.place_order(pair, trade_amount, price * (1 - buydown_margin))

    def _get_last_buy_order(self, pair):
        try:
            return next(reversed(o for o in self._exchange.get_trades(pair) if o.is_buy))
        except StopIteration:
            raise ValueError('No last %s buy order found!' % pair)
