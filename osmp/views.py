# -*- mode: python; coding: utf-8; -*-

from ipaddr import IPv4Address, IPv4Network
from xml.etree import ElementTree as ET

from osmp.settings import OSMP_IPS

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_GET
from django.contrib.auth.models import User

from osmp.forms import PaymentIdForm, PaymentForm
from osmp.models import Payment
from osmp.signals import payment_accepted

def check_ip_in_range(ip, range):
    ip = IPv4Address(ip).ip
    for net in range:
        net = IPv4Network(net)
        if (ip == net.network) or ((ip > net.network) and (ip < net.broadcast)):
            return True
    return False

def xml_response(osmp_txn_id, result, sum=None, prv_txn=None, comment=None):
    response = ET.Element('response')

    xml_osmp_txn_id = ET.SubElement(response, 'osmp_txn_id')
    xml_osmp_txn_id.text = str(osmp_txn_id)

    xml_sum = ET.SubElement(response, 'sum')
    xml_sum.text = str(sum)

    xml_result = ET.SubElement(response, 'result')
    xml_result.text = str(result)

    if prv_txn is not None:
        xml_prv_txn = ET.SubElement(response, 'prv_txn')
        xml_prv_txn.text = str(prv_txn)

    if comment is not None:
        xml_comment = ET.SubElement(response, 'comment')
        xml_comment.text = unicode(comment)

    return ET.tostring(response, 'utf-8')

@require_GET
def payment(request):
    if not check_ip_in_range(request.META["REMOTE_IP"], OSMP_IPS):
        return HttpResponseForbidden()

    idform = PaymentIdForm(request.GET)
    if idform.is_valid():
        form = PaymentForm(request.GET)
        if form.is_valid():
            try:
                payment = Payment.objects.get(txn_id=idform.cleaned_data['txn_id'])
                return HttpResponse(xml_response(payment.txn_id, 0, payment.sum, prv_txn=payment.id))
            except Payment.DoesNotExist:
                pass

            try:
                user = User.objects.get(username=form.cleaned_data['account'])
            except User.DoesNotExist:
                # return error code 5 (Идентификатор абонента не найден)
                return HttpResponse(xml_response(idform.cleaned_data['txn_id'], 5))

            if not user.is_active:
                # return error code 79 (Счёт абонента не активен)
                return HttpResponse(xml_response(idform.cleaned_data['txn_id'], 79))

            if form.cleaned_data['command'] == 'check':
                # return error code 0 (OK)
                return HttpResponse(xml_response(idform.cleaned_data['txn_id'], 0))
            elif form.cleaned_data['command'] == 'pay':
                payment = Payment.objects.create(
                    txn_id = form.cleaned_data['txn_id'],
                    sum = form.cleaned_data['sum'],
                    txn_date = form.cleaned_data['txn_date'],
                    account = form.cleaned_data['account'],
                    )
                payment_accepted.send(sender=payment.__class__, payment=payment)

                # return error code 0 (OK)
                return HttpResponse(xml_response(payment.txn_id, 0, payment.sum, prv_txn=payment.id))

        elif form.errors.has_key('account'):
            # return error code 4 (Неверный формат идентификатора абонента)
            return HttpResponse(xml_response(idform.cleaned_data['txn_id'], 4))

        # return error code 300 (Другая ошибка провайдера)
        return HttpResponse(xml_response(idform.cleaned_data['txn_id'], 300))

    return HttpResponseBadRequest("Unknown error.")
