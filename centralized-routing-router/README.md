## Sprint 2 - Routing Calculation, Routing Tables and Forwarding Simulation

### Sprint 2 Objective

The objective of Sprint 2 is to extend the centralized routing system implemented in Sprint 1 by adding shortest path calculation, routing table generation, routing table delivery to routers, local routing table storage in each router, and basic forwarding simulation using Longest Prefix Matching logic.

Sprint 2 covers the following functional requirements:

* **FR-04:** The controller computes shortest paths using Dijkstra's algorithm.
* **FR-05:** The controller generates a routing/forwarding table for each router.
* **FR-06:** The controller sends the corresponding routing table to each router using an `UPDATE_TABLE` message.
* **FR-07:** Each router displays its routing table through the command-line interface.
* **Forwarding simulation:** Each router can use its local routing table to decide whether a simulated packet must be forwarded or dropped.

TLS, heartbeat, FIFO queue management and metrics reporting are not part of Sprint 2. These features are planned for Sprint 3.

---

### Sprint 2 Implemented Flow

The complete Sprint 2 flow is:

```text
Router sends AUTH
        ↓
Controller registers router
        ↓
Router sends NEIGHBORS
        ↓
Controller stores topology in MySQL
        ↓
Controller builds active topology graph
        ↓
Controller runs Dijkstra
        ↓
Controller generates routing tables
        ↓
Controller stores calculated routes in MySQL
        ↓
Controller sends UPDATE_TABLE to each router
        ↓
Router stores routing table locally as JSON
        ↓
Router displays its routing table
        ↓
Router simulates packet forwarding using the received table
```

---

### Database Tables Used in Sprint 2

Sprint 2 uses the Sprint 1 tables:

```text
routers
enlaces
eventos
```

And adds:

```text
rutas_calculadas
```

If the table `rutas_calculadas` does not exist, it can be created with:

```sql
CREATE TABLE IF NOT EXISTS rutas_calculadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    router_origen_id INT NOT NULL,
    router_destino_id INT NOT NULL,
    prefijo_destino VARCHAR(50) NOT NULL,
    longitud_prefijo INT NOT NULL,
    siguiente_salto VARCHAR(50) NOT NULL,
    costo INT NOT NULL,
    ruta_completa TEXT NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    fecha_calculo DATETIME NOT NULL,
    FOREIGN KEY (router_origen_id) REFERENCES routers(id),
    FOREIGN KEY (router_destino_id) REFERENCES routers(id)
);
```

---

### Sprint 2 Demo Topology

The Sprint 2 validation topology is:

```text
R1 -> R2 cost 10
R1 -> R3 cost 5
R2 -> R3 cost 1
```

Expected active links in MySQL:

```sql
SELECT * FROM enlaces;
```

Expected result:

```text
R1 -> R2 cost 10
R1 -> R3 cost 5
R2 -> R3 cost 1
```

---

### How to Run the Controller

Open a terminal in:

```text
centralized-routing-controller
```

Run:

```powershell
python -m app.main
```

Expected result:

```text
Controller started successfully.
Connection to MySQL database established.
Controller server listening on 0.0.0.0:6000
```

The controller must remain running while routers connect.

---

### How to Run the Routers

Open a terminal in:

```text
centralized-routing-router
```

Run router R1:

```powershell
python -m app.main router_r1.json
```

Run router R2:

```powershell
python -m app.main router_r2.json
```

Run router R3:

```powershell
python -m app.main router_r3.json
```

Each router sends:

```text
AUTH
NEIGHBORS
```

Then it receives:

```text
AUTH_OK
NEIGHBORS_OK
UPDATE_TABLE
```

---

### Expected Routing Table for R1

With the validation topology, R1 should receive:

```text
Routing table for router R1
------------------------------------------------------------------------------
Destination    Prefix         Len     Next hop       Cost    Path
------------------------------------------------------------------------------
R2             R2             32      R2             10      R1 -> R2
R3             R3             32      R3             5       R1 -> R3
------------------------------------------------------------------------------
```

---

### Expected Routing Table for R2

With the validation topology, R2 should receive:

```text
Routing table for router R2
------------------------------------------------------------------------------
Destination    Prefix         Len     Next hop       Cost    Path
------------------------------------------------------------------------------
R3             R3             32      R3             1       R2 -> R3
------------------------------------------------------------------------------
```

---

### Expected Routing Table for R3

