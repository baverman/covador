from covador.utils import parse_qs

__async__fn = __await__fn = None


def listdict(mdict):
    result = {}
    for k, v in mdict.items():
        result.setdefault(k, []).append(v)
    return result


def get_form(__async__fn, request):
    try:
        return request._covador_form
    except AttributeError:
        if request.content_type.startswith('multipart/form-data'):
            form = listdict(__await__fn(request.post()))
        elif request.content_type.startswith('application/x-www-form-urlencoded'):
            form = parse_qs(__await__fn(request.read()))
        else:
            form = {}
        form = request._covador_form = form
        return form


def get_json(__async__fn, request):
    if request.content_type.startswith('application/json'):
        return __await__fn(request.json())
    return {}
