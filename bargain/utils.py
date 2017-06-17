from datetime import datetime


def dt(ms):
    return datetime.fromtimestamp(ms / 1000)


def ms(time):
    return time.timestamp() * 1000
