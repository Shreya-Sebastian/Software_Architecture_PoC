FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file 
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of code
COPY . .

# Expose the port the FastAPI server runs on
EXPOSE 8000

# Default command
CMD ["uvicorn", "ingestion_server:app", "--host", "0.0.0.0", "--port", "8000"]
