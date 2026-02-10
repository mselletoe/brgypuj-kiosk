FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wget \
    fontconfig \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    xfonts-75dpi \
    xfonts-base \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf from Debian repositories (ARM compatible)
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for generated documents
RUN mkdir -p /app/generated_docs

# Expose port
EXPOSE 8000

# Startup script: wait for DB, run migrations, start server
CMD sh -c "\
    echo 'Waiting for database...' && \
    sleep 5 && \
    echo 'Running migrations...' && \
    alembic upgrade head && \
    echo 'Starting server...' && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000"