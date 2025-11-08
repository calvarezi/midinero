from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import exceptions
from .utils import error_response

def custom_exception_handler(exc, context):
    """
    Envuelve el exception_handler de DRF y transforma la salida a nuestro formato.
    Coloca este handler en settings.py:
    """
    # Primero, deja que DRF genere la respuesta estándar
    response = drf_exception_handler(exc, context)

    # Si DRF produjo una Response, reformatéala
    if response is not None:
        # extrae detalles si existen
        detail = None
        if isinstance(response.data, dict):
            detail = response.data.get('detail', response.data)
        else:
            detail = response.data

        # Para ValidationError, devuelve errores específicos
        if isinstance(exc, exceptions.ValidationError):
            return error_response(
                message="Validation error",
                errors=response.data,
                status_code=response.status_code
            )

        # Para otros errores que DRF reconoce:
        return error_response(
            message=detail or str(exc),
            errors=response.data if not isinstance(response.data, str) else None,
            status_code=response.status_code
        )

    # Si DRF no creó Response (error inesperado), devuelve un 500 genérico
    return error_response(
        message="Server error",
        errors={"detail": str(exc)},
        status_code=500
    )
