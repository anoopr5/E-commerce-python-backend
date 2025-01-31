from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import *
import json
import jwt
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .services import insert_product, update_product, get_all_products,get_specific_products,delete_product,verify_admin_jwt, verify_user_jwt, check_product_availability

class ProductView(APIView):
    def post(self, request):
        try:
            # Get data from the request
            product_name = request.data.get('productName')
            product_description = request.data.get('productDescription')
            product_price = request.data.get('productPrice')
            product_quantity = request.data.get('productQuantity')
            product_category = request.data.get('productCategory')
            product_tags = request.data.get('productTags') 
            isActive = request.data.get('isActive',None)

            jwt_token = request.headers.get('Authorization', None)
            if jwt_token:
                decorded_token = verify_admin_jwt(jwt_token)
                if not decorded_token:
                    return Response({'message': 'Unauthorized! or Token has Expired'}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if all required fields are present  
            if not all([product_name, product_description, product_price, product_quantity, product_category, product_tags]) or isActive is None:
                return Response({'message': 'All fields are required!'}, status=status.HTTP_400_BAD_REQUEST)
            
            success,result = insert_product(product_name, product_description, product_price, product_quantity, product_category, product_tags, isActive)

            # If insertion is successful, return HTTP 201 Created   
            if success == True:
                print("IN TRUE")
                return Response({'message': f'Product created successfully' , 'value':f'{result}'}, status=HTTP_201_CREATED)
            elif success == "updated":
                return Response({'message': f'Product updated successfully' , 'value':f'{result}'}, status=HTTP_200_OK)
            else:
                return Response({'message': f'{result}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Error creating product: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def patch(self, request):
        try:
            # Get the data from the request (fields are optional)
            product_name = request.data.get('productName', None)
            product_description = request.data.get('productDescription', None)
            product_price = request.data.get('productPrice', None)
            product_quantity = request.data.get('productQuantity', None)
            product_category = request.data.get('productCategory', None)
            product_tags = request.data.get('productTags', None)
            isActive = request.data.get('isActive', None)

            jwt_token = request.headers.get('Authorization', None)
            if jwt_token:
                decorded_token = verify_admin_jwt(jwt_token)
                if not decorded_token:
                    return Response({'message': 'Unauthorized! or Token has Expired'}, status=status.HTTP_401_UNAUTHORIZED)


            result = update_product(product_name,product_description, product_price, product_quantity, product_category, product_tags, isActive)

            # If update is successful, return HTTP 200 OK   
            if result:
                return Response({'message': f'Product updated successfully'}, status=HTTP_200_OK)
            else:
                return Response({'message': f"Product doesn't exists"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': f'Error creating product: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        try:
            product_ids = request.query_params.getlist('productId', None)

            jwt_token = request.headers.get('Authorization', None)
            if jwt_token:
                decorded_token = verify_user_jwt(jwt_token)
                if not decorded_token:
                    return Response({'message': 'Unauthorized! or Token has Expired'}, status=status.HTTP_401_UNAUTHORIZED)

            if product_ids:
                result,not_found_ids = get_specific_products(product_ids)
                if len(not_found_ids) == len(product_ids):
                    return Response({'message':f'Product not found for IDs: {not_found_ids}'}, status=HTTP_404_NOT_FOUND)
                elif len(not_found_ids) > 0:
                    return Response({'message':f'Product not found for IDs: {not_found_ids}','products': result}, status=HTTP_200_OK)
                else:
                    return Response({'products': result}, status=HTTP_200_OK)
            else:
                result = get_all_products()
                return Response({'products': result}, status=HTTP_200_OK)
        
        except Exception as e:
            return Response({'message': f'Error getting products: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request):
        try:
            product_ids = request.query_params.getlist('productId', None)

            jwt_token = request.headers.get('Authorization', None)
            if jwt_token:
                decorded_token = verify_admin_jwt(jwt_token)
                if not decorded_token:
                    return Response({'message': 'Unauthorized! or Token has Expired'}, status=status.HTTP_401_UNAUTHORIZED)

            if product_ids:
                deleted_ids,not_found_ids = delete_product(product_ids)
                if len(not_found_ids) == len(product_ids):
                    return Response({'message':f'Product not found for IDs: {not_found_ids}'}, status=HTTP_404_NOT_FOUND)
                elif len(not_found_ids) > 0:
                    return Response({'message':f'Product not found for IDs: {not_found_ids}','deleted_ids': deleted_ids}, status=HTTP_200_OK)
                else:
                    return Response({'message': 'Product deleted successfully'}, status=HTTP_200_OK)
            else:
                return Response({'message': 'Product ID is required!'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Error deleting product: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class CheckProductAvailability(APIView):
    
    def post(self, request):
        products_list = request.data.get('productList')
        
        # Check if 'productList' is provided
        if not products_list:
            return Response({'message': 'Product list is required!'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check product availability
            result, not_found_ids, total_price = check_product_availability(products_list)

            # Handle different cases based on not_found_ids
            if len(not_found_ids) == len(products_list):
                return Response(
                    {'message': 'None of the products were found or are out of stock!',
                     'not_found_ids': not_found_ids},status=status.HTTP_404_NOT_FOUND)
            
            elif not_found_ids:
                return Response(
                    {'message': 'Some products were not found or are out of stock!',
                     'not_found_ids': not_found_ids,
                     'products': result},status=status.HTTP_200_OK
                )
            
            return Response(
                {'message': 'All products are available for purchase!',
                 'products': result,
                 'totalPrice': total_price,
                 'not_found_ids': not_found_ids},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response({'message': f'Error processing products: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)