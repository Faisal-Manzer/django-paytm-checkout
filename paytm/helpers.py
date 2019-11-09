__all__ = [
    'absolute_reverse',
    'generate_hash', 'sha256'
]
import hashlib

from django.shortcuts import reverse
from django.conf import settings


def absolute_reverse(request, *args, **kwargs):
    return "{}://{}{}".format(request.scheme, request.get_host(), reverse(*args, **kwargs))


def generate_hash(algorithm, string, salt=settings.SECRET_KEY):
    """Will generate hash for any of the function"""

    sb = f'{string} {salt}'.encode('utf-8')
    return getattr(hashlib, algorithm)(sb).hexdigest()


def sha256(string):
    return generate_hash('sha256', string)
