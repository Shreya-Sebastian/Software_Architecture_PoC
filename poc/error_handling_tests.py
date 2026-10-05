import pytest
import os
import json
import requests
from collections import deque

from sensor_simulator import Sensor

TEST_SENSOR_ID = "sensor-unit-test"
TEST_URL = "http://fake-server.com/ingest/"
TEST_BUFFER_FILE = f"buffer_{TEST_SENSOR_ID}.log"


@pytest.fixture
def cleanup_buffer():
    yield
    if os.path.exists(TEST_BUFFER_FILE):
        os.remove(TEST_BUFFER_FILE)


@pytest.fixture
def sensor(cleanup_buffer, mocker):
    s = Sensor(TEST_SENSOR_ID, TEST_URL)

    # sleep sets the stop event, so sensor.run() does exactly one iteration
    def sleep_and_stop(*args, **kwargs):
        s._stop_event.set()

    mocker.patch("sensor_simulator.time.sleep", side_effect=sleep_and_stop)

    yield s


def test_sensor_init_loads_buffer(cleanup_buffer):
    """A buffer file left from an earlier run is loaded on init."""
    reading1 = {"id": 1, "ts": "2025-01-01T00:00:00Z"}
    reading2 = {"id": 2, "ts": "2025-01-01T00:00:01Z"}
    with open(TEST_BUFFER_FILE, "w") as f:
        f.write(json.dumps(reading1) + "\n")
        f.write(json.dumps(reading2) + "\n")

    s = Sensor(TEST_SENSOR_ID, TEST_URL)

    assert len(s.buffer) == 2
    assert s.buffer[0] == reading1
    assert s.buffer[1] == reading2


@pytest.mark.parametrize(
    "error_response",
    [
        {"exc": requests.exceptions.RequestException},
        {"status_code": 503},
    ],
)
def test_sensor_buffers_on_failure(sensor, requests_mock, error_response):
    """The sensor buffers its reading and goes offline when the server is unreachable or returns 5xx."""
    requests_mock.post(TEST_URL, **error_response)

    sensor.is_connected = True
    assert len(sensor.buffer) == 0

    sensor.run()

    assert len(sensor.buffer) == 1
    assert os.path.exists(TEST_BUFFER_FILE)
    assert sensor.is_connected is False


def test_sensor_sends_buffer_in_chunks(sensor, requests_mock, mocker):
    """The backlog is sent one chunk per iteration, followed by the new reading."""
    sensor.CHUNK_SIZE = 100

    fake_readings = [{"id": i} for i in range(250)]
    sensor.buffer = deque(fake_readings)

    new_reading = {"id": 999}
    mocker.patch.object(sensor, "generate_reading", return_value=new_reading)

    requests_mock.post(TEST_URL, status_code=200, json={"status": "accepted"})

    sensor.is_connected = True
    sensor.run()

    assert requests_mock.call_count == 2
    assert len(requests_mock.request_history[0].json()) == 100
    assert requests_mock.request_history[0].json()[0] == {"id": 0}
    assert requests_mock.request_history[1].json() == [new_reading]

    assert len(sensor.buffer) == 150
    assert sensor.buffer[0] == {"id": 100}
    assert os.path.exists(TEST_BUFFER_FILE)


def test_sensor_stops_chunking_on_failure(sensor, requests_mock, mocker):
    """If a chunk fails, sending stops, the buffer is kept and the new reading is buffered too."""
    sensor.CHUNK_SIZE = 100

    fake_readings = [{"id": i} for i in range(250)]
    sensor.buffer = deque(fake_readings)

    new_reading = {"id": 999}
    mocker.patch.object(sensor, "generate_reading", return_value=new_reading)

    requests_mock.post(TEST_URL, status_code=503)

    sensor.is_connected = True
    sensor.run()

    assert requests_mock.call_count == 1
    assert len(requests_mock.request_history[0].json()) == 100

    assert len(sensor.buffer) == 251
    assert sensor.buffer[0] == fake_readings[0]
    assert sensor.buffer[-1] == new_reading
    assert sensor.is_connected is False
