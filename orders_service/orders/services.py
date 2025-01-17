import jwt
import requests
from .db_client import CosmosDBClient
import re
import uuid
from datetime import datetime, timedelta

def check_product_availability(product_list):
    url = 'http://127.0.0.1:8000/api/v1/check/product/'
    data = {
        'productList': product_list
    }
    print("WORKING TILL HERE 1")
    response = requests.post(url, json=data)
    print("WORKING TILL HERE 2",response.json())
    return response.json()

def insert_order(products, user_id, shipping_address, payment_method):
    """Insert a new order into the database asynchronously."""
    try:
        # Create a new CosmosDBClient instance

        product_availability_response = check_product_availability(products)
        if len(product_availability_response.get('not_found_ids'))>0 :
            return False, 'All products are not available'
        db_client = CosmosDBClient(container_name='Orders')

        rzp_test_d3cSqBhEchRSfu
        mG3bBnqWf6Rqrwrt6QI0Uuor
        id = str(uuid.uuid4().int)[:8]
        order = {
            'id': id,
            'orderId': id,
            'products': products,
            'userId': user_id,
            'shippingAddress': shipping_address,
            'paymentMethod': payment_method,
            'totalPrice': product_availability_response.get('totalPrice'),
            'orderStatus': 'Pending',
            'createdDate': str(datetime.now()),
            'updatedDate': str(datetime.now())
        }
        # Insert the order into the database
        result = db_client.create_item(order)
        return True, result
    except Exception as e:
        return False, str(e)