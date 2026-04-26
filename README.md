# Smarter Home — Architecture & Ingestion-Pipeline PoC


## What this is
> Course project for **TU Delft Software Architecture course**.
> The course assignment was to design a software system end-to-end: stakeholder analysis → quality attributes → architecture → a working PoC that validates the architecture's most non-trivial claim. **Smarter Home** is the team's chosen system: a smart-home platform that *learns* household routines from IoT sensor data and suggests user-approved automations, designed for users without deep technical expertise. The full architecture report is in `report/` and is the primary deliverable; the PoC in `poc/` validates one specific architectural claim.

The PoC is **not** a complete smart-home implementation. It is a focused validation of the ingestion pipeline: that the architecture can ingest sensor data without loss under intermittent network conditions and remain stable under high concurrent load. This is the architectural claim where the design risk concentrates, so the PoC was scoped to test exactly that.

## Quality goals that drove the architecture

The design balances seven quality attributes. Two tensions shaped the structural decisions:

- **Privacy vs. correctness.** Routines can only be detected from data, but data collection inside the home is the central privacy concern. Resolved by keeping sensitive data on a local hub and giving the user inspection/deletion rights over recorded data.
- **Security vs. extensibility.** Every connected device is an attack surface. Resolved by a microkernel-with-plug-ins design on the local hub: new devices integrate through a stable plug-in interface that the core enforces, rather than by direct access to the core.

## Architecture decisions

The report records each decision as a Y-statement (`report/` §8.1.2, §8.2.6). Key decisions:

- **Hybrid local/cloud split** rather than pure cloud or pure local. The local hub holds all sensitive data and runs automations; the cloud handles remote access, authentication, update delivery, and notifications. The trade-off accepted is increased system complexity and dependence on local hardware.
- **Microkernel for the local hub, microservices for the cloud.** Microkernel was chosen for the local hub for plug-in extensibility (new IoT devices over time) under a security boundary. Microservices was chosen for the cloud for independent scalability and availability of remote-access, auth, and notification services.
- **REST for telemetry ingestion** over MQTT, WebSockets, or UDP. REST was selected for firewall-friendliness, simpler validation at the edge, and clear audit trails, accepting the higher per-message overhead vs MQTT.
- **Decoupled ingestion via message broker.** A lightweight FastAPI ingestion server validates and forwards; RabbitMQ buffers; consumer processes acknowledge after successful processing. This decoupling is the architectural feature the PoC was specifically built to validate.
- **Store-and-forward at the sensor.** Sensors buffer to a local file when the ingestion server is unreachable, and forward in chunks on reconnect. This addresses both data loss during network outages and the resync-spike scalability concern in a single mechanism.

## Tech stack

Open-source components selected in `report/` §9:

| Concern             | Choice                       | Why                                                       |
|---------------------|------------------------------|-----------------------------------------------------------|
| Ingestion backend   | **FastAPI**                  | High-throughput async HTTP, integrated Pydantic validation |
| Message broker      | **RabbitMQ**                 | Reliable delivery, decouples ingestion from processing    |
| Data validation     | **Pydantic**                 | Schema validation at the entry point of the pipeline      |
| Database (planned)  | **PostgreSQL + TimescaleDB** | Relational + time-series for sensor data                  |
| Analytics (planned) | **NumPy / pandas / scikit-learn** | Interpretable models for routine detection           |
| Device integration  | **Home Assistant**           | Active community, broad device support, Python-extensible |
| Frontend            | **React**                    | Mature ecosystem, team familiarity                        |
| Auth                | **Keycloak**                 | Role-based access, OAuth/OIDC                             |
| Deployment          | **Docker**                   | Per-component isolation, reproducible test environments   |

The PoC implements the **bold** rows. The other rows are architectural choices justified in the report but not built in the PoC.

## What the PoC actually validates

The PoC simulates the ingestion path under three test categories (`poc/`, see `report/` §11):

