FROM python:3.11-slim

# Instalar herramientas básicas del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git \
    && rm -rf /var/lib/apt/lists/*

# Configurar usuario sin privilegios (estándar para Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Instalar dependencias de Python
COPY --chown=user requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copiar el código del proyecto
COPY --chown=user . /app

# Asegurar permisos de escritura para la generación de imágenes
RUN mkdir -p /app/static/generated

# Puerto estándar expuesto por Hugging Face Spaces
EXPOSE 7860

# Ejecutar con Gunicorn en producción (puerto dinámico $PORT para Render / 7860 para Spaces)
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-7860} app:app --workers 1 --threads 2 --max-requests 100 --max-requests-jitter 20 --timeout 120"]
