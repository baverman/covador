from ast import iter_fields, Store, Load
iteritems = dict.items


def dumptree(node, result, level):
    LW = '   '
    fields = [(k, v)
              for k, v in iter_fields(node)
              if (hasattr(v, '_fields') and not isinstance(v, Store) and not isinstance(v, Load)) or
                 (isinstance(v, list) and v and hasattr(v[0], '_fields'))]
    field_names = set(k for k, _ in fields)

    result.append('{} {} {}'.format(
        LW * level,
        type(node).__name__,
        ', '.join('{}: {}'.format(k, v)
                  for k, v in sorted(iteritems(vars(node)))
                  if k not in field_names)))

    for k, v in fields:
        if isinstance(v, list):
            result.append('{} {}[]: '.format(LW * (level + 1), k))
            for child in v:
                dumptree(child, result, level + 2)
        else:
            result.append('{} {}:'.format(LW * (level + 1), k))
            dumptree(v, result, level + 2)

    return result


def dump(node):
    return '\n'.join(dumptree(node, [], 0))


def print_dump(node):
    print(dump(node))
