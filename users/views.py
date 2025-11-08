from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer
from core.utils import success_response, error_response


class RegisterView(generics.CreateAPIView):
    """
    Registro de nuevos usuarios.

    Crea una cuenta nueva con los campos:
    - username
    - email
    - password

    Devuelve los datos del usuario recién creado (sin contraseña).
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Sobrescribimos create para devolver una respuesta uniforme
        usando los helpers del módulo `core.utils`.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return success_response(
            data=serializer.data,
            message="Usuario registrado exitosamente.",
            status_code=status.HTTP_201_CREATED
        )


class ProfileView(generics.RetrieveAPIView):
    """
    Devuelve los datos del usuario autenticado.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        """
        Devuelve el perfil del usuario con formato uniforme.
        """
        serializer = self.get_serializer(self.get_object())
        return success_response(data=serializer.data, message="Perfil obtenido correctamente.")


class LogoutView(APIView):
    """
    Cierra la sesión de forma segura invalidando el token de refresco.
    Requiere enviar en el body:
    {
        "refresh": "<token_refresh>"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return error_response("El token de refresco es requerido.", status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return success_response(message="Sesión cerrada correctamente.", status_code=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return error_response("Token inválido o ya expirado.", status.HTTP_400_BAD_REQUEST)
