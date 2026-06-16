from test_support import ControllerDatabaseTestCase

from app.controllers.router_registry_controller import RouterRegistryController
from app.controllers.routing_controller import RoutingController
from app.controllers.topology_controller import TopologyController


class TestRoutingControllerSprint2(ControllerDatabaseTestCase):
    """
    Sprint 2 integration-style tests for the controller.

    These tests validate:
    - Active topology graph from MySQL.
    - Dijkstra execution over stored topology.
    - Routing table generation.
    - Persistence in rutas_calculadas.

    They use TEST_ routers only and clean all generated data.
    """

    def register_test_router(self, router_id, port):
        registry_controller = RouterRegistryController()

        message = {
            "type": "AUTH",
            "router_id": router_id,
            "ip": "127.0.0.1",
            "port": port,
            "token": f"token_{router_id.lower()}"
        }

        response = registry_controller.register_router(message)

        self.assertEqual(response["type"], "AUTH_OK")
        self.assertEqual(response["router_id"], router_id)

    def register_test_topology(self):
        self.register_test_router("TEST_R1", 5101)
        self.register_test_router("TEST_R2", 5102)
        self.register_test_router("TEST_R3", 5103)

        topology_controller = TopologyController()

        r1_neighbors = {
            "type": "NEIGHBORS",
            "router_id": "TEST_R1",
            "neighbors": [
                {
                    "neighbor_id": "TEST_R2",
                    "cost": 10
                },
                {
                    "neighbor_id": "TEST_R3",
                    "cost": 5
                }
            ]
        }

        r2_neighbors = {
            "type": "NEIGHBORS",
            "router_id": "TEST_R2",
            "neighbors": [
                {
                    "neighbor_id": "TEST_R3",
                    "cost": 1
                }
            ]
        }

        r1_response = topology_controller.register_neighbors(r1_neighbors)
        r2_response = topology_controller.register_neighbors(r2_neighbors)

        self.assertEqual(r1_response["type"], "NEIGHBORS_OK")
        self.assertEqual(r2_response["type"], "NEIGHBORS_OK")

    def test_get_active_topology_graph_from_database(self):
        self.register_test_topology()

        routing_controller = RoutingController()
        graph = routing_controller.get_active_topology_graph()

        self.assertIn("TEST_R1", graph)
        self.assertIn("TEST_R2", graph)
        self.assertIn("TEST_R3", graph)

        self.assertIn(
            {
                "to": "TEST_R2",
                "cost": 10
            },
            graph["TEST_R1"]
        )

        self.assertIn(
            {
                "to": "TEST_R3",
                "cost": 5
            },
            graph["TEST_R1"]
        )

        self.assertIn(
            {
                "to": "TEST_R3",
                "cost": 1
            },
            graph["TEST_R2"]
        )

    def test_generate_routing_tables_from_database_topology(self):
        self.register_test_topology()

        routing_controller = RoutingController()
        response = routing_controller.generate_routing_tables()

        self.assertEqual(response["type"], "ROUTING_TABLES_GENERATED")

        routing_tables = response["routing_tables"]

        self.assertIn("TEST_R1", routing_tables)
        self.assertIn("TEST_R2", routing_tables)
        self.assertIn("TEST_R3", routing_tables)

        r1_entries = routing_tables["TEST_R1"]["entries"]
        r2_entries = routing_tables["TEST_R2"]["entries"]
        r3_entries = routing_tables["TEST_R3"]["entries"]

        self.assertEqual(len(r1_entries), 2)
        self.assertEqual(len(r2_entries), 1)
        self.assertEqual(len(r3_entries), 0)

        r2_route_from_r1 = next(
            entry for entry in r1_entries
            if entry["destination_router"] == "TEST_R2"
        )

        r3_route_from_r1 = next(
            entry for entry in r1_entries
            if entry["destination_router"] == "TEST_R3"
        )

        self.assertEqual(r2_route_from_r1["next_hop"], "TEST_R2")
        self.assertEqual(r2_route_from_r1["cost"], 10)

        self.assertEqual(r3_route_from_r1["next_hop"], "TEST_R3")
        self.assertEqual(r3_route_from_r1["cost"], 5)

        r3_route_from_r2 = r2_entries[0]

        self.assertEqual(r3_route_from_r2["destination_router"], "TEST_R3")
        self.assertEqual(r3_route_from_r2["next_hop"], "TEST_R3")
        self.assertEqual(r3_route_from_r2["cost"], 1)

    def test_calculate_and_store_routing_tables_persists_routes(self):
        self.register_test_topology()

        routing_controller = RoutingController()
        response = routing_controller.calculate_and_store_routing_tables()

        self.assertEqual(response["type"], "ROUTING_TABLES_STORED")
        self.assertGreaterEqual(response["saved_entries"], 3)

        stored_routes = self.fetch_all(
            """
            SELECT
                ro.nombre AS router_origen,
                rd.nombre AS router_destino,
                rc.siguiente_salto,
                rc.costo,
                rc.ruta_completa,
                rc.estado
            FROM rutas_calculadas rc
            INNER JOIN routers ro ON rc.router_origen_id = ro.id
            INNER JOIN routers rd ON rc.router_destino_id = rd.id
            WHERE ro.nombre LIKE 'TEST_%'
            ORDER BY ro.nombre, rd.nombre
            """
        )

        self.assertEqual(len(stored_routes), 3)

        expected_routes = {
            ("TEST_R1", "TEST_R2"): 10,
            ("TEST_R1", "TEST_R3"): 5,
            ("TEST_R2", "TEST_R3"): 1
        }

        for route in stored_routes:
            key = (route["router_origen"], route["router_destino"])

            self.assertIn(key, expected_routes)
            self.assertEqual(route["costo"], expected_routes[key])
            self.assertEqual(route["estado"], "activa")

    def test_calculate_shortest_paths_from_specific_router(self):
        self.register_test_topology()

        routing_controller = RoutingController()
        response = routing_controller.calculate_shortest_paths_from_router("TEST_R2")

        self.assertEqual(response["type"], "ROUTES_CALCULATED")
        self.assertEqual(response["router_id"], "TEST_R2")

        shortest_paths = response["shortest_paths"]

        self.assertIn("TEST_R2", shortest_paths)
        self.assertIn("TEST_R3", shortest_paths)
        self.assertNotIn("TEST_R1", shortest_paths)

        self.assertEqual(shortest_paths["TEST_R3"]["cost"], 1)
        self.assertEqual(shortest_paths["TEST_R3"]["path"], ["TEST_R2", "TEST_R3"])


if __name__ == "__main__":
    import unittest
    unittest.main()