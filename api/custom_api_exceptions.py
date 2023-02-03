from rest_framework.exceptions import APIException
from rest_framework import status


class AutherizationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This endpoint is meant for only unauthenticated users."
    default_code = "invalid"
