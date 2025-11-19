FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .

# Instalar dependencias del sistema necesarias para psycopg2 + WeasyPrint
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev libffi-dev libcairo2 libpango-1.0-0 shared-mime-info wget ca-certificates && \
    # intentar instalar variantes de libgdk-pixbuf disponibles en distintas distros
    (apt-get install -y --no-install-recommends libgdk-pixbuf2.0-0 || apt-get install -y --no-install-recommends libgdk-pixbuf-xlib-2.0-0 || apt-get install -y --no-install-recommends libgdk-pixbuf-x11-2.0-0) && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential && apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
