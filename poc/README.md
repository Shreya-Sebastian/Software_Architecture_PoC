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

## How to Run

This method runs the ingestion server, consumer, and RabbitMQ message broker in containers. You then run the test script from your host machine to interact with the containerized server.

### Prerequisites
* Docker
* Docker Compose
* Python 3.8+ (for running the test script locally)


From the root of the project, run:

```shell
docker-compose up --build
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

## Running Unit Tests

The PoC includes unit tests for the sensor logic (`test_sensors.py`).
These tests run in isolation and do not require a live RabbitMQ server.

1.  **Run the tests:**
    From within the poc folder, run `python -m pytest -v`.

    ```shell
    python -m pytest -v
    ```
