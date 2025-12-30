# Stage 1: Build environment (optional for Python)
FROM python:3.12-slim AS build

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Expose port
EXPOSE 8000

# Command to run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]