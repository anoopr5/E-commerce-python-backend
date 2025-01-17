from django.conf import settings
from django.http import JsonResponse
from django.views import View
from .razorpay_client import create_order
from django.views.decorators.csrf import csrf_exempt

class CreatePaymentOrderView(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """
        Create an order in Razorpay.
        :return: JSON response containing the order ID and Razorpay key.
        """
        amount = 100  # Example amount in INR (replace with your order amount)
        
        try:
            print("Creating order")
            order = create_order(amount)
            response_data = {
                'order_id': order['id'],
                'key': settings.RAZORPAY_KEY_ID,
            }
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

import hashlib
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .razorpay_client import client

class PaymentCallbackView(View):
    @csrf_exempt  # Disable CSRF protection for payment callback (you should handle CSRF in production)
    def post(self, request, *args, **kwargs):
        """
        Handle Razorpay payment callback and verify payment signature.
        """
        params_dict = request.POST
        razorpay_order_id = params_dict.get('razorpay_order_id')
        razorpay_payment_id = params_dict.get('razorpay_payment_id')
        razorpay_signature = params_dict.get('razorpay_signature')

        # Construct the string for signature verification
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected_signature = hashlib.sha256(message.encode('utf-8')).hexdigest()

        if expected_signature == razorpay_signature:
            # Payment successful, handle your order here
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failure', 'message': 'Signature mismatch'}, status=400)
