from test_support import ControllerDatabaseTestCase

from app.cli.network_status_cli import NetworkStatusCLI
from app.controllers.metrics_controller import MetricsController
from app.controllers.router_registry_controller import RouterRegistryController


class TestNetworkStatusCLISprint3(ControllerDatabaseTestCase):
    """
    Sprint 3 tests for network status CLI.

    These tests validate:
    - The CLI returns registered routers.
    - The CLI includes latest metrics.
    - The CLI handles routers without metrics.
    - The CLI reflects active/inactive router status.
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

    def find_router_status_row(self, rows, router_id):
        for row in rows:
            if row["router_name"] == router_id:
                return row

        return None

    def test_network_status_includes_registered_router(self):
        self.register_test_router("TEST_R1", 6401)

        cli = NetworkStatusCLI()
        rows = cli.get_network_status()

        router_row = self.find_router_status_row(rows, "TEST_R1")

        self.assertIsNotNone(router_row)
        self.assertEqual(router_row["router_name"], "TEST_R1")
        self.assertEqual(router_row["ip"], "127.0.0.1")
        self.assertEqual(router_row["puerto"], 6401)
        self.assertEqual(router_row["estado"], "activo")

    def test_network_status_includes_latest_metrics_for_router(self):
        self.register_test_router("TEST_R1", 6401)

        metrics_controller = MetricsController()

        first_metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_R1",
            "uptime_seconds": 10,
            "heartbeat_count": 2,
            "routing_entries": 1
        }

        second_metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_R1",
            "uptime_seconds": 30,
            "heartbeat_count": 6,
            "routing_entries": 3
        }

        first_response = metrics_controller.register_metrics(first_metrics_message)
        second_response = metrics_controller.register_metrics(second_metrics_message)

        self.assertEqual(first_response["type"], "METRICS_OK")
        self.assertEqual(second_response["type"], "METRICS_OK")

        cli = NetworkStatusCLI()
        rows = cli.get_network_status()

        router_row = self.find_router_status_row(rows, "TEST_R1")

        self.assertIsNotNone(router_row)
        self.assertEqual(router_row["uptime_seconds"], 30)
        self.assertEqual(router_row["heartbeat_count"], 6)
        self.assertEqual(router_row["routing_entries"], 3)
        self.assertIsNotNone(router_row["metrics_timestamp"])

    def test_network_status_handles_router_without_metrics(self):
        self.register_test_router("TEST_R1", 6401)

        cli = NetworkStatusCLI()
        rows = cli.get_network_status()

        router_row = self.find_router_status_row(rows, "TEST_R1")

        self.assertIsNotNone(router_row)
        self.assertEqual(router_row["router_name"], "TEST_R1")
        self.assertIsNone(router_row["uptime_seconds"])
        self.assertIsNone(router_row["heartbeat_count"])
        self.assertIsNone(router_row["routing_entries"])
        self.assertIsNone(router_row["metrics_timestamp"])

    def test_network_status_reflects_inactive_router_status(self):
        self.register_test_router("TEST_R1", 6401)
        self.set_router_status("TEST_R1", "inactivo")

        cli = NetworkStatusCLI()
        rows = cli.get_network_status()

        router_row = self.find_router_status_row(rows, "TEST_R1")

        self.assertIsNotNone(router_row)
        self.assertEqual(router_row["router_name"], "TEST_R1")
        self.assertEqual(router_row["estado"], "inactivo")

    def test_format_value_returns_dash_for_none(self):
        self.assertEqual(NetworkStatusCLI.format_value(None), "-")

    def test_format_value_returns_string_for_non_none_value(self):
        self.assertEqual(NetworkStatusCLI.format_value(123), "123")
        self.assertEqual(NetworkStatusCLI.format_value("activo"), "activo")

    def test_format_datetime_returns_dash_for_none(self):
        self.assertEqual(NetworkStatusCLI.format_datetime(None), "-")


if __name__ == "__main__":
    import unittest
    unittest.main()