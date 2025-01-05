import logging
from .db_client import CosmosDBClient
import re
import phonenumbers
from phonenumbers import NumberParseException, is_valid_number

logger = logging.getLogger(__name__)
def insert_user(Fname, Lname, email, password,phone_number,address):
    """Insert a new user into the database asynchronously."""
    try:
        # Create a new CosmosDBClient instance
        db_client = CosmosDBClient(container_name='Users')
        db_item = db_client.read_item("email", email)
        logger.info(f"db_item: {db_item}")
        # Create a new user object
        if db_item:
            return False, "User already exists"
        
        user = {
            'id': email,
            'Fname': Fname,
            'Lname': Lname,
            'email': email,
            'password': password,
            'phoneNum': phone_number,
            'address': address
        }
        # Insert the user into the database
        result = db_client.create_user(user)
        return True, result
    
    except Exception as e:
        logger.error(f"Error inserting user: {str(e)}")
        return False, str(e)
    
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def is_valid_password(password):
    if (len(password) < 8 or not re.search("[a-z]", password) or
            not re.search("[A-Z]", password) or not re.search("[0-9]", password)):
        return False
    return True

def verify_creds(email, password):
    try:
        db_client = CosmosDBClient(container_name='Users')
        db_item = db_client.read_item("email", email)
        if db_item is None:
            return False, "User does not exist"
        if db_item['password'] != password:
            return False, "Invalid password"
        return True, db_item
    except Exception as e:
        logger.error(f"Error verifying user credentials: {str(e)}")
        return False, str(e)
    
from datetime import datetime, timedelta

def check_jwt_is_within_10_minutes(json_data):
    # Extract datetime from the JSON (string format)
    json_datetime_str = json_data['datetime']
    
    # Convert the datetime string from the JSON into a datetime object
    json_datetime = datetime.strptime(json_datetime_str, "%Y-%m-%d %H:%M:%S.%f")
    
    # Get the current date and time
    current_datetime = datetime.now()
    
    # Calculate the difference between the current datetime and the datetime in the JSON
    time_difference = current_datetime - json_datetime
    
    # Check if the time difference is less than 10 minutes
    if time_difference < timedelta(minutes=0.5):
        return True
    else:
        return False


def is_valid_phone_number(phone_number, region="IN"):
    try:
        # Parse the phone number with the provided region
        parsed_number = phonenumbers.parse(phone_number, region)
        
        # Validate the number
        if is_valid_number(parsed_number):
            return True
        else:
            return False
    except NumberParseException:
        # If the phone number cannot be parsed, it's invalid
        return False
