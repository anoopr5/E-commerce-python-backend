import jwt
import requests
from .db_client import CosmosDBClient
import re
import uuid
from datetime import datetime, timedelta

def insert_product(product_name, product_description, product_price, product_quantity, product_category, product_tags, isActive):
    """Insert a new product into the database asynchronously."""
    try:
        # Create a new CosmosDBClient instance
        db_client = CosmosDBClient(container_name='Products')
        db_item = db_client.read_item("productName", product_name)
        print("db_item: ",db_item)
        
        if not db_item:
            print("INSIDE IF")
            id = str(uuid.uuid4().int)[:8]
            product = {
                'id': id,
                'productId':id,
                'productName': product_name,
                'productDescription': product_description,
                'productPrice': product_price,
                'productQuantity': product_quantity,
                'productCategory': product_category,
                'productTags': product_tags,
                'isActive': isActive,
                'createdDate': str(datetime.now()),
                'updatedDate': str(datetime.now())
            }
            # Insert the product into the database
            result = db_client.create_item(product)
            return True, result
        else:
            print("INSIDE ELSE")
            product = {
                'id': db_item['id'],
                'productId': db_item['productId'],
                'productName': db_item['productName'],
                'productDescription': product_description,
                'productPrice': product_price,
                'productQuantity': int(product_quantity) + int(db_item['productQuantity']),
                'productCategory': product_category,
                'productTags': list(set(db_item['productTags'] + product_tags)),
                'isActive': isActive,
                'createdDate': db_item['createdDate'],
                'updatedDate': str(datetime.now())
            }
            result = db_client.update_item(product)
        # Update the product in the database
            return "updated", result
    
    except Exception as e:
        return False, str(e)
    
def update_product(product_name, product_description, product_price, product_quantity, product_category, product_tags, isActive):

    """Update a product in the database."""
    try:
        # Create a new CosmosDBClient instance
        db_client = CosmosDBClient(container_name='Products')
        db_item = db_client.read_item("productName", product_name)
        # Create a new product object
        if db_item:
            product = {
                'id': db_item['id'],
                'productId': db_item['productId'],
                'productName': db_item['productName'],
                'productDescription': product_description if product_description else db_item['productDescription'],
                'productPrice': product_price if product_price else db_item['productPrice'],
                'productQuantity': int(product_quantity) + int(db_item['productQuantity']),
                'productCategory': product_category if product_category else db_item['productCategory'],
                'productTags': list(set(db_item['productTags'] + product_tags)),
                'isActive': isActive if isActive is not None else db_item['isActive'],
                'createdDate': db_item['createdDate'],
                'updatedDate': str(datetime.now())
            }
            # Update the product in the database
            result = db_client.update_item(product)
            return result
        else:
            return False
    except Exception as e:
        return False
    
def get_all_products():
    """Get all products from the database."""
    try:
        # Create a new CosmosDBClient instance
        db_client = CosmosDBClient(container_name='Products')
        result = []
        db_items = db_client.get_all_items()
        for item in db_items:
            value = {
                'productId': item.get('productId'),
                'productName': item.get('productName'),
                'productPrice': item.get('productPrice'),
                'productQuantity': item.get('productQuantity'),
                'isActive': item.get('isActive')
            }
            if value.get('isActive'):
                result.append(value)
        return result
    except Exception as e:
        return str(e)
    
def get_specific_products(product_ids):
    """Get specific products from the database."""
    try:
        db_client = CosmosDBClient(container_name='Products')
        result = []
        not_found_ids = []
        for product_id in product_ids:
            print("product_id: ",product_id)
            db_value = db_client.read_item("productId", product_id)
            print("db_value: ",db_value)
            if db_value:
                value = {
                    'productId': db_value.get('productId'),
                    'productName': db_value.get('productName'),
                    'productPrice': db_value.get('productPrice'),
                    'productQuantity': db_value.get('productQuantity'),
                    'isActive': db_value.get('isActive')
                }
                if value.get('isActive'):
                    result.append(value)
            else:
                not_found_ids.append(product_id)
        return result, not_found_ids
    except Exception as e:
        return str(e)
    
def delete_product(product_ids):
    """Delete a product from the database."""
    try:
        db_client = CosmosDBClient(container_name='Products')
        deleted_ids = []
        not_found_ids = []
        for product_id in product_ids:
            db_value = db_client.read_item("productId", product_id)
            if db_value:
                print("product_id: ",product_id)
                db_client.delete_item(user_id=product_id)
                deleted_ids.append(product_id)
            else:
                not_found_ids.append(product_id)
        return deleted_ids, not_found_ids
    except Exception as e:
        return str(e)
    
def verify_admin_jwt(jwt_token):
    try:
        jwt_token = jwt_token.replace("Bearer ","",1)
        decoded_jwt_token = jwt.decode(jwt_token,'secret', algorithms=["HS256"])
        print("decoded_jwt_token: ",decoded_jwt_token)

        if decoded_jwt_token.get('email') == 'Admin@123' :
            given_datetime = datetime.strptime(decoded_jwt_token.get('datetime'), '%Y-%m-%d %H:%M:%S.%f')
            current_time = datetime.now()
            time_diff = current_time - given_datetime

            if time_diff <= timedelta(minutes=30):
                return True

        return False
    except Exception as e:
        return False
    
def verify_user_jwt(jwt_token):
    try:
        url = "http://127.0.0.1:5000/api/v1/check/user/"
        
        jwt_token = jwt_token.replace("Bearer ","",1)
        decoded_jwt_token = jwt.decode(jwt_token,'secret', algorithms=["HS256"])
        print("decoded_jwt_token: ",decoded_jwt_token)
        data = {
            'email':decoded_jwt_token.get('email'),
            'password':decoded_jwt_token.get('password')
        }
        response = requests.post(url, json=data)
        print("response: ",response.json())
        if response.status_code == 200:
            given_datetime = datetime.strptime(decoded_jwt_token.get('datetime'), '%Y-%m-%d %H:%M:%S.%f')
            current_time = datetime.now()
            time_diff = current_time - given_datetime

            if time_diff <= timedelta(minutes=30):
                return True

        return False
    except Exception as e:
        return False