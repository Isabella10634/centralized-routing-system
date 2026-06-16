from test_support import ControllerDatabaseTestCase

from app.controllers.metrics_controller import MetricsController
from app.controllers.router_registry_controller import RouterRegistryController
from app.dao.metrics_dao import MetricsDAO


class TestMetricsSprint3(ControllerDatabaseTestCase):
    """
    Sprint 3 tests for router metrics.

    These tests validate:
    - METRICS messages are stored correctly.
    - METRICS from unknown routers are rejected.
    - METRICS messages with missing fields are rejected.
    - METRICS values must be valid non-negative integers.
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

    def test_register_metrics_stores_metrics_successfully(self):
        self.register_test_router("TEST_R1", 6301)

        metrics_controller = MetricsController()

        metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_R1",
            "uptime_seconds": 25,
            "heartbeat_count": 5,
            "routing_entries": 3
        }

        response = metrics_controller.register_metrics(metrics_message)

        self.assertEqual(response["type"], "METRICS_OK")
        self.assertEqual(response["router_id"], "TEST_R1")
        self.assertIn("metric_id", response)

        metric = self.fetch_one(
            """
            SELECT router_nombre,
                   uptime_seconds,
                   heartbeat_count,
                   routing_entries
            FROM metricas_router
            WHERE id = %s
            """,
            (response["metric_id"],)
        )

        self.assertIsNotNone(metric)
        self.assertEqual(metric["router_nombre"], "TEST_R1")
        self.assertEqual(metric["uptime_seconds"], 25)
        self.assertEqual(metric["heartbeat_count"], 5)
        self.assertEqual(metric["routing_entries"], 3)

    def test_register_metrics_rejects_unknown_router(self):
        metrics_controller = MetricsController()

        metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_UNKNOWN_ROUTER",
            "uptime_seconds": 10,
            "heartbeat_count": 2,
            "routing_entries": 1
        }

        response = metrics_controller.register_metrics(metrics_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("not registered", response["message"])

    def test_register_metrics_rejects_missing_router_id(self):
        metrics_controller = MetricsController()

        metrics_message = {
            "type": "METRICS",
            "uptime_seconds": 10,
            "heartbeat_count": 2,
            "routing_entries": 1
        }

        response = metrics_controller.register_metrics(metrics_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("router_id", response["message"])

    def test_register_metrics_rejects_missing_uptime_seconds(self):
        self.register_test_router("TEST_R1", 6301)

        metrics_controller = MetricsController()

        metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_R1",
            "heartbeat_count": 2,
            "routing_entries": 1
        }

        response = metrics_controller.register_metrics(metrics_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("uptime_seconds", response["message"])

    def test_register_metrics_rejects_missing_heartbeat_count(self):
        self.register_test_router("TEST_R1", 6301)

        metrics_controller = MetricsController()

        metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_R1",
            "uptime_seconds": 10,
            "routing_entries": 1
        }

        response = metrics_controller.register_metrics(metrics_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("heartbeat_count", response["message"])

    def test_register_metrics_rejects_missing_routing_entries(self):
        self.register_test_router("TEST_R1", 6301)

        metrics_controller = MetricsController()

        metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_R1",
            "uptime_seconds": 10,
            "heartbeat_count": 2
        }

        response = metrics_controller.register_metrics(metrics_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("routing_entries", response["message"])

    def test_register_metrics_rejects_non_integer_values(self):
        self.register_test_router("TEST_R1", 6301)

        metrics_controller = MetricsController()

        metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_R1",
            "uptime_seconds": "invalid",
            "heartbeat_count": 2,
            "routing_entries": 1
        }

        response = metrics_controller.register_metrics(metrics_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("integers", response["message"])

    def test_register_metrics_rejects_negative_uptime_seconds(self):
        self.register_test_router("TEST_R1", 6301)

        metrics_controller = MetricsController()

        metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_R1",
            "uptime_seconds": -1,
            "heartbeat_count": 2,
            "routing_entries": 1
        }

        response = metrics_controller.register_metrics(metrics_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("uptime_seconds", response["message"])

    def test_register_metrics_rejects_negative_heartbeat_count(self):
        self.register_test_router("TEST_R1", 6301)

        metrics_controller = MetricsController()

        metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_R1",
            "uptime_seconds": 10,
            "heartbeat_count": -1,
            "routing_entries": 1
        }

        response = metrics_controller.register_metrics(metrics_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("heartbeat_count", response["message"])

    def test_register_metrics_rejects_negative_routing_entries(self):
        self.register_test_router("TEST_R1", 6301)

        metrics_controller = MetricsController()

        metrics_message = {
            "type": "METRICS",
            "router_id": "TEST_R1",
            "uptime_seconds": 10,
            "heartbeat_count": 2,
            "routing_entries": -1
        }

        response = metrics_controller.register_metrics(metrics_message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("routing_entries", response["message"])

    def test_metrics_dao_get_metrics_by_router_name_returns_metrics(self):
        self.register_test_router("TEST_R1", 6301)

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
            "uptime_seconds": 20,
            "heartbeat_count": 4,
            "routing_entries": 2
        }

        metrics_controller.register_metrics(first_metrics_message)
        metrics_controller.register_metrics(second_metrics_message)

        metrics_dao = MetricsDAO()
        metrics = metrics_dao.get_metrics_by_router_name("TEST_R1")

        self.assertGreaterEqual(len(metrics), 2)

        router_names = [metric["router_nombre"] for metric in metrics]

        self.assertIn("TEST_R1", router_names)


if __name__ == "__main__":
    import unittest
    unittest.main()