from collections import namedtuple


Ticker = namedtuple('Ticker', 'bid, ask')
Trade = namedtuple('Trade', 'timestamp, signal, price, amount')


class Exchange:
    pass
