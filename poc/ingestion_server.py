from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pika
from typing import List
from datetime import datetime
import uuid
import os


# Pydantic Models for Data Validation
class SensorReading(BaseModel):
    reading_id: uuid.UUID
    sensor_id: str
    type: str
    value: float
    timestamp: datetime


# RabbitMQ Connection Setup
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "sensor_data_queue"


def get_rabbitmq_connection():
    # Establishes a connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    return connection


# FastAPI Application
app = FastAPI(title="Smarter Home Ingestion Service")


@app.on_event("startup")
def startup_event():
    # On startup, ensure the RabbitMQ queue exists
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        # Declare a durable queue
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        connection.close()
        print("INFO: RabbitMQ queue 'sensor_data_queue' is ready.")
    except pika.exceptions.AMQPConnectionError:
        print("ERROR: Could not connect to RabbitMQ. Please ensure it's running.")
        exit(1)


@app.post("/ingest/")
def ingest_data(readings: List[SensorReading]):
    # Receives a list of sensor readings and publishes them to the message queue.

    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
    except pika.exceptions.AMQPConnectionError:
        raise HTTPException(
            status_code=503, detail="Service unavailable: Message queue is down."
        )

    messages_published = 0
    for reading in readings:
        message_body = reading.model_dump_json()
        try:
            channel.basic_publish(
                exchange="",
                routing_key=QUEUE_NAME,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                ),
            )
            messages_published += 1
        except Exception as e:
            print(f"ERROR: Failed to publish message: {e}")

    connection.close()
    return {"status": "accepted", "published_count": messages_published}


@app.get("/health")
def health_check():
    return {"status": "ok"}
