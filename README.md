# Smarter Home — Architecture & Ingestion-Pipeline PoC

> Course project for **TU Delft Software Architecture**. Team-designed smart-home platform that learns household routines from IoT sensor data and suggests user-approved automations. The full architecture is in `report/`; this PoC validates the highest-risk structural claim — that the ingestion pipeline survives intermittent network conditions and high concurrent load.

The PoC is **not** a complete smart-home implementation. Automation execution, ML routine detection, the cloud microservices, and the React UI are described in the report but not built here.

**Team:** Wout Burgers, Levi Raktoe, Shreya Sebastian, Archita Selvam.

## Quality goals that drove the architecture

Two tensions shaped the structural decisions (full list of seven attributes in `report/` §6):

- **Privacy vs. correctness.** Routines need data; data inside the home is the central privacy concern. Resolved by keeping sensitive data on a local hub with user inspection/deletion rights.
- **Security vs. extensibility.** Every connected device is an attack surface. Resolved by a microkernel + plug-in design on the local hub.

## Architecture decisions

Each decision is recorded as a Y-statement in `report/` §8.

- **Hybrid local/cloud split.** Local hub holds sensitive data and runs automations; cloud handles remote access, auth, updates, notifications. Cost: complexity and reliance on local hardware.
- **Microkernel for the local hub, microservices for the cloud.** Microkernel for plug-in extensibility under a security boundary; microservices for independent scaling of remote-access, auth, and notification.
- **REST for telemetry ingestion** over MQTT, WebSockets, or UDP. Chosen for firewall-friendliness and edge validation, accepting higher per-message overhead.
- **Decoupled ingestion via message broker.** FastAPI ingestion server validates and forwards; RabbitMQ buffers; consumer acknowledges after processing. **This is the feature the PoC validates.**
- **Store-and-forward at the sensor.** Sensors buffer to a local file when the server is unreachable, forward in chunks on reconnect. Addresses both data-loss and resync-spike scalability in one mechanism.

## Tech stack

| Concern | Choice | Why |
|---|---|---|
| Ingestion backend | **FastAPI** | High-throughput async HTTP, integrated Pydantic validation |
| Message broker | **RabbitMQ** | Reliable delivery, decouples ingestion from processing |
| Data validation | **Pydantic** | Schema validation at the entry point |
| Deployment | **Docker** | Per-component isolation |
| Database (planned) | PostgreSQL + TimescaleDB | Relational + time-series for sensor data |
| Analytics (planned) | NumPy / pandas / scikit-learn | Interpretable routine detection |
| Device integration (planned) | Home Assistant | Broad device support, Python-extensible |
| Frontend (planned) | React | Mature ecosystem |
| Auth (planned) | Keycloak | Role-based access, OAuth/OIDC |

**Bold** rows are implemented in the PoC. The rest are justified in the report but not built.

## What the PoC validates

Three test categories in `poc/` (see `report/` §11):

1. **Phased fault-tolerance** (`run_poc_test.py`) — three-phase script: normal → disconnect one sensor → reconnect. Passes if the local buffer ends empty and no messages are lost.
2. **Store-and-forward unit tests** (`error_handling_tests.py`) — buffer init on existing file, buffering on connection/server failure, chunked sending on resync, mid-resync recovery (failed chunk preserved, not deleted).
3. **Scalability tests** (`scalability_tests.py`) — single very large request (long-offline resync), high concurrency (many sensors at once), sustained load (consumer keeps up so the queue does not grow unbounded).

The deliberate scope is to validate the **structural claims**: decoupling, store-and-forward, horizontal consumer scaling. End-to-end smart-home behavior is not built in this PoC.

## Repository structure

- `ingestion_server/` — FastAPI server: receives sensor POSTs, publishes to RabbitMQ
- `consumer/` — consumes from the queue, processes messages (prints to console in this PoC)
- `sensor_simulator/` — sensors with store-and-forward to local `.log` files
- `poc/run_poc_test.py` — three-phase orchestration script
- `poc/error_handling_tests.py`, `poc/scalability_tests.py`, `poc/test_sensors.py` — pytest suites
- `Dockerfile`, `docker-compose.yml` — packaging
- `.gitlab-ci.yml` — original GitLab CI (preserved from the source repo)

## Running it

**Prerequisites:** Docker, Python 3.8+.

### Option 1 — local Python, RabbitMQ in Docker

```bash
docker run -d --name rabbitmq-poc -p 5672:5672 -p 15672:15672 rabbitmq:3-management

python -m venv venv && source venv/bin/activate     # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

cd poc && python run_poc_test.py
```

### Option 2 — everything in Docker

```bash
docker-compose up --build
```

### Tests

```bash
# From poc/
python -m pytest -v error_handling_tests.py    # no live server needed
python -m pytest -v scalability_tests.py       # requires services running (Option 2)
```

## What we'd do differently

- The PoC consumer only acknowledges messages — it does not process them. Validating that the queue is drained at line-rate is enough to prove the scalability claim, but it is not a real consumer.
- No authentication is integrated into the ingestion path. Anything that talks to the ingestion server is trusted. The architecture calls for the auth service to gate ingestion; the PoC defers that integration.
- REST was chosen over MQTT for firewall-friendliness and observability. For high-frequency sensor streams at hundreds of devices per home, this decision deserves a second look.
- The microkernel/microservices split is justified at the structural level but the cloud microservices are not implemented. The cloud-side claims rest on the architectural argument in the report, not on running code.
- Scalability tests run on a developer machine, not against a representative production deployment. The numbers prove the pipeline does not collapse under stress, not that it meets a specific SLA.
