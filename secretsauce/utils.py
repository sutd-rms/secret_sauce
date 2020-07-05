from django.urls import reverse

from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from django.template import loader
from django.core.mail import send_mail

import random
import string
import csv, io

def reverse_args(name):
    """
    Helper function to reverse URL with arguments.
    Returns a function whose parameters are the URL arguments.
    """
    return lambda *args: reverse(name, args=tuple(args)) 

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first, 
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response

class UnreadableCSVFile(APIException):
    status_code = 400
    default_detail = "Unable to read file."
    default_code = "unreadable_csv_file"

class WrongHeaderCSVFile(APIException):
    status_code = 400
    default_detail = "CSV file has the wrong headers"
    default_code = "wrong_format_csv_file"

class WrongCellTypeCSVFile(APIException):
    status_code = 400
    default_detail = "CSV file has the wrong cell type"
    default_code = "wrong_cell_type_csv_file"

class UploadVerifier:
    """
    Helper class to verify validity of the uploaded datablock file

    Raises
    ------
    UnreadableCSVFile : APIException
        Exception raised when there are issues with reading the file.
    WrongHeaderCSVFile : APIException
        Exception raised when there are issues related to the structure of the csv file.
    WrongCellTypeCSVFile : APIException
        Exception raised when there are issues related to the cell types of the csv file.
    """

    headers = ['Wk', 'Tier', 'Groups', 'Store', 'Item_ID', 'Qty_', 'Price_']

    def __init__(self, upload, encoding='utf-8'):
        """Raises UnreadableCSVFile if there are issues with reading the file"""
        upload.seek(0)
        try:
            self.io_obj = io.StringIO(upload.read().decode(encoding))
            self.csv_file = csv.DictReader(self.io_obj)
        except:
            raise UnreadableCSVFile()

        checks = [getattr(self, m) for m in dir(self) if m.startswith('check_')]
        for m in checks:
            m()
            self.reset_seeker()

    def check_headers(self):
        """Raises WrongHeaderCSVFile if there are issues related to the structure of the csv file"""
        first_row = next(self.csv_file)
        for idx, header in enumerate(first_row):
            if header != self.headers[idx]:
                raise WrongHeaderCSVFile()
        
    def check_type(self):
        """Raises WrongCellTypeCSVFile if there are issues related to the structure of the csv file"""
        for row in self.csv_file:
            # row is an OrderedDict of (header, value)
            for header in row:
                value = row[header]
                try:
                    float(value)
                except:
                    raise WrongCellTypeCSVFile()

    def reset_seeker(self):
        self.io_obj.seek(0)
        self.csv_file = csv.DictReader(self.io_obj)

    def get_schema(self):
        """Returns list of unique Item_IDs from uploaded file"""
        required_header = self.headers[4]
        item_ids = map(lambda row: int(row[required_header]), self.csv_file)
        self.reset_seeker()
        return set(item_ids)

def send_email(subject, from_email, to_email, message, html_message_path, mappings={}):
    html_message = loader.render_to_string(
        html_message_path,
        mappings
    )
    send_mail(subject, message, from_email, to_email, fail_silently=False, html_message=html_message)

def generatePassword(stringLength=10):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))    
