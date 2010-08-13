from django.contrib import admin
from osmp.models import Payment

class PaymentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_on'
    list_display = ['id', 'txn_id', 'txn_date', 'sum', 'account', 'created_on']
    list_filter = ['created_on']
    ordering = ['-created_on']
    search_fields = ['id', 'txn_id']

admin.site.register(Payment, PaymentAdmin)
