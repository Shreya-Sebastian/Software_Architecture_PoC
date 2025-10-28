import subprocess
import time
import os
import sys
import requests
from sensor_simulator import Sensor

# Config

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}/ingest/"

# Choose test: "default", "staggered_failure"
TEST_SCENARIO = "default"

# Params for default
NUM_SENSORS = 5
PHASE_1_NORMAL_DURATION = 10
PHASE_2_DISRUPTION_DURATION = 20
PHASE_3_RESYNC_DURATION = 20
DISCONNECTED_SENSOR_IDS = ["sensor-1", "sensor-3", "sensor-5"]


def cleanup():
    # Removes old buffer files if they exist
    print("--- Running Cleanup ---")
    for file in os.listdir("."):
        if file.startswith("buffer_") and file.endswith(".log"):
            os.remove(file)
            print(f"Removed old buffer file: {file}")


def start_services():
    # Starts the background processes
    print("--- Starting Background Services ---")
    # Start the FastAPI server
    server_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "ingestion_server:app",
            "--host",
            SERVER_HOST,
            "--port",
            str(SERVER_PORT),
        ]
    )
    # Start the consumer
    consumer_process = subprocess.Popen(["python", "consumer.py"])

    # Wait for the server to be ready
    server_ready = False
    print("Waiting for server to be ready...")
    for _ in range(20):  # Try for up to 10 seconds
        try:
            response = requests.get(
                f"http://{SERVER_HOST}:{SERVER_PORT}/health", timeout=0.5
            )
            if response.status_code == 200:
                print("Server is ready.")
                server_ready = True
                break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)  # Wait and retry if not connected

    if not server_ready:
        print("SERVER FAILED TO START.")
        if server_process:
            server_process.terminate()
        if consumer_process:
            consumer_process.terminate()
        return None, None

    print("Services are running.")
    return server_process, consumer_process


def stop_services(server_process, consumer_process):
    # Stops the background services
    print("--- Stopping Services ---")
    if server_process:
        server_process.terminate()
    if consumer_process:
        consumer_process.terminate()
    if server_process:
        server_process.wait()
    if consumer_process:
        consumer_process.wait()
    print("Services Stopped.")


# TEST SCENARIOS
def run_scenario_default(sensors):

    print(
        f"\n--- Default Scenario: ({PHASE_1_NORMAL_DURATION}s -> {PHASE_2_DISRUPTION_DURATION}s -> {PHASE_3_RESYNC_DURATION}s) ---"
    )

    disconnected_sensors = []
    for sensor_id in DISCONNECTED_SENSOR_IDS:
        sensor = next((s for s in sensors if s.sensor_id == sensor_id), None)
        if sensor:
            disconnected_sensors.append(sensor)
        else:
            print(f"Warning: Sensor '{sensor_id}' not found. Will be skipped.")

    if not disconnected_sensors:
        print("No sensors to disconnect. Skipping test.")
        return []

    # Phase 1: Normal Operation
    print(f"\n[Phase 1] Regular Operation ({PHASE_1_NORMAL_DURATION}s)")
    print("All sensors are connected and sending data.")
    time.sleep(PHASE_1_NORMAL_DURATION)

    # Phase 2: Disruption
    print(f"\n[Phase 2] Simulating Disruption ({PHASE_2_DISRUPTION_DURATION}s)")
    print(f"Disconnecting sensors: {[s.sensor_id for s in disconnected_sensors]}")
    for sensor in disconnected_sensors:
        sensor.is_connected = False
    print("Other sensors continue to operate normally.")
    time.sleep(PHASE_2_DISRUPTION_DURATION)

    # Phase 3: Resynchronization
    print(f"\n[Phase 3] Resynchronization ({PHASE_3_RESYNC_DURATION}s)")
    print(f"Reconnecting sensors: {[s.sensor_id for s in disconnected_sensors]}")
    print("Attempting to upload all buffered data (simulating 'thundering herd').")
    for sensor in disconnected_sensors:
        sensor.is_connected = True
    time.sleep(PHASE_3_RESYNC_DURATION)

    # Return a list of sensors to check
    return disconnected_sensors


