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
    - Upon reconnection, it sends the buffered data.
    """
    def __init__(self, sensor_id: str, server_url: str, data_type: str = "temperature"):
        self.sensor_id = sensor_id
        self.server_url = server_url
        self.data_type = data_type
        self.buffer_file = f"buffer_{self.sensor_id}.log"
        self.buffer = self._load_buffer()
        self.is_connected = True  # Controlled externally by the test script
        self._stop_event = threading.Event()
        self.CHUNK_SIZE = 100

    def _load_buffer(self) -> deque:
        # Loads pending data from the buffer file on startup
        if not os.path.exists(self.buffer_file):
            return deque()
        with open(self.buffer_file, 'r') as f:
            readings = [json.loads(line) for line in f]
            print(f"[{self.sensor_id}] INFO: Loaded {len(readings)} readings from buffer.")
            return deque(readings)

    def _save_to_buffer(self, reading: dict):
        # Appends a single reading to the buffer and the file
        self.buffer.append(reading)
        with open(self.buffer_file, 'a') as f:
            f.write(json.dumps(reading) + '\n')

    def _clear_buffer_file(self):
        # Clears the buffer file after successful transmission
        if os.path.exists(self.buffer_file):
            os.remove(self.buffer_file)

    def generate_reading(self) -> dict:
        # Generates a new sensor reading
        return {
            "reading_id": str(uuid.uuid4()),
            "sensor_id": self.sensor_id,
            "type": self.data_type,
            "value": round(random.uniform(18.0, 25.0), 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def _send_data(self, readings: list) -> bool:
        # Tries to send a batch of readings to the server
        try:
            response = requests.post(
                self.server_url,
                json=readings,
                headers={"Content-Type": "application/json"},
                timeout=2.0
            )
            response.raise_for_status() # This will raise an HTTPError for 4xx/5xx responses
            print(f"[{self.sensor_id}] INFO: Successfully sent {len(readings)} readings. Server says: {response.json()['status']}")
            return True
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            print(f"[{self.sensor_id}] ERROR: Could not connect to server. {e.__class__.__name__}")
            return False

    def run(self):
        # Main loop for the sensor thread
        while not self._stop_event.is_set():
            # Generate new data
            current_reading = self.generate_reading()
            send_current_reading_now = True  # Flag to control sending the new reading

            if self.is_connected:
                # When connected, try to send buffer first (resynchronize)
                if self.buffer:
                    print(f"[{self.sensor_id}] INFO: Connection restored. Attempting to send {len(self.buffer)} buffered readings in chunks...")
                    
                    all_chunks_sent = True
                    # Work on a temporary copy
                    temp_buffer = list(self.buffer) 
                    
                    while temp_buffer:
                        # Create a chunk from the temp buffer
                        chunk = temp_buffer[:self.CHUNK_SIZE]
                        
                        if self._send_data(chunk):
                            print(f"[{self.sensor_id}] INFO: Sent chunk of {len(chunk)}. {len(temp_buffer)-len(chunk)} remaining in queue.")
                            # Send the temp buffer only on success
                            del temp_buffer[:self.CHUNK_SIZE]
                        else:
                            print(f"[{self.sensor_id}] WARNING: Failed to send chunk. Aborting buffer send.")
                            all_chunks_sent = False
                            self.is_connected = False
                            break # Stop trying to send chunks
                    
                    if all_chunks_sent:
                        print(f"[{self.sensor_id}] INFO: Buffer successfully sent and cleared.")
                        self.buffer.clear() # Clear in-memory
                        self._clear_buffer_file() # Clear on-disk
                    else:
                        # A chunk failed, don't send the current reading.
                        send_current_reading_now = False

                # If connected and buffer sending was succesful
                if send_current_reading_now and self.is_connected:
                    # Send current data or give warning if sending fails
                    if not self._send_data([current_reading]):
                        print(f"[{self.sensor_id}] WARNING: Connection lost. Buffering new reading.")
                        self.is_connected = False
                    
            # If not connected
            if not self.is_connected:
                # Buffer the current reading.
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