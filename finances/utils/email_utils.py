from django.core.mail import send_mail
from django.conf import settings


def send_notification_email(to_email, subject, message):
    """
    Envía un correo electrónico de notificación al usuario.
    Este helper es usado por NotificationService cuando 'send_email=True'.

    Parámetros:
    - to_email (str): dirección de correo del destinatario
    - subject (str): asunto del correo
    - message (str): cuerpo del mensaje (texto plano)
    """

    if not to_email:
        return False  # no enviar si el usuario no tiene correo

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False
