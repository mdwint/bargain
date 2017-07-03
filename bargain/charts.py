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


def show_chart(candles, *args):
    try:
        import matplotlib.pyplot as plt
        # from matplotlib.dates import DateFormatter, HourLocator
    except ImportError:
        log.warning('Rendering charts requires matplotlib (not installed)')
        return

    fig, ax = plt.subplots()
    # ax.xaxis.set_major_locator(HourLocator(interval=6))
    # ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    dates = [c.time for c in candles]

    plt.plot(dates, [c.close for c in candles])
    for indicator in args:
        plt.plot(dates, indicator.values)

    ax.xaxis_date()
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.show()
