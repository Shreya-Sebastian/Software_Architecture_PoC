FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code into the container
COPY . .

# Expose the port the FastAPI server runs on
EXPOSE 8000

# Default command to run
CMD ["uvicorn", "ingestion_server:app", "--host", "0.0.0.0", "--port", "8000"]