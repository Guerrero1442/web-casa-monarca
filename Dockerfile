FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y activar el vaciado de búfer de salida
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requerimientos de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y configuraciones del backend
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY src/ ./src/
COPY main.py .

# Exponer el puerto 8080 para Google Cloud Run
EXPOSE 8080

# Comando de inicio del servidor ASGI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
