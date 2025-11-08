from rest_framework import status
from rest_framework.response import Response
from .utils import success_response

class CreateListMixin:
    """
    Mixin conveniente para viewsets que quieren endpoints index/create con
    respuestas formateadas uniformemente.
    Úsalo así:
        class MyViewSet(CreateListMixin, ModelViewSet):
            ...
    """

    def create(self, request, *args, **kwargs):
        resp = super().create(request, *args, **kwargs)
        # resp.data contiene el serializer.data ya validado
        return success_response(data=resp.data, message="Created", status_code=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        # list ya devuelve paginated Response o queryset serializado
        return success_response(data=resp.data, message="List retrieved", status_code=status.HTTP_200_OK)
