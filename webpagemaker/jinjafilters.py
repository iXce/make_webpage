# coding: utf-8
from collections import defaultdict

from jinja2 import environmentfilter
from jinja2.utils import soft_unicode


@environmentfilter
def inc_filter(env, key, value=1, result='value', reset=False):
    """
    Count ocurrences of key.
    Stores the counter on Jinja's environment.
        >>> class Env: pass
        >>> env = Env()
        >>> inc_filter(env, 'x')
        1
        >>> inc_filter(env, 'x')
        2
        >>> inc_filter(env, 'y')
        1
        >>> inc_filter(env, 'x')
        3
        >>> inc_filter(env, 'x', reset=True)
        1
        >>> inc_filter(env, 'x')
        2
        >>> inc_filter(env, 'x', value=0, reset=True)
        0
        >>> inc_filter(env, 'x', result=None)
        >>> inc_filter(env, 'x', result=False)
        u''
        >>> inc_filter(env, 'x', result='key')
        'x'
        >>> inc_filter(env, 'x')
        4
    """
    if not hasattr(env, 'counters'):
        env.counters = defaultdict(int)

    if reset:
        env.counters[key] = 0

    env.counters[key] += value

    if result == 'key':
        return key
    elif result == 'value':
        return env.counters[key]
    elif result is None:
        return None
    else:
        return soft_unicode('')


# Module doctest
if __name__ == '__main__':
    import doctest
    doctest.testmod()
