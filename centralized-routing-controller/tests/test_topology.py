from test_support import ControllerDatabaseTestCase

from app.controllers.router_registry_controller import RouterRegistryController
from app.controllers.topology_controller import TopologyController


class TestTopology(ControllerDatabaseTestCase):
    """
    Sprint 1 tests for FR-02 and FR-03.

    These tests validate neighbor information exchange and topology storage
    as weighted links in the enlaces table.
    """

    def register_test_router(self, router_id, ip, port, token):
        registry_controller = RouterRegistryController()

        message = {
            "type": "AUTH",
            "router_id": router_id,
            "ip": ip,
            "port": port,
            "token": token
        }

        response = registry_controller.register_router(message)

        self.assertEqual(response["type"], "AUTH_OK")
        self.assertEqual(response["router_id"], router_id)

    def test_register_neighbors_successfully(self):
        self.register_test_router("TEST_R1", "127.0.0.1", 5001, "token_r1")
        self.register_test_router("TEST_R2", "127.0.0.1", 5002, "token_r2")
        self.register_test_router("TEST_R3", "127.0.0.1", 5003, "token_r3")

        topology_controller = TopologyController()

        message = {
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

        response = topology_controller.register_neighbors(message)

        self.assertEqual(response["type"], "NEIGHBORS_OK")
        self.assertEqual(response["router_id"], "TEST_R1")

        links = self.fetch_all(
            """
            SELECT
                ro.nombre AS origen,
                rd.nombre AS destino,
                e.costo,
                e.estado
            FROM enlaces e
            INNER JOIN routers ro ON e.router_origen_id = ro.id
            INNER JOIN routers rd ON e.router_destino_id = rd.id
            WHERE ro.nombre = %s
            ORDER BY rd.nombre
            """,
            ("TEST_R1",)
        )

        self.assertEqual(len(links), 2)

        expected_links = {
            ("TEST_R1", "TEST_R2"): 10,
            ("TEST_R1", "TEST_R3"): 5
        }

        for link in links:
            key = (link["origen"], link["destino"])

            self.assertIn(key, expected_links)
            self.assertEqual(link["costo"], expected_links[key])
            self.assertEqual(link["estado"], "activo")

    def test_register_neighbors_updates_existing_link_cost(self):
        self.register_test_router("TEST_R1", "127.0.0.1", 5001, "token_r1")
        self.register_test_router("TEST_R2", "127.0.0.1", 5002, "token_r2")

        topology_controller = TopologyController()

        first_message = {
            "type": "NEIGHBORS",
            "router_id": "TEST_R1",
            "neighbors": [
                {
                    "neighbor_id": "TEST_R2",
                    "cost": 10
                }
            ]
        }

        second_message = {
            "type": "NEIGHBORS",
            "router_id": "TEST_R1",
            "neighbors": [
                {
                    "neighbor_id": "TEST_R2",
                    "cost": 3
                }
            ]
        }

        first_response = topology_controller.register_neighbors(first_message)
        second_response = topology_controller.register_neighbors(second_message)

        self.assertEqual(first_response["type"], "NEIGHBORS_OK")
        self.assertEqual(second_response["type"], "NEIGHBORS_OK")

        links = self.fetch_all(
            """
            SELECT
                ro.nombre AS origen,
                rd.nombre AS destino,
                e.costo,
                e.estado
            FROM enlaces e
            INNER JOIN routers ro ON e.router_origen_id = ro.id
            INNER JOIN routers rd ON e.router_destino_id = rd.id
            WHERE ro.nombre = %s AND rd.nombre = %s
            """,
            ("TEST_R1", "TEST_R2")
        )

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["origen"], "TEST_R1")
        self.assertEqual(links[0]["destino"], "TEST_R2")
        self.assertEqual(links[0]["costo"], 3)
        self.assertEqual(links[0]["estado"], "activo")

    def test_register_neighbors_fails_when_origin_router_is_not_registered(self):
        topology_controller = TopologyController()

        message = {
            "type": "NEIGHBORS",
            "router_id": "TEST_UNKNOWN",
            "neighbors": [
                {
                    "neighbor_id": "TEST_R2",
                    "cost": 10
                }
            ]
        }

        response = topology_controller.register_neighbors(message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("not registered", response["message"])

    def test_register_neighbors_fails_when_required_field_is_missing(self):
        topology_controller = TopologyController()

        message = {
            "type": "NEIGHBORS",
            "router_id": "TEST_R1"
        }

        response = topology_controller.register_neighbors(message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("Missing field", response["message"])


if __name__ == "__main__":
    import unittest
    unittest.main()