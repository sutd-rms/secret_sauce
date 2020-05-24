from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first, 
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response

import csv, io
from rest_framework.exceptions import APIException

class UnreadableCSVFile(APIException):
    status_code = 400
    default_detail = "Unable to read file."
    default_code = "unreadable_csv_file"

class WrongFormatCSVFile(APIException):
    status_code = 400
    default_detail = "CSV file has the wrong headers"
    default_code = "wrong_format_csv_file"

class UploadVerifier:
    """
    Helper class to verify validity of the uploaded datablock file

    Raises
    ------
    UnreadableCSVFile : APIException
        Exception raised when there are issues with reading the file.
    WrongFormatCSVFile : APIException
        Exception raised when there are issues related to the structure of the csv file.
    """

    def __init__(self, upload, encoding='utf-8'):
        """Raises UnreadableCSVFile if there are issues with reading the file"""
        upload.seek(0)
        try:
            io_obj = io.StringIO(upload.read().decode(encoding))
            self.csv_file = csv.DictReader(io_obj)
        except:
            raise UnreadableCSVFile()

    def is_valid(self):
        """Raises WrongFormatCSVFile if there are issues related to the structure of the csv file"""
        # TODO: Check validity of csv file, raise WrongFormatCSVFile
        pass