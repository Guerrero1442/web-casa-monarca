from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger
from src.config import settings


def enviar_correo_confirmacion(email: str, titulo_evento: str) -> None:
    """Simula el envío inmediato de un correo de confirmación de inscripción

    utilizando la API de Resend.
    """
    logger.info(
        f"Comunicaciones - Iniciando envio de correo de confirmacion para {email}..."
    )
    # Lógica de simulación (simula la integración asíncrona de Resend API)
    logger.info(
        f"Comunicaciones - Correo de confirmacion enviado exitosamente a {email} para el evento '{titulo_evento}'."
    )


def enviar_correo_agradecimiento(
    email: str, titulo_evento: str, horas: float
) -> None:
    """Simula el envío de un correo de agradecimiento por participación,

    reportando las horas de voluntariado acreditadas.
    """
    logger.info(
        f"Comunicaciones - Iniciando envio de agradecimiento y reporte de horas para {email}..."
    )
    # Lógica de simulación
    logger.info(
        f"Comunicaciones - Correo de agradecimiento enviado a {email} para el evento '{titulo_evento}'. Horas acreditadas: {horas}."
    )


def enviar_correo_bienvenida(email_destino: str, nombre_usuario: str) -> None:
    """Envía un correo electrónico real de bienvenida y confirmación de registro

    utilizando un servidor SMTP.
    """
    logger.info(
        f"Comunicaciones - Preparando correo SMTP de bienvenida para {email_destino}..."
    )

    # Crear el mensaje MIME
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Bienvenido a Casa Monarca"
    msg["From"] = settings.SMTP_USER
    msg["To"] = email_destino

    # Cuerpo HTML
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #23352F;">
        <h1 style="color: #C36B53;">¡Bienvenido a Casa Monarca, {nombre_usuario}!</h1>
        <p>Gracias por registrarte como voluntario en nuestra plataforma de ayuda humanitaria.</p>
        <p>Tu participación es fundamental para continuar apoyando a nuestra comunidad migrante.</p>
        <br/>
        <p>Atentamente,</p>
        <p><strong>El equipo de Casa Monarca</strong></p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    server = None
    try:
        # Iniciar conexión SMTP
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        server.starttls()  # Seguridad obligatoria
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        logger.info(
            f"Comunicaciones - Correo de bienvenida enviado con éxito vía SMTP a {email_destino}."
        )
    except smtplib.SMTPException:
        # Registrar el traceback completo usando logger.exception sin lanzar el error al cliente
        logger.exception(
            f"Comunicaciones - Error SMTP al enviar correo de bienvenida a {email_destino}."
        )
    except Exception:
        # Captura de errores inesperados de socket/conexión
        logger.exception(
            f"Comunicaciones - Error inesperado al conectar con el servidor SMTP para {email_destino}."
        )
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass


def enviar_correo_inscripcion(
    email_destino: str,
    nombre_usuario: str,
    nombre_evento: str,
    fecha_inicio: datetime,
) -> None:
    """Envía un correo electrónico real de confirmación de inscripción a un

    evento utilizando SMTP.
    """
    logger.info(
        f"Comunicaciones - Preparando correo SMTP de inscripcion para {email_destino}..."
    )

    # Formatear la fecha
    fecha_str = fecha_inicio.strftime("%d/%m/%Y a las %H:%M")

    # Crear el mensaje MIME
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Confirmación de Inscripción: {nombre_evento}"
    msg["From"] = settings.SMTP_USER
    msg["To"] = email_destino

    # Cuerpo HTML
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #23352F;">
        <h1 style="color: #C36B53;">¡Hola, {nombre_usuario}!</h1>
        <p>Te confirmamos que te has inscrito con éxito en la actividad de voluntariado <strong>{nombre_evento}</strong>.</p>
        <p><strong>Detalles del evento:</strong></p>
        <ul>
          <li><strong>Fecha y Hora de Inicio:</strong> {fecha_str}</li>
        </ul>
        <p>¡Muchas gracias por tu tiempo y dedicación solidaria!</p>
        <br/>
        <p>Atentamente,</p>
        <p><strong>El equipo de Casa Monarca</strong></p>
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
        logger.info(
            f"Comunicaciones - Correo de inscripción enviado exitosamente a {email_destino}."
        )
    except smtplib.SMTPException:
        logger.exception(
            f"Comunicaciones - Error SMTP al enviar confirmacion de inscripcion a {email_destino}."
        )
    except Exception:
        logger.exception(
            f"Comunicaciones - Error inesperado al conectar para confirmacion de inscripcion a {email_destino}."
        )
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass


def enviar_correo_asistencia(
    email_destino: str, nombre_usuario: str, nombre_evento: str
) -> None:
    """Envía un correo electrónico real de agradecimiento por participación y

    registro de asistencia a un evento utilizando SMTP.
    """
    logger.info(
        f"Comunicaciones - Preparando correo SMTP de asistencia para {email_destino}..."
    )

    # Crear el mensaje MIME
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"¡Gracias por tu participación en {nombre_evento}!"
    msg["From"] = settings.SMTP_USER
    msg["To"] = email_destino

    # Cuerpo HTML
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #23352F;">
        <h1 style="color: #C36B53;">¡Muchas gracias, {nombre_usuario}!</h1>
        <p>Hemos registrado tu asistencia a la actividad <strong>{nombre_evento}</strong>.</p>
        <p>Tus horas de voluntariado e impacto han sido debidamente acreditadas en la plataforma.</p>
        <p>Valoramos profundamente tu servicio para con la comunidad migrante.</p>
        <br/>
        <p>Atentamente,</p>
        <p><strong>El equipo de Casa Monarca</strong></p>
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
        logger.info(
            f"Comunicaciones - Correo de asistencia enviado exitosamente a {email_destino}."
        )
    except smtplib.SMTPException:
        logger.exception(
            f"Comunicaciones - Error SMTP al enviar agradecimiento de asistencia a {email_destino}."
        )
    except Exception:
        logger.exception(
            f"Comunicaciones - Error inesperado al conectar para agradecimiento de asistencia a {email_destino}."
        )
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass
