__all__ = [
    'GenericInitiatePaymentView', 'InitiatePaymentView',
    'GenericValidateCheckoutView', 'VerifyCheckoutView',
    'StatusCheckView'
]
from math import ceil
from random import randint

from django.shortcuts import render, Http404, reverse, get_object_or_404
from django.utils.timezone import datetime
from django.conf import settings as django_settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http.response import HttpResponseRedirect
from django.views import View

from paytm import conf as paytm_conf, Checksum
from paytm.models import Order, Item
from paytm.helpers import sha256, absolute_reverse


class GenericInitiatePaymentView(View):
    """
    create_order
        get_user -> get_customer_id
        -> get_amount
            (include_extra_tax -> get_paytm_charge -> get_gst_rate)
        -> get_channel -> get_mobile -> get_email -> get_notes

    get_payload
        get_merchant_credentials -> get_order_details
        -> restrict_mode
            (get_payment_type -> get_auth_mode)
        -> generate_checksumhash -> get_callback_url
    """
    conf = paytm_conf
    order_model = Order

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = None
        self._user = None
        self._customer_id = None
        self._amount = 0
        self._channel = 'WEB'
        self._payload = dict()
        self._checksumhash = ''

    def get_merchant_credentials(self):
        """
        :return: dict({
            MID
            WEBSITE
            INDUSTRY_TYPE_ID
        })
        """

        return self.conf.merchant_credentials

    def get_channel(self):
        """
        Hook for getting Channel of request
        It only can be either "WEB" or "WAP"

        :return: str(3)
        """

        if self.channel == 'WEB':
            return self.conf.CHANNEL_WEBSITE
        elif self.channel == 'WAP':
            return self.conf.CHANNEL_MOBILE_APP

        raise ValueError(
            'Channel can\'t be any other than "WEB" or "WAP", channel got is {}'.format(self.channel)
        )

    def get_user(self):
        """

        :return: None | user
        """
        if not self.request.user.is_anonymous:
            return self.request.user

    def create_order(self):
        self._user = self.get_user()
        self._customer_id = self.get_customer_id()
        self._amount = self.amount
        self._channel = self.get_channel()

        return self.order_model.create(
            user=self._user,
            customer_id=self._customer_id,
            real_amount=self._amount,
            amount=self.get_amount(),
            channel=self._channel,

            mobile=self.get_user_mobile(),
            email=self.get_user_email(),
            notes=self.add_note()
        )

    def get_order_id(self):
        """This has to be called after create_order"""
        return self.order.order_id

    def get_customer_id(self):
        if self._user:
            return str(self._user.id)

        return sha256(f'{datetime.now()} {randint(1, 100)}')[:80]

    def get_amount(self):
        """

        :return: float()
        """
        raise NotImplemented()

    @property
    def amount(self):
        amount = self.get_amount()
        if self.include_payment_charge:
            amount = amount * 10 ** 4 / (10 ** 4 - 82 * self.conf.TRANSACTION_CHARGE)

        return ceil(amount * 100) / 100

    def get_user_mobile(self):
        pass

    def get_user_email(self):
        pass

    def add_note(self):
        pass

    def get_callback_url(self):
        return absolute_reverse(self.request, 'paytm:checkout:validate')

    def get_payload(self):
        paytm_params = {
            **self.get_merchant_credentials(),
            'CHANNEL_ID': self.channel,
            'WEBSITE': paytm_conf.WEBSITE,
            'ORDER_ID': self.get_order_id(),
            'CUST_ID': self.get_customer_id(),
            'TXN_AMOUNT': str(self.amount),
            'CALLBACK_URL': self.get_callback_url()
        }

        note = self.add_note()
        if note:
            paytm_params['MERC_UNQ_REF'] = note

        email = self.get_user_email()
        if email:
            paytm_params['EMAIL'] = email

        phone = self.get_user_mobile()
        if phone:
            paytm_params['MOBILE_NO'] = phone

        return paytm_params

    def get_checksumhash(self):
        return Checksum.generate_checksum(self._payload, self.conf.KEY)

    def post(self, request):
        self.request = request
        self.order = self.create_order()
        self._payload = self.get_payload()
        self._checksumhash = self.get_checksumhash()

        payload = {
            **self._payload,
            'CHECKSUMHASH': self._checksumhash,
            'domain': self.conf.DOMAIN
        }

        return render(request, 'paytm/checkout/redirect.html', payload)


