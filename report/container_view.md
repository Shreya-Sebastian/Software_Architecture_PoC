## Container view

In this section we show the components of the Smart Home system. The diagram below shows the system is composed of two parts: One part on the cloud and one part on a local hub. The different boxes inside the cloud depict different microservices. Inside the local hub, the different boxes depict plug-ins. The cylinders depict databases. As per the microkernel architecture, plug-ins in the local hub only communicate with the core.

![Container View](images/container.png)

Cloud building blocks:

| **Building block** | **Description** |
| ------------------ | --------------- |
| API gateway | Entry point for all requests to the cloud and can forward requests to the local hub. |
| Notifications | Responsible for notifying the user directly on their mobile device. |
| Routine detection | Reads the sensor data inside the database and infers routines from them. |
| Database | Cloud storage that holds user information for authentication and sensor data for routine detection. |

Local hub building blocks:

| **Building block** | **Description** |
| ------------------ | --------------- |
| Core | Core of the microkernel architecture of the local hub. Calls other plug-ins when needed. |
| Cloud synchronization | Responsible for offloading sensor data to the cloud database. |
| Automation | Runs configured automations. |
| Device communication | Responsible for building and interpreting requests to and from smart home devices. |
| Authentication | Makes sure only authenticated users can interact with the Smarter Home. |
| Automation suggestion | Interprets detected routine to suggest automations to the user. |
| User Management | Manages authentication levels of all users of the Smarter Home. |
| Network Module | Entry point for all requests to the local hub. |
| Database | Holds information on the connected devices, users of the Smarter Home, configured automations and sensor data before it is moved to cloud storage. |

Besides detecting routines, the cloud acts as an intermediary between remote users and the local hub, allowing users to interact with their devices from outside their home. Similarly, the local hub may notify the users via the cloud. Users may also interact with their local hub directly if they are on the same local network. 