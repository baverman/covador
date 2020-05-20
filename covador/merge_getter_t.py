__async__getter = __await__getter = None


def merge_getter(sync_getters, async_getters):
    def getter(__async__getter, *args, **kwargs):
        result = [g(*args, **kwargs) for g in sync_getters]
        if async_getters:  # pragma: no py2 cover
            for g in async_getters:
                result.append(__await__getter(g(*args, **kwargs)))
        return result
    return getter
