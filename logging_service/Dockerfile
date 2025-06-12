# Utilise une image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système pour MySQL client
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    default-mysql-client \
    netcat-openbsd \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Port exposé (modifié selon le service via docker-compose)
EXPOSE 8000

# Point d’entrée par défaut (écrasé par docker-compose `command`)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