With the validation topology, R3 may receive an empty table if it has no outgoing links:

```text
Routing table for router R3
------------------------------------------------------------------------------
Destination    Prefix         Len     Next hop       Cost    Path
------------------------------------------------------------------------------
No routing entries available.
------------------------------------------------------------------------------
```

---

### Local Router Persistence

Each router stores its received routing table locally in JSON format.

Expected files:

```text
centralized-routing-router/data/routing_table_R1.json
centralized-routing-router/data/routing_table_R2.json
centralized-routing-router/data/routing_table_R3.json
```

These files represent lightweight local router persistence for Sprint 2.

---

### How to Verify Calculated Routes in MySQL

Run:

```sql
SELECT * FROM rutas_calculadas;
```

Expected calculated routes:

```text
R1 -> R2 | next hop R2 | cost 10 | path ["R1", "R2"]
R1 -> R3 | next hop R3 | cost 5  | path ["R1", "R3"]
R2 -> R3 | next hop R3 | cost 1  | path ["R2", "R3"]
```

A more readable query is:

```sql
SELECT
    rc.id,
    ro.nombre AS router_origen,
    rd.nombre AS router_destino,
    rc.prefijo_destino,
    rc.longitud_prefijo,
    rc.siguiente_salto,
    rc.costo,
    rc.ruta_completa,
    rc.estado,
    rc.fecha_calculo
FROM rutas_calculadas rc
INNER JOIN routers ro ON rc.router_origen_id = ro.id
INNER JOIN routers rd ON rc.router_destino_id = rd.id;
```

---

### Forwarding Simulation

After the routers have received and stored their routing tables, forwarding can be simulated from the router application.

Open a terminal in:

```text
centralized-routing-router
```

Run:

```powershell
python -m app.cli.packet_sim_cli R1 R2
```

Expected result:

```text
Forwarding simulation at router R1
------------------------------------------------------------------------
Destination: R2
Action:      FORWARD
Next hop:    R2
Match:       R2/32
Cost:        10
Path:        R1 -> R2
------------------------------------------------------------------------
```

Run:

```powershell
python -m app.cli.packet_sim_cli R1 R3
```

Expected result:

```text
Forwarding simulation at router R1
------------------------------------------------------------------------
Destination: R3
Action:      FORWARD
Next hop:    R3
Match:       R3/32
Cost:        5
Path:        R1 -> R3
------------------------------------------------------------------------
```

Run:

```powershell
python -m app.cli.packet_sim_cli R2 R3
```

Expected result:

```text
Forwarding simulation at router R2
------------------------------------------------------------------------
Destination: R3
Action:      FORWARD
Next hop:    R3
Match:       R3/32
Cost:        1
Path:        R2 -> R3
------------------------------------------------------------------------
```

Run:

```powershell
python -m app.cli.packet_sim_cli R3 R1
```

Expected result:

```text
Forwarding simulation at router R3
------------------------------------------------------------------------
Destination: R1
Action:      DROP
Reason:      No matching route found.
------------------------------------------------------------------------
```

---

### Sprint 2 Evidence Checklist

The following evidence should be saved for Sprint 2:

```text
[ ] Controller terminal showing AUTH, NEIGHBORS and UPDATE_TABLE messages.
[ ] R1 terminal showing received routing table with routes to R2 and R3.
[ ] R2 terminal showing received routing table with route to R3.
[ ] R3 terminal showing empty table or no available routes.
[ ] MySQL table enlaces with R1->R2, R1->R3 and R2->R3.
[ ] MySQL table rutas_calculadas with R1->R2, R1->R3 and R2->R3.
[ ] Local JSON files routing_table_R1.json, routing_table_R2.json and routing_table_R3.json.
[ ] Forwarding simulation R1 -> R2 with FORWARD.
[ ] Forwarding simulation R1 -> R3 with FORWARD.
[ ] Forwarding simulation R2 -> R3 with FORWARD.
[ ] Forwarding simulation R3 -> R1 with DROP.
```

---

### Sprint 2 Status

Sprint 2 is considered functionally completed when:

```text
[OK] The controller computes shortest paths using Dijkstra.
[OK] The controller generates routing tables.
[OK] The controller stores calculated routes in MySQL.
[OK] The controller sends UPDATE_TABLE messages to routers.
[OK] Routers store their routing tables locally.
[OK] Routers display their routing tables in the terminal.
[OK] Routers simulate forwarding decisions using their local routing table.
```
