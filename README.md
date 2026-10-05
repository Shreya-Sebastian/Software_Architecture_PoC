# Smarter Home - Data Ingestion PoC

Group project for the Software Architecture course at TU Delft (2025) by Wout Burgers, Levi Raktoe, Shreya Sebastian and Archita Selvam. The architecture report is in `report/` and the team's journals are in `journals/`. The proof of concept in `poc/` is described below.

Proof of concept for fault-tolerant ingestion of IoT sensor data. Simulated sensors buffer readings to a local file while the network is down and resend the backlog in chunks once they reconnect.

A FastAPI server receives readings and publishes them to RabbitMQ; a separate consumer reads them from the queue.

## Components

All code is in `poc/`.

- `ingestion_server.py`: FastAPI server; `POST /ingest/` publishes readings to a durable RabbitMQ queue.
- `consumer.py`: reads messages from the queue and prints them.
- `sensor_simulator.py`: a `Sensor` class that generates readings, buffers them to `buffer_<id>.log` when sending fails, and sends the backlog one chunk per iteration after reconnecting.
- `run_poc_test.py`: starts the server and consumer, runs a disconnect/reconnect scenario and checks that every buffer was emptied.
- `Dockerfile`, `docker-compose.yml`: run the server, consumer and RabbitMQ in containers.

## Run the simulation

Start RabbitMQ:

```shell
docker run -d --name rabbitmq-poc -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

Install the dependencies and run the test script from `poc/`:

```shell
cd poc
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run_poc_test.py
```

The default scenario has three phases: all sensors connected, three sensors disconnected while the others keep sending, and the three reconnected to upload their backlog. Setting `TEST_SCENARIO = "staggered_failure"` in `run_poc_test.py` instead disconnects and reconnects two sensors at overlapping times.

## Run with Docker Compose

```shell
cd poc
docker-compose up --build
```

This starts the server, consumer and RabbitMQ, for manual testing or the scalability tests below.

## Tests

From `poc/`:

```shell
python -m pytest -v error_handling_tests.py    # buffering and resync logic, no server needed
python -m pytest -v scalability_tests.py       # load tests, needs the server running
```
