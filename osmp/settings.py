
from django.conf import settings


OSMP_IPS = getattr(settings, 'OSMP_IPS', ['79.142.16.0/20',])

OSMP_ACCOUNT_RE = getattr(settings, 'OSMP_ACCOUNT_RE', r'^[\w.@+-]+$',)
