
def get_cache_key(instance, extra=None):
    """
    get current cachekey name  based on random generated shorten url
    (to be used in redis cache)
    """
    return '%s.%s.%s' % (instance.__class__.__name__, instance.short_url, extra) if extra else '%s.%s' % (instance.__class__.__name__, instance.short_url)
