from test_support import ControllerDatabaseTestCase

from app.controllers.router_registry_controller import RouterRegistryController
from app.controllers.topology_controller import TopologyController
from app.controllers.routing_controller import RoutingController


class TestLinkCostSprint3(ControllerDatabaseTestCase):
    """
    Sprint 3 tests for link cost update and routing recalculation.

    These tests validate:
    - Existing link cost update.
    - Invalid cost rejection.
    - Missing link rejection.
    - Routing table recalculation after cost change.
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
        self.register_test_router("TEST_R1", 6101)
        self.register_test_router("TEST_R2", 6102)
        self.register_test_router("TEST_R3", 6103)

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

    def test_update_existing_link_cost_successfully(self):
        self.register_test_topology()

        topology_controller = TopologyController()

        response = topology_controller.update_link_cost(
            "TEST_R1",
            "TEST_R2",
            3
        )

        self.assertEqual(response["type"], "LINK_COST_UPDATED")
        self.assertEqual(response["origin_router"], "TEST_R1")
        self.assertEqual(response["destination_router"], "TEST_R2")
        self.assertEqual(response["new_cost"], 3)

        updated_link = self.fetch_one(
            """
            SELECT e.costo
            FROM enlaces e
            INNER JOIN routers ro ON e.router_origen_id = ro.id
            INNER JOIN routers rd ON e.router_destino_id = rd.id
            WHERE ro.nombre = %s AND rd.nombre = %s
            """,
            ("TEST_R1", "TEST_R2")
        )

        self.assertIsNotNone(updated_link)
        self.assertEqual(updated_link["costo"], 3)

    def test_update_link_cost_rejects_negative_cost(self):
        self.register_test_topology()

        topology_controller = TopologyController()

        response = topology_controller.update_link_cost(
            "TEST_R1",
            "TEST_R2",
            -5
        )

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("greater than zero", response["message"])

    def test_update_link_cost_rejects_missing_link(self):
        self.register_test_topology()

        topology_controller = TopologyController()

        response = topology_controller.update_link_cost(
            "TEST_R3",
            "TEST_R1",
            2
        )

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("does not exist", response["message"])

    def test_routing_recalculation_uses_updated_link_cost(self):
        self.register_test_topology()

        topology_controller = TopologyController()
        routing_controller = RoutingController()

        update_response = topology_controller.update_link_cost(
            "TEST_R1",
            "TEST_R2",
            3
        )

        self.assertEqual(update_response["type"], "LINK_COST_UPDATED")

        recalculation_response = routing_controller.calculate_and_store_routing_tables()

        self.assertEqual(recalculation_response["type"], "ROUTING_TABLES_STORED")
        self.assertGreaterEqual(recalculation_response["saved_entries"], 3)

        stored_route = self.fetch_one(
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
            WHERE ro.nombre = %s AND rd.nombre = %s
            """,
            ("TEST_R1", "TEST_R3")
        )

        self.assertIsNotNone(stored_route)
        self.assertEqual(stored_route["router_origen"], "TEST_R1")
        self.assertEqual(stored_route["router_destino"], "TEST_R3")
        self.assertEqual(stored_route["siguiente_salto"], "TEST_R2")
        self.assertEqual(stored_route["costo"], 4)
        self.assertEqual(stored_route["estado"], "activa")

        self.assertIn("TEST_R1", stored_route["ruta_completa"])
        self.assertIn("TEST_R2", stored_route["ruta_completa"])
        self.assertIn("TEST_R3", stored_route["ruta_completa"])


if __name__ == "__main__":
    import unittest
    unittest.main()