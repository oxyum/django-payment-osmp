
from django.conf.urls.defaults import *

from osmp.views import payment

urlpatterns = patterns('',
    url(r'^payment/$', payment, name='osmp-payment'),
)
