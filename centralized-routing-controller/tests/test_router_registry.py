from test_support import ControllerDatabaseTestCase

from app.controllers.router_registry_controller import RouterRegistryController


class TestRouterRegistry(ControllerDatabaseTestCase):
    """
    Sprint 1 tests for FR-01: router registration.

    These tests validate the same controller logic used when an AUTH message
    is received from a router.
    """

    def test_register_router_successfully(self):
        controller = RouterRegistryController()

        message = {
            "type": "AUTH",
            "router_id": "TEST_R1",
            "ip": "127.0.0.1",
            "port": 5001,
            "token": "test_token_r1"
        }

        response = controller.register_router(message)

        self.assertEqual(response["type"], "AUTH_OK")
        self.assertEqual(response["router_id"], "TEST_R1")

        router = self.fetch_one(
            """
            SELECT nombre, ip, puerto, token, estado
            FROM routers
            WHERE nombre = %s
            """,
            ("TEST_R1",)
        )

        self.assertIsNotNone(router)
        self.assertEqual(router["nombre"], "TEST_R1")
        self.assertEqual(router["ip"], "127.0.0.1")
        self.assertEqual(router["puerto"], 5001)
        self.assertEqual(router["token"], "test_token_r1")
        self.assertEqual(router["estado"], "activo")

    def test_register_existing_router_updates_information_without_duplicate(self):
        controller = RouterRegistryController()

        first_message = {
            "type": "AUTH",
            "router_id": "TEST_R1",
            "ip": "127.0.0.1",
            "port": 5001,
            "token": "first_token"
        }

        second_message = {
            "type": "AUTH",
            "router_id": "TEST_R1",
            "ip": "192.168.1.50",
            "port": 6001,
            "token": "updated_token"
        }

        first_response = controller.register_router(first_message)
        second_response = controller.register_router(second_message)

        self.assertEqual(first_response["type"], "AUTH_OK")
        self.assertEqual(second_response["type"], "AUTH_OK")

        count_row = self.fetch_one(
            """
            SELECT COUNT(*) AS total
            FROM routers
            WHERE nombre = %s
            """,
            ("TEST_R1",)
        )

        self.assertEqual(count_row["total"], 1)

        router = self.fetch_one(
            """
            SELECT nombre, ip, puerto, token, estado
            FROM routers
            WHERE nombre = %s
            """,
            ("TEST_R1",)
        )

        self.assertEqual(router["ip"], "192.168.1.50")
        self.assertEqual(router["puerto"], 6001)
        self.assertEqual(router["token"], "updated_token")
        self.assertEqual(router["estado"], "activo")

    def test_register_router_fails_when_required_field_is_missing(self):
        controller = RouterRegistryController()

        message = {
            "type": "AUTH",
            "router_id": "TEST_R1",
            "ip": "127.0.0.1",
            "token": "test_token_r1"
        }

        response = controller.register_router(message)

        self.assertEqual(response["type"], "AUTH_FAIL")
        self.assertIn("Missing field", response["message"])

        router = self.fetch_one(
            """
            SELECT *
            FROM routers
            WHERE nombre = %s
            """,
            ("TEST_R1",)
        )

        self.assertIsNone(router)


if __name__ == "__main__":
    import unittest
    unittest.main()