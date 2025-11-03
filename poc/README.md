# Smarter Home - Data Ingestion PoC

This is a Proof of Concept (PoC) demonstrating a fault-tolerant, data ingestion architecture for IoT sensors. It simulates sensors that buffer data locally during network outages and resynchronize upon reconnection with the server.

The system uses a FastAPI server for ingestion, RabbitMQ as a message broker, and a separate consumer script for processing.

## Architecture

* **`ingestion_server`**: A FastAPI web server that receives sensor data via a POST request and publishes it to a RabbitMQ queue.
* **`consumer`**: A Python script that connects to RabbitMQ, consumes messages from the queue, and 'processes' them (prints to console).
* **`sensor_simulator`**: A Python class that simulates multiple sensors. Each sensor can be disconnected, at which point it buffers its generated data to a local `.log` file. Upon reconnection, it sends its entire backlog.
* **`run_poc_test`**: An orchestration script that runs a three-phase simulation to test the system's fault tolerance.
* **`rabbitmq`**: The RabbitMQ service, acting as a message broker between the server and the consumer.
* **`Dockerfile` / `docker-compose.yml`**: Files to build and orchestrate the entire application (server, consumer, and message broker) using Docker.
* `.gitlab-ci.yml`: A CI/CD pipeline configured for GitLab to automatically build, test, and style-check the code.

---

### Option 1: Run the Full PoC Simulation Locally

This method runs the entire simulation from your local machine, using the `run_poc_test.py` script to orchestrate all the services. It only uses Docker for the RabbitMQ message broker.

**Prerequisites:**
* Docker
* Python 3.8+

**1. Start the RabbitMQ Service**

In a terminal, run the RabbitMQ container. This will provide the message broker that the local server and consumer will connect to:

```shell
docker run -d --name rabbitmq-poc -p 5672:5672 -p 15672:15672 rabbitmq:3-management
``` 

**2. Set Up Your Python Environment**

From the root of the project, create a virtual environment and install the required dependencies:

```shell
# Create a virtual environment
python -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate

# Activate it (Windows)
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
``` 


In a new terminal, run the run_poc_test.py script (within the poc folder): 

```shell
cd poc
python run_poc_test.py
```
---

The script will execute a three-phase test:

* Normal Operation: All sensors are connected and sending data.

* Disruption: One sensor is disconnected. It begins buffering its data locally while the others continue to send data normally.

* Resynchronization: The disconnected sensor is reconnected. It uploads its entire backlog of buffered data, which is processed alongside the real-time data from other sensors.

---


### Option 2: Run All Services with Docker Compose

This method runs the ingestion server, consumer, and RabbitMQ message broker in containers. This is useful if you want to run the infrastructure and test it manually or with a separate script (like the pytest files).

**Prerequisites:**
* Docker
* Docker Compose

From the root of the project, run:

```shell
docker-compose up --build
```

## Running Unit Tests

The PoC includes unit tests for the sensor logic (`test_sensors.py`).
The error handling test run in isolation and do not require a live RabbitMQ server.

1.  **Run the tests:**
    From within the poc folder, run `python -m pytest -v` to run the unit tests testing error handling and scalability.

```shell
# Test the sensor's error handling and buffering logic
python -m pytest -v error_handling_tests.py

# Run the scalability/load tests (requires the server to be running)
# First, start the services (e.g., with 'docker-compose up')
# Then, in a new terminal:
python -m pytest -v scalability_tests.py
```
---