1. **Phased fault-tolerance test.** A scripted three-phase run: normal operation → one sensor is disconnected and buffers locally → sensor reconnects and replays its backlog. Pass/fail is decided by checking the local buffer is empty at the end and that no messages were dropped.
2. **Store-and-forward unit tests.** Four tests on the sensor's offline behavior in isolation: buffer initialization on startup with an existing file, buffering on connection or server failure, chunked sending on resync, and recovery from a server failure mid-resync (the failed chunk is preserved, not deleted).
3. **Scalability tests against the full pipeline.** Three load profiles: a single very large request (resync of a long-offline sensor), high concurrency (many sensors firing simultaneously), and sustained load (long-running stream confirming the consumer keeps up with the ingestion server so the queue does not grow unbounded).

Reviewers familiar with this kind of project: the deliberate scope is to validate the **structural claims** (decoupling, store-and-forward, horizontal consumer scaling). End-to-end smart-home behavior — automation execution, ML routine detection, the cloud microservices, the React UI — is **not** built in this PoC. Those are described in the report and left for future work.

## Running the PoC

[CONFIRM the actual commands. Likely shape:]

```bash
# Start the pipeline (ingestion server + RabbitMQ + consumer)
docker-compose up --build

# Run the phased fault-tolerance test
[CONFIRM script name, e.g. python poc/run_phased_test.py]

# Run unit tests on the sensor's store-and-forward logic
[CONFIRM, e.g. pytest poc/tests/test_sensor.py]

# Run scalability tests against the running pipeline
[CONFIRM, e.g. pytest poc/scalability_tests.py]
```

[CONFIRM any required env vars, ports exposed, or RabbitMQ credentials.]

## What we'd do differently

This is the section technical reviewers actually read. Honest reflections from the report and PoC scope:

- **The PoC consumer only acknowledges messages — it doesn't process them.** Validating that the queue is consumed at line-rate is enough to prove the scalability claim, but it is not a real consumer. A reviewer should read `report/` §11 + "Future Work" together: the PoC scope is *narrower* than the architecture it validates.
- **No authentication is integrated into the ingestion path.** Anything that talks to the ingestion server is trusted. The architecture calls for the auth service to gate ingestion; the PoC defers that integration.
- **REST was chosen over MQTT primarily for firewall-friendliness and observability**, but for high-frequency sensor streams MQTT is the better fit. If the system grew to hundreds of sensors per home, this decision would deserve a second look.
- **The microkernel/microservices split is justified at the structural level but the cloud microservices are not implemented.** The cloud-side claims (independent scaling of remote-access, auth, notifications) rest on the architectural argument in the report, not on running code.
- **Single-classroom-of-the-team-laptop validation.** Scalability tests run on a developer machine, not against a representative production deployment. The numbers prove the pipeline does not collapse under stress, not that it meets a specific SLA.

## Repository layout

[CONFIRM the actual top-level structure when finalizing. Based on standard course structure:]

- `poc/` — proof-of-concept implementation (FastAPI ingestion server, RabbitMQ consumer, simulated sensors, test scripts)
- `report/` — written architecture report (the primary deliverable)
- `journals/` — engineering journals documenting weekly design decisions
- `appendix/` — functional requirements (Appendix A) and supporting material
- `images/` — diagrams referenced in the report (power-interest, domain model, C4 views, runtime view, PoC architecture)
- `Dockerfile`, `docker-compose.yml` — service packaging
- `.gitlab-ci.yml` — original CI pipeline configuration (preserved from GitLab origin)

## License

[CONFIRM — likely no license (academic) or MIT if the team agrees on a permissive choice for portfolio publication.]

## Acknowledgements

Course staff at TU Delft for the [Software Architecture, course code TBC] course. The open-source projects this PoC depends on — FastAPI, RabbitMQ, Pydantic, and Docker — without which the PoC would not have been buildable in the time available. Thanks also to teammates Wout Burgers, Levi Raktoe, and Archita Selvam for the joint design and implementation work documented in the report.
