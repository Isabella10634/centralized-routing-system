import os
import shutil
import sys
import tempfile
import unittest


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.dao.routing_table_dao import RoutingTableDAO


class TestRoutingTableDAO(unittest.TestCase):
    """
    Sprint 2 tests for local routing table persistence in the router.

    These tests validate that routing table data can be saved and loaded
    from a local JSON file without modifying the real router data folder.
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

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_routing_table_creates_json_file(self):
        routing_table = {
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

        self.dao.save_routing_table(routing_table)

        expected_file = os.path.join(
            self.temp_dir,
            "routing_table_TEST_R1.json"
        )

        self.assertTrue(os.path.exists(expected_file))

    def test_load_routing_table_returns_saved_data(self):
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

        loaded_table = self.dao.load_routing_table()

        self.assertEqual(loaded_table["source_router"], "TEST_R1")
        self.assertEqual(len(loaded_table["entries"]), 1)

        entry = loaded_table["entries"][0]

        self.assertEqual(entry["destination_router"], "TEST_R3")
        self.assertEqual(entry["next_hop"], "TEST_R2")
        self.assertEqual(entry["cost"], 4)
        self.assertEqual(entry["path"], ["TEST_R1", "TEST_R2", "TEST_R3"])

    def test_load_missing_routing_table_returns_empty_table(self):
        loaded_table = self.dao.load_routing_table()

        self.assertEqual(loaded_table["source_router"], "TEST_R1")
        self.assertEqual(loaded_table["entries"], [])


if __name__ == "__main__":
    unittest.main()