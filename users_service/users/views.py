from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import *
from .services import insert_user, is_valid_email, is_valid_password, verify_creds, is_valid_phone_number
import json
import jwt
from datetime import datetime

class UserRegister(APIView):

    def post(self, request):
        try:
            # Get data from the request
            Fname = request.data.get('Fname')
            Lname = request.data.get('Lname')
            email = request.data.get('email')
            password = request.data.get('password')
            phone_number = request.data.get('phoneNumber')
            address = request.data.get('address')

            # Check if all required fields are present
            if not all([Fname, Lname, email, password, phone_number]):
                return Response({'message': 'All fields are required!'}, status=status.HTTP_400_BAD_REQUEST)

            if not is_valid_email(email):
                return Response({'message': 'Invalid email address!'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not is_valid_password(password):
                return Response({'message': 'Invalid password!'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not is_valid_phone_number(phone_number):
                return Response({'message': 'Invalid phone number!'}, status=status.HTTP_400_BAD_REQUEST)
            # Use sync_to_async to wrap the async insert_user function call
            success,result = insert_user(Fname, Lname, email, password, phone_number, address)
            # If insertion is successful, return HTTP 201 Created
            if success:
                return Response({'message': f'User created successfully' , 'value':f'{result}'}, status=HTTP_201_CREATED)
            else:
                return Response({'message': f'{result}'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # If there's any other error, return a generic error response
            return Response({'message': f'Error creating user: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLogin(APIView):

    def post(self, request):
        try:
            # Get data from the request
            email = request.data.get('email')
            password = request.data.get('password')

            # Check if all required fields are present
            if not all([email, password]):
                return Response({'message': 'All fields are required!'}, status=status.HTTP_400_BAD_REQUEST)
            
            success,result = verify_creds(email, password)
            # If insertion is successful, return HTTP 201 Created
            if success:
                jwt_token = jwt.encode({'email': email, 'password':password,'datetime':str(datetime.now())}, 'secret', algorithm='HS256')
                decoded_jwt_token = jwt.decode(jwt_token,'secret', algorithms=["HS256"])
                print("DECODED JWT:",decoded_jwt_token)
                return Response({'message': f'Login successfully','JWT_TOKEN':jwt_token }, status=HTTP_200_OK)
            else:
                return Response({'message': f'{result}'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # If there's any other error, return a generic error response
            return Response({'message': f'Error creating user: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckUserExistence(APIView):
    
    def post(self, request):
        try:
            # Get data from the request
            email = request.data.get('email')
            password = request.data.get('password')
            
            if not all([email, password]):
                return Response({'message': 'All fields are required!'}, status=status.HTTP_400_BAD_REQUEST)
            
            success,result = verify_creds(email, password)
            if success:
                return Response({'message': f'User exists'}, status=HTTP_200_OK)
            else:
                return Response({'message': f'{result}'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': f'Error creating user: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
