import logging


log = logging.getLogger(__name__)


class Candle:

    def __init__(self, time, open, close, high, low, volume):
        self.time = time
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume

    def __repr__(self):
        return '{time} [O={open:.2f}] [C={close:.2f}] [H={high:.2f}] [L={low:.2f}]'.format(
            time=self.time.strftime('%Y-%m-%d %H:%M'), open=self.open, close=self.close, high=self.high, low=self.low)


def emac_chart(candles, ema_fast, ema_slow):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        log.warning('Rendering charts requires matplotlib (not installed)')
        return

    fig, ax = plt.subplots()
    plt.plot([c.close for c in candles])
    plt.plot(ema_slow)
    plt.plot(ema_fast)
    plt.show()
