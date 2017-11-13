import re

def _escape(chars):
    return '\\' + '\\'.join(iter(chars))

regex_onion = '[a-zA-Z0-9]{16}'
regex_btc = '1[a-zA-Z0-9]{25,}'
regex_handle = '[a-zA-Z0-9_\\.\\-]{1,50}'
regex_path = '[A-Za-z0-9_/%s-]+' % _escape('.()[]')

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
    if (lower is not None) and (value < lower):
        raise ValueError('Value is too small. It should be in range%s' % repr(inclusive))
    if (upper is not None) and (value > upper):
        raise ValueError('Value is too big. It should be in range%s' % repr(inclusive))
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
    u_path = check_regex(u_path.replace('\\', '/'), regex_path)
    u_path = u_path.lstrip('/')
    if '..' in u_path:
        raise ValueError('.. in inner_path %s' % repr(u_path))
    return u_path


def accept_opt(func):
    def newf(value, opt, *args):
        if opt and (value is None):
            return None
        else:
            return func(value, *args)

    return newf

opt_check_types = accept_opt(check_types)
opt_check_range = accept_opt(check_range)
opt_check_length = accept_opt(check_length)
opt_check_regex = accept_opt(check_regex)
opt_check_path = accept_opt(check_path)


def opt(key):
    return (key, True)

def _unpack_opt(keyopt):
    if isinstance(keyopt, tuple):
        return (bytes(keyopt[0], encoding='utf-8'), keyopt[1])
    else:
        return (bytes(keyopt, encoding='utf-8'), False)

def unpack_opt(func):
    def f(self, keyopt, *args):
        k, o = _unpack_opt(keyopt)
        return func(self, k, o, *args)
    return f


class Condition(object):
    __slots__ = ['params']

    def __init__(self, params):
        self.params = params

    @unpack_opt
    def as_type(self, k, o, t):
        return opt_check_types(self.params.get(k), o, t)

    @unpack_opt
    def strlen(self, k, o, length):
        return opt_check_length(self.params.get(k), o, length)

    @unpack_opt
    def range(self, k, o, inclusive):
        return opt_check_range(self.params.get(k), o, inclusive)

    def time(self, keyopt):
        return self.range(keyopt, range_time)

    def as_size(self, keyopt):
        return self.range(keyopt, range_size)

    def port(self, keyopt):
        return self.range(keyopt, (0, 65535))

    @unpack_opt
    def regex(self, k, o, r):
        s = self.params.get(k)
        try:
            s = s.decode('ascii')
        except AttributeError as e:
            raise TypeError('A bytes object is required, not %s' % s.__class__.__name__) from e
        return opt_check_regex(s, o, r)

    def btc(self, keyopt):
        return self.regex(keyopt, regex_btc)

    def handle(self, keyopt):
        return self.regex(keyopt, handle_btc)

    def onion(self, keyopt):
        return self.regex(keyopt, regex_onion)

    @unpack_opt
    def inner(self, k, o):
        return opt_check_path(self.params.get(k), o)


def is_regex_subset(regex_str):
    raise NotImplementedError()

__all__ = ['is_regex_subset']
