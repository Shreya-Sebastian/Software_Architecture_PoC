import requests
import json
import time
import threading
import uuid
from datetime import datetime, timezone
import random
import os
from collections import deque


class Sensor:
    """
    A simulated sensor with 'store and forward' capability.
    - Generates data periodically.
    - Tries to send data (and any existing backlog) to the server.
    - If sending fails, it buffers data to a local file.
    - Upon reconnection, it sends the buffered data one chunk at a time.
    """

    def __init__(self, sensor_id: str, server_url: str, data_type: str = "temperature"):
        self.sensor_id = sensor_id
        self.server_url = server_url
        self.data_type = data_type
        self.buffer_file = f"buffer_{self.sensor_id}.log"
        self.buffer = self._load_buffer()
        self.is_connected = True  # Controlled externally by the test script
        self._stop_event = threading.Event()
        self.CHUNK_SIZE = 25

    def _load_buffer(self) -> deque:
        # Loads pending data from the buffer file on startup
        if not os.path.exists(self.buffer_file):
            return deque()
        with open(self.buffer_file, "r") as f:
            readings = [json.loads(line) for line in f]
            print(
                f"[{self.sensor_id}] INFO: Loaded {len(readings)} readings from buffer."
            )
            return deque(readings)

    def _save_to_buffer(self, reading: dict):
        # Appends a single reading to the buffer and the file
        self.buffer.append(reading)
        with open(self.buffer_file, "a") as f:
            f.write(json.dumps(reading) + "\n")

    def _persist_buffer(self):
        # Rewrites the buffer file from the in-memory deque.
        if not self.buffer:
            # If deque is empty, just remove the file
            if os.path.exists(self.buffer_file):
                os.remove(self.buffer_file)
            return

        # Rewrite the file with the remaining buffer contents
        with open(self.buffer_file, "w") as f:
            for reading in self.buffer:
                f.write(json.dumps(reading) + "\n")

    def generate_reading(self) -> dict:
        # Generates a new sensor reading
        return {
            "reading_id": str(uuid.uuid4()),
            "sensor_id": self.sensor_id,
            "type": self.data_type,
            "value": round(random.uniform(18.0, 25.0), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _send_data(self, readings: list) -> bool:
        # Tries to send a batch of readings to the server
        try:
            response = requests.post(
                self.server_url,
                json=readings,
                headers={"Content-Type": "application/json"},
                timeout=2.0,
            )
            response.raise_for_status()  # This will raise an HTTPError for 4xx/5xx responses
            print(
                f"[{self.sensor_id}] INFO: Successfully sent {len(readings)} readings. Server says: {response.json()['status']}"
            )
            return True
        except (
            requests.exceptions.RequestException,
            requests.exceptions.HTTPError,
        ) as e:
            print(
                f"[{self.sensor_id}] ERROR: Could not connect to server. {e.__class__.__name__}"
            )
            return False

    def run(self):
        # Main loop for the sensor thread
        while not self._stop_event.is_set():
            # Generate new data
            current_reading = self.generate_reading()
            # Flag
            buffer_current_reading = False

            if self.is_connected:
                # When connected try to send one chunk from buffer first
                if self.buffer:
                    print(
                        f"[{self.sensor_id}] INFO: Connection OK. Attempting to send 1 chunk of {min(len(self.buffer), self.CHUNK_SIZE)}/{len(self.buffer)} readings..."
                    )

                    # Create chunk from the front of the deque (don't remove yet)
                    chunk = [self.buffer[i] for i in range(min(len(self.buffer), self.CHUNK_SIZE))]

                    if self._send_data(chunk):
                        # Remove sent items from in-memory buffer
                        for _ in range(len(chunk)):
                            self.buffer.popleft()
                        print(
                            f"[{self.sensor_id}] INFO: Chunk sent. {len(self.buffer)} readings remain."
                        )
                        # Persist this change to the file
                        self._persist_buffer()
                    else:
                        # Stop trying for this loop
                        print(
                            f"[{self.sensor_id}] WARNING: Failed to send chunk. Aborting."
                        )
                        self.is_connected = False
                        # Buffer the current_reading
                        buffer_current_reading = True

                # If still connected (buffer was empty or chunk send was OK)
                if self.is_connected:
                    # try to send the current reading.
                    if not self._send_data([current_reading]):
                        print(
                            f"[{self.sensor_id}] WARNING: Connection lost. Buffering new reading."
                        )
                        self.is_connected = False
                        buffer_current_reading = True

            else:  # Was not connected from the start
                print(f"[{self.sensor_id}] OFFLINE: Buffering reading.")
                buffer_current_reading = True

            # Final buffering check
            if buffer_current_reading:
                print(f"[{self.sensor_id}] OFFLINE: Buffering reading.")
                self._save_to_buffer(current_reading)

            # Wait before generating next reading
            time.sleep(random.uniform(1.0, 2.0))

    def start(self):
        # Starts the sensor's run loop in a new thread
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        # Stops the sensor's run loop
        self._stop_event.set()
        self.thread.join()
        print(f"[{self.sensor_id}] INFO: Sensor stopped.")