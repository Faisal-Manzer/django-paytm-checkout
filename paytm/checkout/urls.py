from django.urls import path

from .views import *

urlpatterns = [
    path('', InitiatePaymentView.as_view(), name='index'),
    path('initiate/', InitiatePaymentView.as_view(), name='initiate'),
    path('validate/', VerifyCheckoutView.as_view(), name='validate'),
    path('status/<str:order_id>/', StatusCheckView.as_view(), name='status')
]

app_name = 'paytm:checkout'
