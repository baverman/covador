from asyncio import coroutines


def mark_coro(fn):
    fn._is_coroutine = getattr(coroutines, '_is_coroutine', True)
    return fn
