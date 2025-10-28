import pytest
import os
import json
import requests
from collections import deque

# Import the class to test
from sensor_simulator import Sensor

# Constants for testing
TEST_SENSOR_ID = "sensor-unit-test"
TEST_URL = "http://fake-server.com/ingest/"
TEST_BUFFER_FILE = f"buffer_{TEST_SENSOR_ID}.log"


@pytest.fixture
def cleanup_buffer():
    # Fixture to ensure the buffer file is deleted after each test.
    yield
    if os.path.exists(TEST_BUFFER_FILE):
        os.remove(TEST_BUFFER_FILE)


@pytest.fixture
def sensor(cleanup_buffer, mocker):
    # Provides a Sensor instance for testing.
    s = Sensor(TEST_SENSOR_ID, TEST_URL)

    # Mock time.sleep to also set the stop event.
    # This makes sensor.run() execute exactly one loop.
    def sleep_and_stop(*args, **kwargs):
        s._stop_event.set()  # Set stop event to exit loop after this iteration

    # Apply the mock with the side_effect
    mocker.patch("sensor_simulator.time.sleep", side_effect=sleep_and_stop)

    yield s


# Test Cases


# Tests if the sensor correctly loads pre-existing buffer file on init.
def test_sensor_init_loads_buffer(cleanup_buffer):
    # Create a fake buffer file
    reading1 = {"id": 1, "ts": "2025-01-01T00:00:00Z"}
    reading2 = {"id": 2, "ts": "2025-01-01T00:00:01Z"}
    with open(TEST_BUFFER_FILE, "w") as f:
        f.write(json.dumps(reading1) + "\n")
        f.write(json.dumps(reading2) + "\n")

    # Create sensor
    s = Sensor(TEST_SENSOR_ID, TEST_URL)

    assert len(s.buffer) == 2
    assert s.buffer[0] == reading1
    assert s.buffer[1] == reading2


@pytest.mark.parametrize(
    "error_response",
    [
        {"exc": requests.exceptions.RequestException},  # Test connection error
        {"status_code": 503},  # Test server error
    ],
)
# Tests error handling - Sensor should buffer data if the server is unreachable or returns a 5xx error.
def test_sensor_buffers_on_failure(sensor, requests_mock, error_response):

    # Mock the server to be down
    requests_mock.post(TEST_URL, **error_response)

    sensor.is_connected = True
    assert len(sensor.buffer) == 0

    # Run one iteration
    sensor.run()

    # Verify it buffered the data
    assert len(sensor.buffer) == 1
    assert os.path.exists(TEST_BUFFER_FILE)
    assert sensor.is_connected is False  # Should set itself to offline


# Tests scalability - verifies that sensor sends its buffer in chunks.
def test_sensor_sends_buffer_in_chunks(sensor, requests_mock, mocker):

    sensor.CHUNK_SIZE = 100

    # Create a fake buffer of 250 items
    fake_readings = [{"id": i} for i in range(250)]
    sensor.buffer = deque(fake_readings)

    # Mock a new reading
    new_reading = {"id": 999}
    mocker.patch.object(sensor, "generate_reading", return_value=new_reading)

    # Mock the server to always succeed
    requests_mock.post(TEST_URL, status_code=200, json={"status": "accepted"})

    sensor.is_connected = True
    sensor.run()  # Run one iteration

    # Verify 2 requests were made:
    # 1 for the first chunk (100) and 1 for the new reading.
    assert requests_mock.call_count == 2

    # Verify the payloads of the requests
    assert len(requests_mock.request_history[0].json()) == 100
    assert requests_mock.request_history[0].json()[0] == {"id": 0}
    assert requests_mock.request_history[1].json() == [new_reading]

    # Verify the buffer was partially cleared from memory
    assert len(sensor.buffer) == 150  # 250 - 100 = 150
    assert sensor.buffer[0] == {"id": 100}  # Check first remaining item
    assert os.path.exists(TEST_BUFFER_FILE)  # File should still exist


# Tests error handling during resync - If a chunk fails, it should stop, not clear the buffer, and re-buffer.
def test_sensor_stops_chunking_on_failure(sensor, requests_mock, mocker):

    sensor.CHUNK_SIZE = 100

    # Create a fake buffer of 250 items
    fake_readings = [{"id": i} for i in range(250)]
    sensor.buffer = deque(fake_readings)

    # Mock a new reading
    new_reading = {"id": 999}
    mocker.patch.object(sensor, "generate_reading", return_value=new_reading)

    # Mock server: fail on the first attempt
    requests_mock.post(TEST_URL, status_code=503)

    sensor.is_connected = True
    sensor.run()  # Run one iteration

    # Verify it tried to send one chunk, failed, and stopped
    assert requests_mock.call_count == 1
    assert len(requests_mock.request_history[0].json()) == 100

    # Verify it did not clear the buffer
    assert len(sensor.buffer) == 251  # Original 250 + the new reading
    assert sensor.buffer[0] == fake_readings[0]  # Verify original data is still there
    assert sensor.buffer[-1] == new_reading  # Verify new reading was added to the end

    # Verify it buffered the new reading
    assert sensor.buffer[-1] == new_reading  # New reading added to end
    assert len(sensor.buffer) == 251  # Total buffer size
    assert sensor.is_connected is False  # Set itself offline
