# NETCORE - Centralized Routing Management System

## 1. Project Information

**Course:** Informatics for Telecommunications  
**Program:** Electronic Engineering and Telecommunications  
**Project:** Centralized Routing System  
**Team:** NetCore Team  

**Team members:**

- Eider Daniel Fernandez — Developer + Tester
- Isabella Perez Hoyos — Documenter + Developer

---

## 2. General Description

NETCORE is a centralized routing management system developed in Python.

The system is composed of:

- A centralized controller application.
- Multiple distributed router applications.
- A MySQL database used by the controller.
- Local persistence files used by each router.
- TCP + TLS communication.
- JSON-based messages.
- Dijkstra shortest path calculation.
- Routing table generation and delivery.
- Longest Prefix Matching forwarding simulation.
- Heartbeat-based fault detection.
- FIFO queue management with tail drop.
- Periodic metrics reporting.
- Command-line tools for administration and testing.

The controller works as the Control Plane.  
The routers work as the Data Plane.

Routers register with the controller, send their neighbors and link costs, receive routing tables, simulate packet forwarding, report metrics, and send heartbeat messages.

---

## 3. Main Implemented Requirements

### Sprint 1 - Communication Base and Topology

Implemented:

- Router registration using `AUTH`.
- Authentication response using `AUTH_OK` or `AUTH_FAIL`.
- Neighbor information exchange using `NEIGHBORS`.
- Topology storage in MySQL.
- TCP server in the controller.
- TCP client in the routers.
- JSON message format.
- Controller database tables for routers, links, routes, events and metrics.

Status:

```text
Sprint 1: Completed
```

---

### Sprint 2 - Dijkstra, Routing Tables and Forwarding

Implemented:

- Dijkstra shortest path calculation.
- Routing table generation for each router.
- Routing table delivery using `UPDATE_TABLE`.
- Router-side local storage of forwarding tables.
- Routing table visualization in the terminal.
- Longest Prefix Matching forwarding simulation.
- Packet forwarding CLI.

Status:

```text
Sprint 2: Completed
```

---

### Sprint 3 - Security, Fault Detection, Metrics and Final Delivery

Implemented:

- TLS encryption over TCP sockets.
- Token-based authentication.
- Link cost update from administrator CLI.
- Route recalculation after link cost changes.
- Heartbeat messages.
- Router inactivity detection.
- Route recalculation after router inactivity.
- FIFO queue with configurable max size.
- Tail drop when the queue is full.
- Periodic metrics reporting:
  - queue size
  - packets forwarded
  - packets discarded
- Centralized network status CLI.
- Final integration with five routers: R1, R2, R3, R4 and R5.

Status:

```text
Sprint 3: Completed
```

---

## 4. Technologies Used

- Python 3
- MySQL 8.0
- TCP sockets
- TLS with Python `ssl`
- JSON
- Python `unittest`
- PowerShell / terminal execution
- MVC + DAO architecture

---

## 5. Project Structure

```text
centralized-routing-system/
│
├── centralized-routing-controller/
│   ├── app/
│   │   ├── cli/
│   │   ├── controllers/
│   │   ├── dao/
│   │   ├── models/
│   │   ├── network/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── certificates/
│   │   ├── generate_certificates.py
│   │   ├── server.crt
│   │   └── server.key
│   │
│   └── tests/
│
└── centralized-routing-router/
    ├── app/
    │   ├── cli/
    │   ├── config/
    │   ├── controllers/
    │   ├── dao/
    │   ├── models/
    │   ├── network/
    │   ├── services/
    │   ├── views/
    │   └── main.py
    │
    ├── certificates/
    │   └── server.crt
    │
    └── tests/
```

---

## 6. Database Setup

The controller uses the database:

```sql
centralized_routing_controller
```

Required main tables:

- `routers`
- `enlaces`
- `rutas_calculadas`
- `eventos`
- `metricas_router`
- `metricas_globales`

The table `metricas_globales` stores the documented Sprint 3 metrics:

```sql
CREATE TABLE IF NOT EXISTS metricas_globales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    router_id INT NOT NULL,
    router_nombre VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    tamano_cola INT NOT NULL,
    paquetes_enviados INT NOT NULL,
    paquetes_descartados INT NOT NULL,
    FOREIGN KEY (router_id) REFERENCES routers(id)
);
```

---

## 7. TLS Certificates

The system uses TLS over TCP.

To generate certificates, go to the controller folder:

