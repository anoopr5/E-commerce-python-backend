import razorpay
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_order(amount):
    """
    Create an order on Razorpay.
    """
    order = client.order.create({
        'amount': amount * 100,  # amount in paise
        'currency': 'INR',
        'payment_capture': 1,  # 1 for automatic capture
    })
    return order
