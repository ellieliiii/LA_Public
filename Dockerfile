# Use the official Python image for your desired Python version.
FROM python:3.9-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr.
ENV PYTHONUNBUFFERED=1

# Install system dependencies, including SQLite.
RUN apt-get update && apt-get install -y sqlite3

WORKDIR /app

# Create a non-privileged user.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the source code into the container.
COPY . .

# Switch to the non-privileged user.
USER appuser

# Copy the source code and the 'shared-db' directory into the container.
COPY --chown=appuser:appuser . .

# Run the Flask app.
CMD ["python3", "app.py"]
