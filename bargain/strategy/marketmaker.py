import logging

from bargain.exchange import Order
from bargain.strategy import Strategy


log = logging.getLogger(__name__)


class MarketMaker(Strategy):

    def __init__(self, exchange, now, interval):
        self._exchange = exchange
        self._now = now
        self._interval = interval

    def trade(self, pair, trade_amount, profit_margin, buydown_margin):
        price = self._exchange.get_ticker(pair).ask
        orders = self._exchange.get_active_orders(pair)

        sell_orders = [o for o in orders if o.is_sell]
        buy_orders = [o for o in orders if o.is_buy]

        if not sell_orders:
            # Place market buy order
            buy = self._exchange.place_order(Order(pair, trade_amount, price))
        elif not buy_orders:
            buy = self._get_last_buy(pair)
        else:
            buy = None

        if buy:
            # Place limit sell order
            self._exchange.place_order(Order(pair, -trade_amount, buy.price * (1 + profit_margin)))
            price = buy.price

        # (Re)place limit buydown order
        if buy_orders:
            self._exchange.cancel_orders(buy_orders)
        self._exchange.place_order(Order(pair, trade_amount, price * (1 - buydown_margin)))

    def _get_last_buy(self, pair):
        try:
            return [o for o in self._exchange.get_past_trades(pair) if o.is_buy][-1]
        except IndexError:
            raise ValueError('No last %s buy order found!' % pair)
