import os
import shutil
import sys
import tempfile
import unittest


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.controllers.routing_table_controller import RoutingTableController
from app.dao.routing_table_dao import RoutingTableDAO


class TestRoutingTableController(unittest.TestCase):
    """
    Sprint 2 tests for the router routing table controller.

    These tests validate that the router can apply UPDATE_TABLE messages
    and persist the received routing table locally.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.router_name = "TEST_R1"

        self.dao = RoutingTableDAO(self.router_name)
        self.dao.data_dir = self.temp_dir

        if hasattr(self.dao, "file_path"):
            self.dao.file_path = os.path.join(
                self.temp_dir,
                f"routing_table_{self.router_name}.json"
            )

        self.controller = RoutingTableController(self.router_name)
        self.controller.routing_table_dao = self.dao

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_apply_update_table_message_stores_received_table(self):
        message = {
            "type": "UPDATE_TABLE",
            "router_id": "TEST_R1",
            "table": {
                "source_router": "TEST_R1",
                "entries": [
                    {
                        "source_router": "TEST_R1",
                        "destination_router": "TEST_R2",
                        "destination_prefix": "TEST_R2",
                        "prefix_length": 32,
                        "next_hop": "TEST_R2",
                        "cost": 10,
                        "path": ["TEST_R1", "TEST_R2"]
                    }
                ]
            }
        }

        response = self.controller.apply_update_table_message(message)

        self.assertEqual(response["type"], "UPDATE_TABLE_OK")
        self.assertEqual(response["router_id"], "TEST_R1")
        self.assertEqual(response["entries"], 1)

        loaded_table = self.dao.load_routing_table()

        self.assertEqual(loaded_table["source_router"], "TEST_R1")
        self.assertEqual(len(loaded_table["entries"]), 1)

        entry = loaded_table["entries"][0]

        self.assertEqual(entry["destination_router"], "TEST_R2")
        self.assertEqual(entry["next_hop"], "TEST_R2")
        self.assertEqual(entry["cost"], 10)
        self.assertEqual(entry["path"], ["TEST_R1", "TEST_R2"])

    def test_get_current_routing_table_returns_saved_table(self):
        routing_table = {
            "source_router": "TEST_R1",
            "entries": [
                {
                    "source_router": "TEST_R1",
                    "destination_router": "TEST_R3",
                    "destination_prefix": "TEST_R3",
                    "prefix_length": 32,
                    "next_hop": "TEST_R2",
                    "cost": 4,
                    "path": ["TEST_R1", "TEST_R2", "TEST_R3"]
                }
            ]
        }

        self.dao.save_routing_table(routing_table)

        current_table = self.controller.get_current_routing_table()

        self.assertEqual(current_table["source_router"], "TEST_R1")
        self.assertEqual(len(current_table["entries"]), 1)
        self.assertEqual(current_table["entries"][0]["destination_router"], "TEST_R3")
        self.assertEqual(current_table["entries"][0]["next_hop"], "TEST_R2")

    def test_apply_update_table_message_rejects_missing_table(self):
        message = {
            "type": "UPDATE_TABLE",
            "router_id": "TEST_R1"
        }

        response = self.controller.apply_update_table_message(message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("valid table", response["message"])

    def test_apply_update_table_message_rejects_wrong_router_id(self):
        message = {
            "type": "UPDATE_TABLE",
            "router_id": "TEST_R2",
            "table": {
                "source_router": "TEST_R2",
                "entries": []
            }
        }

        response = self.controller.apply_update_table_message(message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("not for TEST_R1", response["message"])

    def test_apply_update_table_message_rejects_invalid_message_type(self):
        message = {
            "type": "AUTH_OK",
            "router_id": "TEST_R1",
            "table": {
                "source_router": "TEST_R1",
                "entries": []
            }
        }

        response = self.controller.apply_update_table_message(message)

        self.assertEqual(response["type"], "ERROR")
        self.assertIn("Invalid message type", response["message"])


if __name__ == "__main__":
    unittest.main()