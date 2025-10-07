import subprocess
import time
import os
import signal
import sys
import requests
from sensor_simulator import Sensor

#Config
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/ingest/"

NUM_SENSORS = 3
DISCONNECTED_SENSOR_ID = "sensor-1"

#Test Durations (seconds)
PHASE_1_NORMAL_DURATION = 10
PHASE_2_DISRUPTION_DURATION = 15
PHASE_3_RESYNC_DURATION = 20

def cleanup():
    # Removes old buffer files
    print("Running Cleanup")
    for file in os.listdir("."):
        if file.startswith("buffer_") and file.endswith(".log"):
            os.remove(file)
            print(f"Removed old buffer file: {file}")

def start_services():
    #Starts the ingestion server and consumer as background processes
    print("Starting Background Services")
    # Start the FastAPI server
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "ingestion_server:app", "--host", SERVER_HOST, "--port", str(SERVER_PORT)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    # Start the consumer
    consumer_process = subprocess.Popen(
        ["python", "consumer.py"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    
    # Wait for the server to be ready
    server_ready = False
    for _ in range(20):  # Try for up to 10 seconds
        try:
            response = requests.get(f"http://{SERVER_HOST}:{SERVER_PORT}/health", timeout=0.5)
            if response.status_code == 200:
                print("Server is ready")
                server_ready = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5) # Wait and retry
    
    if not server_ready:
        print("server not ready yet")
        return None, None 
    
    return server_process, consumer_process

def stop_services(server_process, consumer_process):
    #Stops the background services
    print("\nStopping Background Services")

    server_process.terminate()
    consumer_process.terminate()
    server_process.wait()
    consumer_process.wait()
    print("Services Stopped")


def main():
    cleanup()
    server_proc, consumer_proc = start_services()

    # Create and start sensors
    sensors = [
        Sensor(sensor_id=f"sensor-{i}", server_url=SERVER_URL)
        for i in range(1, NUM_SENSORS + 1)
    ]
    disconnected_sensor = next(s for s in sensors if s.sensor_id == DISCONNECTED_SENSOR_ID)

    for sensor in sensors:
        sensor.start()

    try:
        print(f"\n Regular Operation ({PHASE_1_NORMAL_DURATION}s)")
        print("All sensors are connected and sending data.")
        time.sleep(PHASE_1_NORMAL_DURATION)

        print(f"\n Simulating Disruption ({PHASE_2_DISRUPTION_DURATION}s)")
        print(f"Disconnecting sensor {disconnected_sensor.sensor_id}")
        disconnected_sensor.is_connected = False
        print("Other sensors continue to operate normally.")
        time.sleep(PHASE_2_DISRUPTION_DURATION)

        print(f"\n Resynchronization & Load Test ({PHASE_3_RESYNC_DURATION}s)")
        print(f"Reconnecting sensor {disconnected_sensor.sensor_id}")
        print("Attempting to upload sensor's buffered data.")
        print("Historical data is processed alongside real-time data from others.")
        disconnected_sensor.is_connected = True
        time.sleep(PHASE_3_RESYNC_DURATION)

    except KeyboardInterrupt:
        print("\n Test interrupted by user")
    finally:
        # Stop all sensor threads
        for sensor in sensors:
            sensor.stop()
        
        # Stop background services
        stop_services(server_proc, consumer_proc)

        # Final check
        print("\n Final PoC Verification")
        buffer_file = disconnected_sensor.buffer_file
        if not os.path.exists(buffer_file):
            print(f"SUCCESS - Buffer file '{buffer_file}' was successfully cleared.")
        else:
            with open(buffer_file, 'r') as f:
                lines = len(f.readlines())
            if lines == 0:
                 print(f"SUCCESS - Buffer file '{buffer_file}' is empty.")
                 os.remove(buffer_file)
            else:
                 print(f"FAILURE - Buffer file '{buffer_file}' still contains {lines} items.")

if __name__ == "__main__":
    main()