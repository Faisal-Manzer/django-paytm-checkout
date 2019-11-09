__all__ = ['Order', 'Item']
from django.db import models
from django.contrib.auth import get_user_model

from paytm import conf as paytm_conf
from paytm.helpers import sha256


class Item(models.Model):
    price = models.FloatField()
    name = models.CharField(max_length=255)
    tag = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    class Channel:
        WEB = paytm_conf.CHANNEL_WEBSITE
        APP = paytm_conf.CHANNEL_MOBILE_APP
        choices = (
            (WEB, 'Web'),
            (APP, 'App')
        )

    class Status:
        SUCCESS = 'S'
        FAILURE = 'F'
        UNKNOWN = 'U'
        PENDING = 'P'
        FRAUD = 'E'

        choices = (
            (SUCCESS, 'Success'),
            (FAILURE, 'Failure'),
            (PENDING, 'Pending'),
            (UNKNOWN, 'Unknown'),
            (FRAUD, 'Fraud')
        )

    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.DO_NOTHING)

    # ------------------------------------ Pay load sent to paytm --------------------------------

    # ORDER_ID* String(50)
    order_id = models.CharField(max_length=50)

    # CUST_ID* String(64)
    customer_id = models.CharField(max_length=64)

    # TXN_AMOUNT* String(10)
    amount = models.FloatField()
    real_amount = models.FloatField()  # amount aimed to capture

    # CHANNEL_ID* String(3)
    channel = models.CharField(max_length=3, choices=Channel.choices, default=Channel.WEB)

    # MOBILE_NO String(15)
    mobile = models.CharField(max_length=15, null=True, blank=True)

    # EMAIL String(50
    email = models.EmailField(null=True, blank=True)

    # MERC_UNQ_REF String(50)
    notes = models.CharField(max_length=50, null=True, blank=True)

    # ---------------------------------- Response sent by paytm ---------------------------------

    # TXNID* String(64)
    txn_id = models.CharField(max_length=64, null=True, blank=True)

    # BANKTXNID* String
    bank_txn_id = models.TextField(null=True, blank=True)

    # STATUS* String(20)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNKNOWN)

    # CURRENCY* String(3)
    currency = models.CharField(max_length=3, null=True, blank=True)

    # RESPCODE* String(10)
    resp_code = models.CharField(max_length=10, null=True, blank=True)

    # RESPMSG* String
    resp_message = models.TextField(null=True, blank=True)

    # TXNDATE* DateTime
    transaction_date = models.DateTimeField(null=True, blank=True)

    # GATEWAYNAME String(15)
    gateway = models.CharField(max_length=15, null=True, blank=True)

    # BANKNAME* String
    bank = models.TextField(null=True, blank=True)

    # PAYMENTMODE* String(15)
    mode = models.CharField(max_length=15, null=True, blank=True)

    initiated = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new_order = False
        if self.id is None:
            is_new_order = True
            self.order_id = ''

        super(Order, self).save(*args, **kwargs)
        if is_new_order:
            self.order_id = sha256(str(self.id).rjust(50, '0'))[:50]
            self.save()

    def __str__(self):
        return f'{self.order_id}'
