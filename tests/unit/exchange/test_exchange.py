from bargain.currency import Currency
from bargain.exchange import Order


def test_orders(exchange, now):
    pair = (Currency.ETH, Currency.USD)
    trade_amount = 0.1

    def assert_balance(a, b):
        balance = exchange.get_wallet_balances()
        assert balance[pair[0]] == a
        assert balance[pair[1]] == b

    exchange._balance[pair[1]] = 100
    exchange._set_price(pair, 50)
    exchange._set_price(pair, 50)

    buy = exchange.place_order(Order(pair, trade_amount, 50))

    # Executed buy
    assert_balance(0.1, 95)
    assert exchange.get_past_trades(pair, now, now) == (buy,)
    assert exchange.get_active_orders(pair) == ()

    sell = exchange.place_order(Order(pair, -trade_amount, price=60))
    buydown = exchange.place_order(Order(pair, trade_amount, price=45))

    # Placed sell & buydown
    assert_balance(0, 90.5)
    assert exchange.get_past_trades(pair, now, now) == (buy,)
    assert exchange.get_active_orders(pair) == (sell, buydown)

    exchange._set_price(pair, 61)

    # Executed sell
    assert_balance(0, 96.5)
    assert exchange.get_past_trades(pair, now, now) == (buy, sell)
    assert exchange.get_active_orders(pair) == (buydown,)

    exchange._set_price(pair, 43)

    # Executed buydown
    assert_balance(0.1, 96.5)
    assert exchange.get_past_trades(pair, now, now) == (buy, sell, buydown)
    assert exchange.get_active_orders(pair) == ()