def run_scenario_staggered_failures(sensors):

    # Tests sensors disconnecting and reconnecting at different overlapping times
    print("\n--- Staggered Failure Test ---")

    s1 = next((s for s in sensors if s.sensor_id == "sensor-1"), None)
    s2 = next((s for s in sensors if s.sensor_id == "sensor-2"), None)

    if not s1 or not s2:
        print("Warning: Test requires at least 2 sensors")
        return []

    disconnected_sensors_for_verification = [s1, s2]

    try:
        print("\n[Time 0s] All sensors connected.")
        time.sleep(5)

        print(f"\n[Time 5s] Disconnecting {s1.sensor_id}")
        s1.is_connected = False
        time.sleep(5)

        print(
            f"\n[Time 10s] Disconnecting {s2.sensor_id}. ({s1.sensor_id} is still offline)"
        )
        s2.is_connected = False
        time.sleep(10)

        print(
            f"\n[Time 20s] Reconnecting {s1.sensor_id}. (Resyncing backlog from T5-T20)."
        )
        s1.is_connected = True
        time.sleep(5)

        print(
            f"\n[Time 25s] Reconnecting {s2.sensor_id}. (Resyncing backlog from T10-T25)."
        )
        print(
            f"({s1.sensor_id} is now sending real-time data alongside {s2.sensor_id}'s backlog)."
        )
        s2.is_connected = True
        time.sleep(10)

        print("\n[Time 35s] Test complete. All sensors online.")

    except KeyboardInterrupt:
        print("\nStaggered test interrupted.")

    return disconnected_sensors_for_verification


def main():
    cleanup()
    server_proc, consumer_proc = start_services()
    if not server_proc:
        print("Failed to start services. Exiting.")
        return

    # Create and start sensors
    print(f"--- Creating and starting {NUM_SENSORS} sensors ---")
    sensors = [
        Sensor(sensor_id=f"sensor-{i}", server_url=SERVER_URL)
        for i in range(1, NUM_SENSORS + 1)
    ]
    for sensor in sensors:
        sensor.start()

    # This list will hold sensors that were disconnected at any point
    disconnected_sensors_for_verification = []

    try:
        if TEST_SCENARIO == "default":
            disconnected_sensors_for_verification = run_scenario_default(sensors)
        elif TEST_SCENARIO == "staggered_failure":
            disconnected_sensors_for_verification = run_scenario_staggered_failures(
                sensors
            )
        else:
            print(f"Unknown TEST_SCENARIO: '{TEST_SCENARIO}'. Halting.")

    except KeyboardInterrupt:
        print("\n Test interrupted by user")
    finally:
        # Stop all sensor threads
        print("\n--- Stopping Sensor Threads ---")
        for sensor in sensors:
            sensor.stop()

        # Stop background services
        stop_services(server_proc, consumer_proc)

        # Final verification
        print("\n--- Final Verification ---")
        if not disconnected_sensors_for_verification:
            print("No sensors were disconnected during the test. Verification skipped.")
        else:
            all_clear = True
            print("Checking buffer files for all disconnected sensors...")
            for sensor in disconnected_sensors_for_verification:
                buffer_file = sensor.buffer_file
                if not os.path.exists(buffer_file):
                    print(
                        f"SUCCESS - Buffer file '{buffer_file}' was successfully cleared."
                    )
                else:
                    try:
                        with open(buffer_file, "r") as f:
                            lines = len(f.readlines())
                        if lines == 0:
                            print(f"SUCCESS - Buffer file '{buffer_file}' is empty.")
                            os.remove(buffer_file)
                        else:
                            print(
                                f"FAILURE - Buffer file '{buffer_file}' still contains {lines} items."
                            )
                            all_clear = False
                    except Exception as e:
                        print(
                            f"ERROR - Could not read buffer file '{buffer_file}': {e}"
                        )
                        all_clear = False

            if all_clear:
                print("\nOverall Result: PASSED")
            else:
                print("\nOverall Result: FAILED")


if __name__ == "__main__":
    main()
