# Smarter Home - Data Ingestion PoC

This is a Proof of Concept demonstrating a fault-tolerant data ingestion architecture for IoT sensors. It simulates sensors that buffer data locally during network outages and resynchronize upon reconnection with the server.

---

## How to Run

### Prerequisites
* Python 3.8+
* A running RabbitMQ instance.

---

> With Docker, you can start a RabbitMQ container for this purpose with the following command. It will be accessible on `localhost`.
> ```shell
> docker run -d --hostname my-rabbit --name poc-rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management
> ```

1.  **Install dependencies:**
    ```shell
    pip install fastapi uvicorn pika requests
    ```

2.  **Run the simulation:**
    ```shell
    python run_poc_test.py
    ```

python run_poc_test.py
The script will execute a three-phase test:

* Normal Operation: All sensors are connected and sending data.

* Disruption: One sensor is disconnected. It begins buffering its data locally while the others continue to send data normally.

* Resynchronization: The disconnected sensor is reconnected. It uploads its entire backlog of buffered data, which is processed alongside the real-time data from other sensors.
