# Use an official lightweight Python image as a base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's build cache
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port your FastAPI server runs on
EXPOSE 8000

# This is the default command to run when the container starts.
# We'll run the ingestion server by default.
# Note: We use 0.0.0.0 to make it accessible outside the container.
CMD ["uvicorn", "ingestion_server:app", "--host", "0.0.0.0", "--port", "8000"]
