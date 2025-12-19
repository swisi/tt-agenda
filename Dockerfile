# Verwende Python 3.12 als Basis-Image
FROM python:3.12-slim

# Setze Arbeitsverzeichnis
WORKDIR /app

# Installiere System-Dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Kopiere Requirements
COPY requirements.txt .

# Installiere Python-Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere Anwendungscode
COPY . .

# Erstelle Verzeichnis für die Datenbank
RUN mkdir -p /app/instance

# Setze Umgebungsvariablen
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Exponiere Port 5000
EXPOSE 5000

# Starte die Anwendung
CMD ["python", "app.py"]
