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