class InitiatePaymentView(GenericInitiatePaymentView):
    """Wrapper for testing"""
    include_payment_charge = False
    channel = 'WEB'

    def get_amount(self):
        item_id = self.request.POST['item']
        item = Item.objects.get(pk=item_id)
        return item.price

    def get(self, request):
        if not django_settings.DEBUG:
            raise Http404

        self.request = request
        return render(request, 'paytm/checkout/index.html', {
            'items': Item.objects.all()
        })


class GenericValidateCheckoutView(View):
    model = Order
    PAYTM_MERCHANT_KEY = paytm_conf.KEY

    def __init__(self, *args, **kwargs):
        super(GenericValidateCheckoutView, self).__init__(*args, **kwargs)

        self.order = self.model()
        self.request = None
        self.paytm_params = dict()
        self.checksumhash = ''

    def update_order(self):
        mapping = {
            'TXNID': 'txn_id',
            'BANKTXNID': 'bank_txn_id',
            'CURRENCY': 'currency',
            'RESPCODE': 'resp_code',
            'RESPMSG': 'resp_message',
            'GATEWAYNAME': 'gateway',
            'BANKNAME': 'bank',
            'PAYMENTMODE': 'mode',
        }
        order = self.order
        paytm_prams = self.paytm_params

        for key in mapping:
            try:
                setattr(order, mapping[key], paytm_prams[key])
            except (KeyError, AttributeError):
                pass

            # Set Status
            if paytm_prams['STATUS'] == 'TXN_SUCCESS':
                order.status = Order.Status.SUCCESS
            elif paytm_prams['STATUS'] == 'TXN_FAILURE':
                order.status = Order.Status.FAILURE
            elif paytm_prams['STATUS'] == 'PENDING':
                order.status = Order.Status.PENDING
            else:
                order.status = Order.Status.UNKNOWN

            # Set date time
            if 'TXNDATE' in paytm_prams:
                order.transaction_date = datetime.strptime(paytm_prams['TXNDATE'], '%Y-%m-%d %H:%M:%S.%f')

            order.save()
            self.order = order

    def get_checksumhash(self):
        checksum = ""
        paytm_params = {}
        for key, value in self.paytm_dict.items():
            if key == 'CHECKSUMHASH':
                checksum = value
            else:
                paytm_params[key] = value

        return checksum, paytm_params

    def get_order(self):
        return Order.objects.get(order_id=self.paytm_params['ORDERID'])

    def verify_order(self, request):
        self.request = request
        self.paytm_dict = request.POST
        checksumhash, self.paytm_params = self.get_checksumhash()
        is_checksum_valid = Checksum.verify_checksum(self.paytm_params, self.PAYTM_MERCHANT_KEY, checksumhash)
        self.order = self.get_order()
        self.update_order()

        if not is_checksum_valid:
            self.order.status = self.order.Status.FRAUD
            self.order.save()

        return is_checksum_valid

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(GenericValidateCheckoutView, self).dispatch(*args, **kwargs)

    def post(self, request):
        self.verify_order(request)
        return HttpResponseRedirect(self.redirect_url)


class VerifyCheckoutView(GenericValidateCheckoutView):
    @property
    def redirect_url(self):
        return reverse('paytm:checkout:status', kwargs={
            'order_id': self.order.order_id
        })


class StatusCheckView(View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)

        return render(request, 'paytm/checkout/status.html', {
            'order': order
        })