```powershell
cd "D:\Universidad\SEXTO SEMESTRE\centralized-routing-system\centralized-routing-system\centralized-routing-controller"
python .\certificates\generate_certificates.py
```

Then copy the certificate to the router project:

```powershell
cd "D:\Universidad\SEXTO SEMESTRE\centralized-routing-system\centralized-routing-system\centralized-routing-router"
mkdir certificates
copy "..\centralized-routing-controller\certificates\server.crt" ".\certificates\server.crt"
```

---

## 8. How to Run the System

### 8.1 Start the Controller

Open a terminal in:

```text
centralized-routing-controller
```

Run:

```powershell
python -m app.main
```

Expected output:

```text
Controller started successfully.
Controller TLS server listening on 0.0.0.0:6000
```

---

### 8.2 Start Router R1

Open a new terminal in:

```text
centralized-routing-router
```

Run:

```powershell
python -m app.main router_r1.json
```

Expected output:

```text
Router R1 started successfully.
Connected to controller using TLS at 127.0.0.1:6000
AUTH message sent to controller.
Response from controller: {'type': 'AUTH_OK', ...}
NEIGHBORS message sent to controller.
Message from controller: {'type': 'UPDATE_TABLE', ...}
Starting HEARTBEAT/METRICS loop.
```

---

### 8.3 Start Router R2

```powershell
python -m app.main router_r2.json
```

---

### 8.4 Start Router R3

```powershell
python -m app.main router_r3.json
```

---

### 8.5 Start Router R4

```powershell
python -m app.main router_r4.json
```

---

### 8.6 Start Router R5

```powershell
python -m app.main router_r5.json
```

---

## 9. Final Five-Router Topology

The final demo topology is:

```text
R1 -> R2 cost 10
R1 -> R3 cost 5

R2 -> R3 cost 1
R2 -> R4 cost 4

R3 -> R4 cost 2
R3 -> R5 cost 8

R4 -> R5 cost 3
R4 -> R1 cost 7

R5 -> R1 cost 6
R5 -> R2 cost 2
```

This topology allows all routers to be reachable and allows Dijkstra to generate routing tables for the complete network.

---

## 10. Administrative CLI Commands

### 10.1 View Network Status

From the controller folder:

```powershell
python -m app.cli.network_status_cli
```

Expected output:

```text
NETCORE - Network Status

Router    IP              Port    Status      Last activity         Uptime    HB      Routes  Queue   Forwarded   Discarded   Last metrics
R1        127.0.0.1       5001    activo      ...                   ...       ...     ...     0       2           1           ...
R2        127.0.0.1       5002    activo      ...                   -         -       -       0       0           0           ...
R3        127.0.0.1       5003    activo      ...                   -         -       -       0       0           0           ...
R4        127.0.0.1       5004    activo      ...                   -         -       -       0       0           0           ...
R5        127.0.0.1       5005    activo      ...                   -         -       -       0       0           0           ...
```

---

### 10.2 Update Link Cost and Recalculate Routes

From the controller folder:

```powershell
python -m app.cli.link_cost_cli R1 R2 10
```

Expected result:

```text
Link cost update result:
{
    "type": "LINK_COST_UPDATED",
    "origin_router": "R1",
    "destination_router": "R2",
    "new_cost": 10
}

Routing recalculation result:
{
    "type": "ROUTING_TABLES_STORED",
    "saved_entries": 20,
    ...
}
```

With five routers, `saved_entries` should be:

```text
20
```

because each of the five routers has routes to the other four routers:

```text
5 routers × 4 destinations = 20 routes
```

---

### 10.3 Check Router Health and Recalculate After Failure

Stop one router manually using:

```text
CTRL + C
```

Wait more than 15 seconds.

Then run from the controller folder:

```powershell
python -m app.cli.router_health_cli 15
```

Expected output:

```json
{
    "type": "ROUTER_HEALTH_CHECK_COMPLETED",
    "timeout_seconds": 15,
    "inactive_routers_marked": 1,
    "route_recalculation_triggered": true,
    "routing_result": {
        "type": "ROUTING_TABLES_STORED",
        "saved_entries": 1
    }
}
```

The exact number of saved entries may vary depending on the active topology.

---

## 11. Packet Forwarding Simulation

From the router folder:

```powershell
python -m app.cli.packet_sim_cli R1 R2
python -m app.cli.packet_sim_cli R1 R3
python -m app.cli.packet_sim_cli R1 R9
```

Expected behavior:

