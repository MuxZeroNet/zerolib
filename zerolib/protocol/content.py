from collections import namedtuple
from .sanitizer import check_regex, regex_btc, regex_handle

FileInfo = namedtuple('FileInfo', ['algo', 'digest', 'proof', 'size', 'optional'])


def recover_cert(user_btc, portal, name):
    """Recover the certificate from
    the user's Bitcoin address, the portal type and the user's handle."""

    user_btc = check_regex(user_btc, regex_btc)
    portal = check_regex(portal, regex_handle).lower()
    name = check_regex(name, regex_handle).lower()

    user_btc = bytes(user_btc, encoding='ascii')
    portal = bytes(portal, encoding='ascii')
    name = bytes(name, encoding='ascii')

    return user_btc + b'#' + portal + b'/' + name


__all__ = ['FileInfo', 'recover_cert']
