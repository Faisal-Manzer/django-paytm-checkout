from django.urls import path, include

urlpatterns = [
    path('checkout/', include('paytm.checkout.urls', namespace='checkout'))
]

app_name = 'paytm'
