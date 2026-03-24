# Dev container para siscom-api (puerto 8000)
FROM python:3.11-slim

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libpq5 \
    procps \
    lsof \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Script para arrancar uvicorn en background (disponible aunque /app se monte después)
COPY .devcontainer/start-uvicorn.sh /usr/local/bin/start-siscom-uvicorn.sh
RUN chmod +x /usr/local/bin/start-siscom-uvicorn.sh

# Código se monta desde el workspace; exponer puerto 8000
EXPOSE 8000

# La app se inicia con postStartCommand/postAttachCommand en devcontainer.json
# Mantener el contenedor vivo para desarrollo
CMD ["sleep", "infinity"]
