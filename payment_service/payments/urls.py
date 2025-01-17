from django.urls import path
from .views import CreatePaymentOrderView, PaymentCallbackView

urlpatterns = [
    path('create-payment-order/', CreatePaymentOrderView.as_view(), name='create_payment_order'),
    path('payment-callback/', PaymentCallbackView.as_view(), name='payment_callback'),
]
