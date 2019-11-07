# Django Paytm Checkout
A simple modular approach for Paytm's [checkout][paytm-checkout] and [custom checkout][paytm-custom-checkout]

## Installation
Use pip to install from PyPI:
```shell script
pip install django-paytm-checkout
```

## Configuration
Configure your django project by adding the following in your settings:
```python
PAYTM_MERCHANT_ID = 'YOUR_PAYTM_MERCHANT_ID'
PAYTM_MERCHANT_KEY = 'YOUR_PAYTM_MERCHANT_KEY'
PAYTM_INDUSTRY = 'YOUR_INDUSTRY_TYPE'
PAYTM_WEBSITE = 'YOUR_PAYTM_WEBSITE'
```

Setting the environment:
```python
PAYTM_DEBUG = True 
# default: True (for staging)
# False (for production)
```

These are optional settings, change if it not the same as default:
```python
PAYTM_CHANNEL_WEBSITE = ''  # default: WEB
PAYTM_CHANNEL_MOBILE_APP = ''  # default: WAP

PAYTM_STAGING_DOMAIN = ''  # default: securegw-stage.paytm.in
PAYTM_PRODUCTION_DOMAIN = ''  # default: securegw.paytm.in
```

## Using Default application
Add the following into your `urls.py`
```python
from django.urls import path, include

urlpatterns = [
    path('paytm/', include('paytm.urls', namespace='paytm')),
]
```

---
[paytm-checkout]: https://developer.paytm.com/docs/v1/payment-gateway/
[paytm-custom-checkout]: https://developer.paytm.com/docs/v1/custom-checkout/
