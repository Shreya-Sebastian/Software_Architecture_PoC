import pika
import time
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "sensor_data_queue"


def main():
    # Connects to RabbitMQ and consumes messages from the queue
    print("INFO: [Consumer] Waiting for messages.")

    # Connection loop
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)

            def callback(ch, method, properties, body):
                # Callback function to process a message
                data = json.loads(body)
                sensor_id = data.get("sensor_id", "N/A")
                timestamp = data.get("timestamp", "N/A")
                print(
                    f"  [Consumer] <-- Received data from [{sensor_id}] at {timestamp}"
                )
                ch.basic_ack(
                    delivery_tag=method.delivery_tag
                )  # Acknowledge message processing

            # Ensure balanced dispatching
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

            # Start consuming
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError:
            print(
                "ERROR: [Consumer] Connection to RabbitMQ failed. Retrying in 5 seconds..."
            )
            time.sleep(5)
        except KeyboardInterrupt:
            print("INFO: [Consumer] Shutting down.")
            break
        except Exception as e:
            print(f"ERROR: [Consumer] An unexpected error occurred: {e}. Restarting...")
            time.sleep(5)


if __name__ == "__main__":
    main()
