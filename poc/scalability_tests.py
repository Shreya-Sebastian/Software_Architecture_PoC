import pytest
import requests
import time
import uuid  
import datetime
import random 
from concurrent.futures import ThreadPoolExecutor, as_completed

# config 

SERVER_URL = "http://127.0.0.1:8000/ingest/"
HEALTH_URL = "http://127.0.0.1:8000/health"

# Parameters for the tests
TEST_1_MESSAGES = 5_000      # For large request test
TEST_2_SENSORS = 200         # For concurrency test
TEST_3_SENSORS = 50          # For sustained load test
TEST_3_MESSAGES_PER = 20     # For sustained load test
TEST_3_DELAY_MS = 100        # Delay between messages in sustained test



@pytest.fixture(scope="module")
def server_is_ready():
    # Check if server is running
    try:
        response = requests.get(HEALTH_URL, timeout=2)
        if response.status_code == 200:
            print(f"\nServer is healthy at {HEALTH_URL}. Running scalability tests...")
            yield
        else:
            pytest.skip(
                f"Server at {HEALTH_URL} returned status {response.status_code}."
            )
    except requests.exceptions.ConnectionError:
        pytest.skip(
            f"Server not running at {HEALTH_URL}. "
        )


def generate_reading(sensor_id):
    return {
        "reading_id": str(uuid.uuid4()),
        "sensor_id": sensor_id,
        "type": "temperature", 
        "value": round(random.uniform(18.0, 25.0), 2),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def post_data_worker(payload_list, sensor_id="default"):
    # A function to post a list of readings.
    try:
        response = requests.post(SERVER_URL, json=payload_list, timeout=20)
        return response.status_code
    except Exception as e:
        print(f"Request failed for {sensor_id}: {e}")
        return e


# Scalability Tests

@pytest.mark.usefixtures("server_is_ready")
def test_large_request():
    # Single large request 
    print(f"\nRunning test_large_request({TEST_1_MESSAGES} messages)...")
    sensor_id = "sensor-burst-test"
    
    # Create a large batch of readings
    readings = [generate_reading(sensor_id) for _ in range(TEST_1_MESSAGES)]
    start_time = time.time()
    
    # Send the entire batch in one request
    status = post_data_worker(readings, sensor_id)
    duration = time.time() - start_time
    print(f"Burst test completed in {duration:.2f} seconds.")
    
    # Verify
    assert status == 200, f"Server failed to accept large burst. Status: {status}"


@pytest.mark.usefixtures("server_is_ready")
def test_many_sensors():
    # Many concurrent sensors
    print(f"\nRunning test_many_sensors ({TEST_2_SENSORS} sensors)...")
    
    start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=TEST_2_SENSORS) as executor:
        futures = {}
        for i in range(TEST_2_SENSORS):
            sensor_id = f"sensor-concurrent-{uuid.uuid4()}"
            payload = [generate_reading(sensor_id)]
            f = executor.submit(post_data_worker, payload, sensor_id)
            futures[f] = sensor_id
            
        for future in as_completed(futures):
            results.append(future.result())

    duration = time.time() - start_time
    print(f"Concurrency test completed in {duration:.2f} seconds.")
    
    # Verify
    success_count = sum(1 for r in results if r == 200)
    
    assert success_count == TEST_2_SENSORS, \
        f"Failed requests: {TEST_2_SENSORS - success_count} / {TEST_2_SENSORS}"


@pytest.mark.usefixtures("server_is_ready")
def test_sustained_load():
    # Large load over time
    total_messages = TEST_3_SENSORS * TEST_3_MESSAGES_PER
    print(f"\nRunning test_sustained_load ({TEST_3_SENSORS} sensors, "
          f"{TEST_3_MESSAGES_PER} msg/each = {total_messages} total)...")

    def sensor_worker(sensor_id):
        # worker simulating one sensor sending multiple readings 
        success_count = 0
        for _ in range(TEST_3_MESSAGES_PER):
            payload = [generate_reading(sensor_id)]
            status = post_data_worker(payload, sensor_id)
            if status == 200:
                success_count += 1
            # Simulate time between sensor readings
            time.sleep(TEST_3_DELAY_MS / 1000.0)
        return success_count

    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=TEST_3_SENSORS) as executor:
        futures = [
            executor.submit(sensor_worker, f"sensor-sustained-{uuid.uuid4()}")
            for _ in range(TEST_3_SENSORS)
        ]
        
        for future in as_completed(futures):
            results.append(future.result())

    duration = time.time() - start_time
    print(f"Sustained load test completed in {duration:.2f} seconds.")

    # Verify
    total_successes = sum(results)
    
    assert total_successes == total_messages, \
        f"Failed messages: {total_messages - total_successes} / {total_messages}"