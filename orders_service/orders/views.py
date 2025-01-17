from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import *
import json
import jwt
from datetime import datetime
from .services import insert_order

class OrderView(APIView):
    def post(self, request):
        try:
            # Get data from the request
            products = request.data.get('products')
            user_id = request.data.get('userId')
            shipping_address = request.data.get('shippingAddress')
            payment_method = request.data.get('paymentMethod')

            # Check if all required fields are present
            if not all([products, user_id, shipping_address, payment_method]):
                return Response({'message': 'All fields are required!'}, status=status.HTTP_400_BAD_REQUEST)
                
            success,result = insert_order(products, user_id, shipping_address, payment_method)
            # If insertion is successful, return HTTP 201 Created
            if success:
                return Response({'message': f'Order created successfully' , 'value':f'{result}'}, status=HTTP_201_CREATED)
            else:
                return Response({'message': f'{result}'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'message': f'Error creating order: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)