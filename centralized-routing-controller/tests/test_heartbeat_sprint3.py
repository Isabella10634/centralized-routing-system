from datetime import datetime, timedelta

from test_support import ControllerDatabaseTestCase

from app.controllers.router_registry_controller import RouterRegistryController


class TestHeartbeatSprint3(ControllerDatabaseTestCase):
    """
    Sprint 3 tests for router heartbeat and inactive router detection.

    These tests validate:
    - HEARTBEAT updates router last activity.
    - HEARTBEAT marks router as active.
    - HEARTBEAT from unknown router is rejected.
    - Routers without recent activity are marked inactive.
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

    def set_router_last_activity(self, router_id, last_activity):
        connection = self.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE routers
            SET ultima_actividad = %s
            WHERE nombre = %s
            """,
            (last_activity, router_id)
        )

        connection.commit()

        cursor.close()
        connection.close()

    def set_router_status(self, router_id, status):
        connection = self.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE routers
            SET estado = %s
            WHERE nombre = %s
            """,
            (status, router_id)
        )

        connection.commit()

        cursor.close()
        connection.close()

    def test_register_heartbeat_updates_last_activity_and_sets_active_status(self):
        self.register_test_router("TEST_R1", 6201)

        old_activity = datetime.now() - timedelta(minutes=10)
        self.set_router_last_activity("TEST_R1", old_activity)
        self.set_router_status("TEST_R1", "inactivo")

        registry_controller = RouterRegistryController()

        heartbeat_message = {
            "type": "HEARTBEAT",
            "router_id": "TEST_R1"
        }

        response = registry_controller.register_heartbeat(heartbeat_message)

        self.assertEqual(response["type"], "HEARTBEAT_OK")
        self.assertEqual(response["router_id"], "TEST_R1")

        router = self.fetch_one(
            """
            SELECT nombre, estado, ultima_actividad
            FROM routers
            WHERE nombre = %s
            """,
            ("TEST_R1",)
        )

        self.assertIsNotNone(router)
        self.assertEqual(router["nombre"], "TEST_R1")
        self.assertEqual(router["estado"], "activo")
        self.assertIsNotNone(router["ultima_actividad"])
        self.assertGreater(router["ultima_actividad"], old_activity)

    def test_register_heartbeat_rejects_unknown_router(self):
        registry_controller = RouterRegistryController()

        heartbeat_message = {
            "type": "HEARTBEAT",
            "router_id": "TEST_UNKNOWN_ROUTER"
        }

        response = registry_controller.register_heartbeat(heartbeat_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("not registered", response["message"])

    def test_register_heartbeat_rejects_missing_router_id(self):
        registry_controller = RouterRegistryController()

        heartbeat_message = {
            "type": "HEARTBEAT"
        }

        response = registry_controller.register_heartbeat(heartbeat_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("router_id", response["message"])

    def test_mark_inactive_routers_marks_old_router_as_inactive(self):
        self.register_test_router("TEST_R1", 6201)

        old_activity = datetime.now() - timedelta(seconds=60)
        self.set_router_last_activity("TEST_R1", old_activity)
        self.set_router_status("TEST_R1", "activo")

        registry_controller = RouterRegistryController()

        response = registry_controller.mark_inactive_routers(timeout_seconds=15)

        self.assertEqual(response["type"], "INACTIVE_ROUTERS_MARKED")
        self.assertEqual(response["timeout_seconds"], 15)
        self.assertGreaterEqual(response["affected_rows"], 1)

        router = self.fetch_one(
            """
            SELECT nombre, estado, ultima_actividad
            FROM routers
            WHERE nombre = %s
            """,
            ("TEST_R1",)
        )

        self.assertIsNotNone(router)
        self.assertEqual(router["estado"], "inactivo")

    def test_mark_inactive_routers_keeps_recent_router_active(self):
        self.register_test_router("TEST_R1", 6201)

        recent_activity = datetime.now()
        self.set_router_last_activity("TEST_R1", recent_activity)
        self.set_router_status("TEST_R1", "activo")

        registry_controller = RouterRegistryController()

        response = registry_controller.mark_inactive_routers(timeout_seconds=15)

        self.assertEqual(response["type"], "INACTIVE_ROUTERS_MARKED")
        self.assertEqual(response["timeout_seconds"], 15)

        router = self.fetch_one(
            """
            SELECT nombre, estado, ultima_actividad
            FROM routers
            WHERE nombre = %s
            """,
            ("TEST_R1",)
        )

        self.assertIsNotNone(router)
        self.assertEqual(router["estado"], "activo")


if __name__ == "__main__":
    import unittest
    unittest.main()