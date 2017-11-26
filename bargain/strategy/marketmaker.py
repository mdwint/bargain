import logging

from bargain.exchange import Order, to_symbol
from bargain.strategy import Strategy


log = logging.getLogger(__name__)


class MarketMaker(Strategy):

    def __init__(self, dryrun, exchange, now, interval):
        self._dryrun = dryrun
        self._exchange = exchange
        self._now = now
        self._interval = interval

    def trade(self, pair, trade_amount, profit_pct, buydown_pct):
        symbol = to_symbol(pair)
        orders = self._exchange.fetch_open_orders(symbol)
        sell_orders = [o for o in orders if o['side'] == 'sell']
        buy_orders = [o for o in orders if o['side'] == 'buy']

        profit_scl = (100 + profit_pct) / 100
        buydown_scl = (100 - buydown_pct) / 100

        def place_order(order, type='limit'):
            if self._dryrun:
                log.info('Skipping order (dry run): %s', order)
                return order
            log.info('Placing order: %s', order)
            return self._exchange.create_order(*order.to_ccxt(type))

        def cancel_orders(orders):
            if not orders:
                return
            if self._dryrun:
                log.info('Skipping cancel (dry run): %s', orders)
                return
            log.info('Cancel orders: %s', orders)
            for order in orders:
                self._exchange.cancel_order(orders['id'])

        def place_market_buy():
            buy = Order(pair, trade_amount)
            if self._dryrun:
                buy.price = self._exchange.fetch_ticker(symbol).ask
            return place_order(buy, type='market')

        def place_profit_sell(buy):
            sell = Order(pair, -buy['amount'], buy['price'] * profit_scl)
            sell_orders.append(sell)
            return place_order(sell)

        if not sell_orders:
            buy = place_market_buy()
            place_profit_sell(buy)
        elif not buy_orders:
            buy = self._get_last_buy(symbol) or place_market_buy()
            place_profit_sell(buy)

        min_sell_price = min(o.price for o in sell_orders)
        buydown = Order(pair, trade_amount, min_sell_price / profit_scl * buydown_scl)

        if buydown not in buy_orders:
            cancel_orders(buy_orders)
            place_order(buydown)

    def _get_last_buy(self, symbol):
        since = self._now - self._interval * 2
        trades = self._exchange.fetch_trades(symbol, since)
        log.debug('Past trades: %s', trades)

        try:
            return [t for t in trades if t['side'] == 'buy'][-1]
        except IndexError:
            return None
