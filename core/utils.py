from rest_framework import status
from rest_framework.response import Response

def success_response(data=None, message="OK", status_code=status.HTTP_200_OK):
    """
    Formato uniforme para respuestas exitosas.
    """
    payload = {
        "status": "success",
        "message": message,
        "data": data
    }
    return Response(payload, status=status_code)

def error_response(message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Formato uniforme para respuestas de error.
    """
    payload = {
        "status": "error",
        "message": message,
        "errors": errors or {}
    }
    return Response(payload, status=status_code)
