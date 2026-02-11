FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
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
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install wkhtmltopdf based on architecture
RUN ARCH=$(dpkg --print-architecture) && \
    echo "Detected architecture: $ARCH" && \
    if [ "$ARCH" = "amd64" ]; then \
        wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb && \
        apt-get install -y ./wkhtmltox_0.12.6.1-3.bookworm_amd64.deb && \
        rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb; \
    elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then \
        wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_arm64.deb && \
        apt-get install -y ./wkhtmltox_0.12.6.1-3.bookworm_arm64.deb && \
        rm wkhtmltox_0.12.6.1-3.bookworm_arm64.deb; \
    elif [ "$ARCH" = "armhf" ]; then \
        wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_armhf.deb && \
        apt-get install -y ./wkhtmltox_0.12.6.1-3.bookworm_armhf.deb && \
        rm wkhtmltox_0.12.6.1-3.bookworm_armhf.deb; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for generated documents
RUN mkdir -p /app/generated_docs

# Copy startup script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Use the startup script
ENTRYPOINT ["/app/docker-entrypoint.sh"]