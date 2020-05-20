import sys
import ast
import os.path

from covador.compat import COROUTINE, ASYNC_AWAIT, PY2

GEN_CACHE = {}


def get_fn_param(name):
    return name[len('__async__'):]


def get_await_param(name):
    return name[len('__await__'):]


class AsyncTransformer(ast.NodeTransformer):
    def __init__(self, params):
        self.params = params

    def visit_FunctionDef(self, node):
        args = node.args.args
        if PY2:  # pragma: no py3 cover
            first_arg_name = args and args[0].id
        else:  # pragma: no py2 cover
            first_arg_name = args and args[0].arg

        if first_arg_name and first_arg_name.startswith('__async__'):
            if self.params[get_fn_param(first_arg_name)]:  # pragma: no py2 cover
                if ASYNC_AWAIT:  # pragma: no coro cover
                    node = ast.AsyncFunctionDef(**vars(node))
                else:  # pragma: no async cover
                    node.decorator_list.append(ast.Name(id='coroutine', ctx=ast.Load(),
                                                        lineno=node.lineno-1, col_offset=node.col_offset))
            args.pop(0)
        return self.generic_visit(node)

    def visit_Call(self, node):
        if type(node.func) is ast.Name and node.func.id.startswith('__await__'):
            if self.params[get_await_param(node.func.id)]:  # pragma: no py2 cover
                if ASYNC_AWAIT:  # pragma: no coro cover
                    return ast.Await(value=node.args[0], lineno=node.lineno, col_offset=node.col_offset)
                else:  # pragma: no async cover
                    return ast.YieldFrom(value=node.args[0], lineno=node.lineno, col_offset=node.col_offset)
            else:
                return node.args[0]
        return self.generic_visit(node)


def get_ast(fname):
    with open(fname) as f:
        return ast.parse(f.read(), fname)


def transform(fname, params):
    tree = get_ast(fname)
    transformed = AsyncTransformer(params).visit(tree)
    if COROUTINE and not ASYNC_AWAIT:  # pragma: no cover
        transformed.body.insert(0, ast.ImportFrom(
            module='asyncio',
            lineno=1,
            col_offset=0,
            names=[ast.alias(name='coroutine', asname=None)]))

    return transformed


def execute(module, params):
    key = module, params
    try:
        return GEN_CACHE[key]
    except KeyError:
        pass

    parts = module.split('.')
    parts[-1] += '.py'

    fname = os.path.join(os.path.dirname(__file__), *parts[1:])
    tree = transform(fname, dict(params))
    code = compile(tree, fname, 'exec')
    ctx = {}
    exec(code, ctx, ctx)
    GEN_CACHE[key] = ctx
    return ctx


def import_module(module, params):
    ctx = execute(module, params)
    m = type(sys)(module)
    vars(m).update(ctx)
    m.params = params
    sys.modules[module] = m
    root, _, mname = module.partition('.')
    setattr(sys.modules[root], mname, m)
