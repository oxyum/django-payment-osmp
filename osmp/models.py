
from datetime import datetime, timedelta
from time import sleep

from django.core.exceptions import ObjectDoesNotExist

import signals

class Payment(models.Model):
    txn_id = models.PositiveIntegerField(unique=True, db_index=True)
    sum = models.DecimalField(decimal_places=2, max_digits=7)
    txn_date = models.DateTimeField()
    account = models.CharField(max_length=50)

    created_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return "%s - %s (%s)" % (self.txn_id, self.sum, self.account)
