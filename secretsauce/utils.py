from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException

import csv, io

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

class IncompatibleInvitationCode(APIException):
    status_code = 400
    default_detail = "Invitation code does not belong to this email address"
    default_code = "incompatible_invitation_code"

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

        self.check_headers()
        self.check_type()

    def check_headers(self):
        """Raises WrongHeaderCSVFile if there are issues related to the structure of the csv file"""
        first_row = next(self.csv_file)
        for idx, header in enumerate(first_row):
            if header != self.headers[idx]:
                raise WrongHeaderCSVFile()
        self.io_obj.seek(0)
        self.csv_file = csv.DictReader(self.io_obj)
        
    def check_type(self):
        """Raises WrongCellTypeCSVFile if there are issues related to the structure of the csv file"""
        for row in self.csv_file:
            for header in row:
                value = row[header]
                try:
                    float(value)
                except:
                    raise WrongCellTypeCSVFile()