- Packets to known destinations are forwarded.
- Unknown destinations are discarded.
- Metrics are updated:
  - `packets_forwarded`
  - `packets_discarded`
  - `queue_size`

Then check from the controller folder:

```powershell
python -m app.cli.network_status_cli
```

Expected metrics example:

```text
Queue = 0
Forwarded = 2
Discarded = 1
```

---

## 12. Automated Tests

### 12.1 Controller Tests

From:

```text
centralized-routing-controller
```

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Expected result:

```text
Ran 55 tests
OK
```

---

### 12.2 Router Tests

From:

```text
centralized-routing-router
```

Run:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 13. Requirement Coverage Matrix

| Requirement | Description | Status |
|---|---|---|
| FR-01 | Router registration | Completed |
| FR-02 | Neighbor information exchange | Completed |
| FR-03 | Topology storage | Completed |
| FR-04 | Dijkstra route computation | Completed |
| FR-05 | Routing table generation | Completed |
| FR-06 | Routing table delivery | Completed |
| FR-07 | Routing table visualization | Completed |
| FR-08 | Link cost update and recalculation | Completed |
| FR-09 | Event logging | Completed |
| FR-10 | TLS encryption | Completed |
| FR-11 | Heartbeat fault detection and recalculation | Completed |
| FR-12 | FIFO queue and tail drop | Completed |
| FR-13 | Metrics reporting | Completed |
| NFR-01 | Python implementation | Completed |
| NFR-02 | Modular MVC + DAO design | Completed |
| NFR-03 | JSON messages | Completed |
| NFR-04 | CLI execution | Completed |
| NFR-05 | Error handling | Completed |
| NFR-06 | Five-router scalability demo | Completed |
| NFR-07 | Maintainability | Completed |
| NFR-08 | Testability | Completed |
| NFR-09 | TLS security | Completed |
| NFR-10 | Availability and route recalculation | Completed |

---

## 14. Demonstration Script

Recommended order for the final presentation:

1. Start MySQL.
2. Start the controller.
3. Start routers R1, R2, R3, R4 and R5.
4. Show TLS connection in router terminal.
5. Show `AUTH_OK`.
6. Show `NEIGHBORS_OK`.
7. Show `UPDATE_TABLE`.
8. Show routing table displayed in router terminal.
9. Run:

```powershell
python -m app.cli.network_status_cli
```

10. Show all five routers active.
11. Run:

```powershell
python -m app.cli.link_cost_cli R1 R2 10
```

12. Show route recalculation with `saved_entries: 20`.
13. Simulate packets:

```powershell
python -m app.cli.packet_sim_cli R1 R2
python -m app.cli.packet_sim_cli R1 R3
python -m app.cli.packet_sim_cli R1 R9
```

14. Show metrics:

```powershell
python -m app.cli.network_status_cli
```

15. Stop one router.
16. Run:

```powershell
python -m app.cli.router_health_cli 15
```

17. Show router marked inactive and route recalculation triggered.
18. Run automated tests:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 15. Notes About Implementation Decisions

### Heartbeat Design

The original design describes heartbeat messages sent by the controller and acknowledged by routers.

In this implementation, each router periodically sends a `HEARTBEAT` message to the controller, and the controller responds with `HEARTBEAT_OK`.

This approach still satisfies the monitoring objective because the controller updates the router's last activity timestamp and detects failures when heartbeats stop arriving.

### Local Router Persistence

The original architecture describes local router storage.  
This implementation uses lightweight local JSON persistence for routing tables, queue state and metrics counters.

This decision keeps the system simple, portable and stable for educational execution while preserving the required behavior.

### Metrics

The implemented documented metrics are:

```text
queue_size
packets_forwarded
packets_discarded
```

The controller stores them in:

```text
metricas_globales
```

The network status CLI displays:

```text
Queue
Forwarded
Discarded
```

---

## 16. Final Status

The project implements the required centralized routing system with:

```text
[OK] Controller application
[OK] Router applications
[OK] TCP + TLS communication
[OK] JSON messages
[OK] Token authentication
[OK] Topology storage
[OK] Dijkstra shortest path calculation
[OK] Routing table generation
[OK] Routing table delivery
[OK] Longest Prefix Matching forwarding simulation
[OK] Link cost update and route recalculation
[OK] Heartbeat fault detection
[OK] FIFO queue and tail drop
[OK] Metrics reporting and storage
[OK] Five-router integration demo
[OK] Automated tests
```

Final project status:

```text
Sprint 1: Completed
Sprint 2: Completed
Sprint 3: Completed
```