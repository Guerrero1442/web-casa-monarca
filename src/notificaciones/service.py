from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger
from src.config import settings


def enviar_correo_solicitud_actualizada(
    email_destino: str,
    nombre_madre: str,
    titulo_evento: str,
    estado: str,
) -> None:
    """Envía notificación a la madre cuando se crea un evento que intersecta con su solicitud."""
    logger.info(f"Comunicaciones - Preparando correo de actualización de solicitud para {email_destino}...")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Evento Disponible para Cuidado Infantil: {titulo_evento}"
    msg["From"] = settings.SMTP_USER
    msg["To"] = email_destino

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #23352F;">
        <h1 style="color: #C36B53;">¡Hola, {nombre_madre}!</h1>
        <p>Se ha publicado un nuevo evento de cuidado infantil que coincide con tu franja horaria solicitada: <strong>{titulo_evento}</strong>.</p>
        <p>Estado actualizado de tu solicitud: <strong>{estado}</strong>.</p>
        <p>Puedes ingresar a la plataforma para confirmar la reserva de cupo para tu hijo(a).</p>
        <br/>
        <p>Atentamente,</p>
        <p><strong>Casa Monarca - Cuidado Infantil</strong></p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    server = None
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        logger.info(f"Comunicaciones - Correo de actualización enviado a {email_destino}.")
    except Exception:
        logger.exception(f"Comunicaciones - Error al enviar correo de actualización a {email_destino}.")
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass


def enviar_correo_reserva_confirmada(
    email_destino: str,
    nombre_madre: str,
    titulo_evento: str,
    inicio_evento: datetime,
) -> None:
    """Envía notificación de confirmación de reserva de cuidado infantil."""
    logger.info(f"Comunicaciones - Preparando correo de confirmación de reserva para {email_destino}...")
    fecha_str = inicio_evento.strftime("%d/%m/%Y a las %H:%M")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Reserva Confirmada: {titulo_evento}"
    msg["From"] = settings.SMTP_USER
    msg["To"] = email_destino

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #23352F;">
        <h1 style="color: #C36B53;">¡Reserva Confirmada, {nombre_madre}!</h1>
        <p>Tu reserva para el evento <strong>{titulo_evento}</strong> ha sido confirmada exitosamente.</p>
        <p><strong>Fecha y hora de inicio:</strong> {fecha_str}</p>
        <br/>
        <p>Atentamente,</p>
        <p><strong>Casa Monarca - Cuidado Infantil</strong></p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    server = None
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        logger.info(f"Comunicaciones - Correo de reserva enviado a {email_destino}.")
    except Exception:
        logger.exception(f"Comunicaciones - Error al enviar correo de reserva a {email_destino}.")
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass
