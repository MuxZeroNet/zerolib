import re
import string

def _escape(chars):
    return '\\' + '\\'.join(iter(chars))

regex_onion = '[a-zA-Z0-9]{16}'
regex_btc = '1[a-zA-Z0-9]{25,}'
regex_handle = '[a-zA-Z0-9_\\.\\-]{1,50}'
# regex_path = '[A-Za-z0-9_/%s-]+' % _escape('.()[]')

chars_path = frozenset(string.ascii_letters + string.digits + ' !#$(%&)+,-./=@[_]`{~}')

range_size = (0, 0xFFFFFFFFFF)
range_time = (0, 0xFFffFFffFFffFFff)


def check_types(value, t):
    if not isinstance(value, t):
        raise TypeError('Value should be %s, but not %s' % (repr(t), value.__class__.__name__))
    return value

def val_types(types):
    # make decorator
    def decorator(func):
        def f(value, *args):
            check_types(value, types)
            return func(value, *args)
        return f
    return decorator

@val_types((int, float, bytes))
def check_range(value, inclusive):
    lower, upper = inclusive

    predicate = False
    if (lower is not None) and (upper is not None):
        predicate = (lower <= value <= upper)
    elif lower is None:
        predicate = (value <= upper)
    elif upper is None:
        predicate = (lower <= value)

    if not predicate:
        raise ValueError('Value out of range [%r, %r]' % inclusive)
    else:
        return value

@val_types((str, bytes))
def check_length(value, strlen):
    if len(value) > strlen:
        raise ValueError('String is too long. It should be in %d characters' % strlen)
    return value

@val_types((str, bytes))
def check_regex(value, regex):
    if not(re.fullmatch(regex, value)):
        raise ValueError('Failed RegEx test %s' % repr(regex))
    return value

@val_types(bytes)
def check_path(path):
    u_path = check_length(path, 255).decode('ascii')
    u_path = u_path.replace('\\', '/').lstrip('/')
    if '..' in u_path:
        raise ValueError('.. in inner_path %s' % repr(u_path))
    for ch in u_path:
        if ch not in chars_path:
            raise ValueError('Invalid char %r in inner_path %r' % (ch, u_path))
    return u_path


def opt(key):
    return (key, True)

def _unpack_opt(keyopt):
    if isinstance(keyopt, tuple):
        return (bytes(keyopt[0], encoding='utf-8'), keyopt[1])
    else:
        return (bytes(keyopt, encoding='utf-8'), False)

def unpack_opt(func):
    def f(self, keyopt, *args):
        key, optional = _unpack_opt(keyopt)
        try:
            value = self.params[key]
        except KeyError as e:
            if optional:
                return None
            else:
                raise e
        return func(self, value, *args)
    return f


class Condition(object):
    __slots__ = ['params']

    def __init__(self, params):
        self.params = params

    @unpack_opt
    def as_type(self, v, t):
        return check_types(v, t)

    @unpack_opt
    def strlen(self, v, length):
        return check_length(v, length)

    @unpack_opt
    def range(self, v, inclusive):
        return check_range(v, inclusive)

    def time(self, keyopt):
        return self.range(keyopt, range_time)

    def as_size(self, keyopt):
        return self.range(keyopt, range_size)

    def port(self, keyopt):
        return self.range(keyopt, (0, 65535))

    @unpack_opt
    def regex(self, v, r):
        try:
            s = v.decode('ascii')
        except AttributeError as e:
            raise TypeError('A bytes object is required, not %s' % v.__class__.__name__) from e
        return check_regex(s, r)

    def btc(self, keyopt):
        return self.regex(keyopt, regex_btc)

    def handle(self, keyopt):
        return self.regex(keyopt, handle_btc)

    def onion(self, keyopt):
        return self.regex(keyopt, regex_onion)

    @unpack_opt
    def inner(self, v):
        return check_path(v)

__all__ = ()
