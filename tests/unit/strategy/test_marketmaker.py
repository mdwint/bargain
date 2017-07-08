from datetime import timedelta

from bargain.currency import Currency
from bargain.exchange import Order
from bargain.strategy.marketmaker import MarketMaker


def test_marketmaker(exchange, now):
    pair = (Currency.ETH, Currency.USD)
    trade_amount = 0.1
    profit_pct = 10
    buydown_pct = 5

    pft = (100 + profit_pct) / 100
    bdn = (100 - buydown_pct) / 100

    exchange._balance[pair[1]] = 100
    exchange._set_price(pair, 50)
    exchange._set_price(pair, 50)

    strategy = MarketMaker(0, exchange, now, interval=timedelta(minutes=1))

    def trade():
        strategy.trade(pair, trade_amount, profit_pct, buydown_pct)

    def assert_past_trades(*args):
        assert exchange.get_past_trades(pair, now, now) == tuple(args)

    def assert_active_orders(*args):
        orders = exchange.get_active_orders(pair)
        assert orders == tuple(args)

        assert sum(1 for o in orders if o.is_buy) == 1
        assert sum(1 for o in orders if o.is_sell) >= 1

    buy1 = Order(pair, trade_amount, 50)
    sell1 = Order(pair, -trade_amount, 50 * pft)
    buydown1 = Order(pair, trade_amount, 50 * bdn)
    trade()

    # Executed buy
    assert_past_trades(buy1)
    assert_active_orders(sell1, buydown1)

    trade()

    # No changes
    assert_past_trades(buy1)
    assert_active_orders(sell1, buydown1)

    # Price went up
    exchange._set_price(pair, 50 * 1.11)
    buy2 = Order(pair, trade_amount, 50 * 1.11)
    sell2 = Order(pair, -trade_amount, 50 * 1.11 * pft)
    buydown2 = Order(pair, trade_amount, 50 * 1.11 * bdn)
    trade()

    # Executed sell
    assert_past_trades(buy1, sell1, buy2)
    assert_active_orders(sell2, buydown2)

    # Price went down
    exchange._set_price(pair, 50 * 1.10 * bdn)
    sell3 = Order(pair, -trade_amount, 50 * 1.11 * bdn * pft)
    buydown3 = Order(pair, trade_amount, 50 * 1.11 * bdn * bdn)
    trade()

    # Executed buydown
    assert_past_trades(buy1, sell1, buy2, buydown2)
    assert_active_orders(sell2, sell3, buydown3)
