import os
import sys
import unittest


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.services.routing_table_service import RoutingTableService


class TestRoutingTableService(unittest.TestCase):
    """
    Sprint 2 tests for FR-05: routing/forwarding table generation.

    These are pure unit tests. They do not require MySQL or sockets.
    """

    def setUp(self):
        self.service = RoutingTableService()

    def test_generate_table_for_router_creates_expected_entries(self):
        shortest_paths_from_r1 = {
            "R1": {
                "cost": 0,
                "path": ["R1"]
            },
            "R2": {
                "cost": 10,
                "path": ["R1", "R2"]
            },
            "R3": {
                "cost": 5,
                "path": ["R1", "R3"]
            }
        }

        table = self.service.generate_table_for_router(
            source_router="R1",
            shortest_paths_from_source=shortest_paths_from_r1
        )

        self.assertEqual(table["source_router"], "R1")
        self.assertEqual(len(table["entries"]), 2)

        first_entry = table["entries"][0]
        second_entry = table["entries"][1]

        self.assertEqual(first_entry["source_router"], "R1")
        self.assertEqual(first_entry["destination_router"], "R2")
        self.assertEqual(first_entry["destination_prefix"], "R2")
        self.assertEqual(first_entry["prefix_length"], 32)
        self.assertEqual(first_entry["next_hop"], "R2")
        self.assertEqual(first_entry["cost"], 10)
        self.assertEqual(first_entry["path"], ["R1", "R2"])

        self.assertEqual(second_entry["source_router"], "R1")
        self.assertEqual(second_entry["destination_router"], "R3")
        self.assertEqual(second_entry["next_hop"], "R3")
        self.assertEqual(second_entry["cost"], 5)
        self.assertEqual(second_entry["path"], ["R1", "R3"])

    def test_generate_table_omits_route_to_itself(self):
        shortest_paths_from_r1 = {
            "R1": {
                "cost": 0,
                "path": ["R1"]
            },
            "R2": {
                "cost": 10,
                "path": ["R1", "R2"]
            }
        }

        table = self.service.generate_table_for_router(
            source_router="R1",
            shortest_paths_from_source=shortest_paths_from_r1
        )

        destinations = [
            entry["destination_router"]
            for entry in table["entries"]
        ]

        self.assertNotIn("R1", destinations)
        self.assertIn("R2", destinations)

    def test_generate_table_uses_second_router_in_path_as_next_hop(self):
        shortest_paths_from_r1 = {
            "R1": {
                "cost": 0,
                "path": ["R1"]
            },
            "R3": {
                "cost": 4,
                "path": ["R1", "R2", "R3"]
            }
        }

        table = self.service.generate_table_for_router(
            source_router="R1",
            shortest_paths_from_source=shortest_paths_from_r1
        )

        self.assertEqual(len(table["entries"]), 1)

        entry = table["entries"][0]

        self.assertEqual(entry["destination_router"], "R3")
        self.assertEqual(entry["next_hop"], "R2")
        self.assertEqual(entry["cost"], 4)
        self.assertEqual(entry["path"], ["R1", "R2", "R3"])

    def test_generate_all_tables_creates_one_table_per_router(self):
        all_shortest_paths = {
            "R1": {
                "R1": {
                    "cost": 0,
                    "path": ["R1"]
                },
                "R2": {
                    "cost": 10,
                    "path": ["R1", "R2"]
                }
            },
            "R2": {
                "R2": {
                    "cost": 0,
                    "path": ["R2"]
                },
                "R3": {
                    "cost": 1,
                    "path": ["R2", "R3"]
                }
            },
            "R3": {
                "R3": {
                    "cost": 0,
                    "path": ["R3"]
                }
            }
        }

        tables = self.service.generate_all_tables(all_shortest_paths)

        self.assertIn("R1", tables)
        self.assertIn("R2", tables)
        self.assertIn("R3", tables)

        self.assertEqual(len(tables["R1"]["entries"]), 1)
        self.assertEqual(len(tables["R2"]["entries"]), 1)
        self.assertEqual(len(tables["R3"]["entries"]), 0)

    def test_invalid_shortest_paths_type_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.generate_table_for_router(
                source_router="R1",
                shortest_paths_from_source="invalid"
            )

    def test_missing_path_field_is_rejected(self):
        invalid_shortest_paths = {
            "R2": {
                "cost": 10
            }
        }

        with self.assertRaises(ValueError):
            self.service.generate_table_for_router(
                source_router="R1",
                shortest_paths_from_source=invalid_shortest_paths
            )


if __name__ == "__main__":
    unittest.main()