# Use the official Python base image
FROM python:3.12-slim

WORKDIR /app

# Install the necessary system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
    
# Copy the poetry.lock and pyproject.toml files to the container
COPY pyproject.toml poetry.lock /app/


# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi


# Copy the rest of the application code to the container
COPY src /app/src

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]