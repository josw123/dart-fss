import datetime
import functools

# Default Time-To-Live
CACHE_DEFAULT_TTL = datetime.timedelta(hours=1)


def cache(ttl=CACHE_DEFAULT_TTL):
    """ TTL Cache Decorator

    Parameters
    ----------
    ttl: datetime.timedelta
        Time-To-Live

    Returns
    -------
    function
        Wrapped Function
    """
    def wrap(func):
        cached = {}

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            now = datetime.datetime.now()
            # see lru_cache for fancier alternatives
            key = tuple(args), frozenset(kwargs.items())
            if key not in cached or now - cached[key][0] > ttl:
                value = func(*args, **kwargs)
                cached[key] = (now, value)
            return cached[key][1]
        return wrapped
    return wrap
