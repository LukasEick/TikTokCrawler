# Basis: Offizielles Playwright-Image mit Chromium
FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy

# Arbeitsverzeichnis
WORKDIR /app

# Kopiere alle Dateien ins Image
COPY . .

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Stelle sicher, dass Playwright-Browser installiert sind
RUN playwright install --with-deps

# Starte FastAPI mit Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
