from datetime import datetime
import logging
import time


log = logging.getLogger(__name__)


def dt(ms):
    return datetime.fromtimestamp(ms / 1000)


def ms(time):
    return time.timestamp() * 1000


def retryable(max_attempts=2, wait=0):
    """This decorator adds a retry mechanism to a function.

    If the function raises an exception, it is caught,
    and the call is retried for a given number of attempts.
    Exceptions caught during the last attempt are reraised.

    Args:
        max_attempts: Maximum retry attempts.
        wait: Delay each retry for a given number of seconds.

    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except:
                    log.warning('Attempt %d failed! %s', attempt, func)
                    if attempt == max_attempts:
                        raise
                    elif wait:
                        time.sleep(wait)
        return wrapper
    return decorator
