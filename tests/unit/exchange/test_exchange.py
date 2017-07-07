from bargain.currency import Currency


def test_orders(exchange):
    pair = (Currency.ETH, Currency.USD)
    trade_amount = 0.1

    def assert_balance(a, b):
        balance = exchange.get_wallet_balances()
        assert balance[pair[0]] == a
        assert balance[pair[1]] == b

    exchange._balance[pair[1]] = 100
    exchange.set_price(pair, 50)
    exchange.set_price(pair, 50)

    buy = exchange.place_order(pair, trade_amount)

    # executed buy
    assert_balance(0.1, 95)
    assert exchange.get_trades(pair) == (buy,)
    assert exchange.get_orders(pair) == ()

    sell = exchange.place_order(pair, -trade_amount, price=60)
    buydown = exchange.place_order(pair, trade_amount, price=45)

    # placed sell & buydown
    assert_balance(0, 90.5)
    assert exchange.get_trades(pair) == (buy,)
    assert exchange.get_orders(pair) == (sell, buydown)

    exchange.set_price(pair, 61)

    # executed sell
    assert_balance(0, 96.5)
    assert exchange.get_trades(pair) == (buy, sell)
    assert exchange.get_orders(pair) == (buydown,)

    exchange.set_price(pair, 43)

    # executed buydown
    assert_balance(0.1, 96.5)
    assert exchange.get_trades(pair) == (buy, sell, buydown)
    assert exchange.get_orders(pair) == ()
