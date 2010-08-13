
from django import forms

from osmp.settings import OSMP_ACCOUNT_RE

COMMANDS = ('check','pay')

class PaymentIdForm(forms.Form):
    txn_id = forms.IntegerField()

class PaymentForm(PaymentIdForm):
    command = forms.ChoiceField(choices=[(x, x) for x in COMMANDS])
    sum = forms.DecimalField(max_digits=7, decimal_places=2)
    txn_date = forms.DateTimeField(input_formats=['%Y%m%d%H%M%S'])
    account = forms.RegexField(regex=OSMP_ACCOUNT_RE, max_length=50, min_length=1)
