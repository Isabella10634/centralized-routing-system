import os
import sys
import unittest


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.services.dijkstra_service import DijkstraService


class TestDijkstraService(unittest.TestCase):
    """
    Sprint 2 tests for FR-04: shortest path calculation using Dijkstra.

    These tests are pure unit tests. They do not require MySQL, TCP sockets,
    controller execution, or router execution.
    """

    def setUp(self):
        self.service = DijkstraService()

    def test_compute_shortest_path_from_r1_to_r3(self):
        graph = {
            "R1": [
                {"to": "R2", "cost": 2},
                {"to": "R3", "cost": 5}
            ],
            "R2": [
                {"to": "R3", "cost": 1}
            ],
            "R3": []
        }

        result = self.service.compute_shortest_paths(graph, "R1")

        self.assertEqual(result["R3"]["cost"], 3)
        self.assertEqual(result["R3"]["path"], ["R1", "R2", "R3"])

    def test_compute_shortest_paths_from_source_to_all_reachable_routers(self):
        graph = {
            "R1": [
                {"to": "R2", "cost": 2},
                {"to": "R3", "cost": 8}
            ],
            "R2": [
                {"to": "R3", "cost": 1},
                {"to": "R4", "cost": 4}
            ],
            "R3": [
                {"to": "R4", "cost": 1}
            ],
            "R4": []
        }

        result = self.service.compute_shortest_paths(graph, "R1")

        self.assertEqual(result["R1"]["cost"], 0)
        self.assertEqual(result["R1"]["path"], ["R1"])

        self.assertEqual(result["R2"]["cost"], 2)
        self.assertEqual(result["R2"]["path"], ["R1", "R2"])

        self.assertEqual(result["R3"]["cost"], 3)
        self.assertEqual(result["R3"]["path"], ["R1", "R2", "R3"])

        self.assertEqual(result["R4"]["cost"], 4)
        self.assertEqual(result["R4"]["path"], ["R1", "R2", "R3", "R4"])

    def test_unreachable_router_is_not_in_result(self):
        graph = {
            "R1": [
                {"to": "R2", "cost": 1}
            ],
            "R2": [],
            "R3": []
        }

        result = self.service.compute_shortest_paths(graph, "R1")

        self.assertIn("R1", result)
        self.assertIn("R2", result)
        self.assertNotIn("R3", result)

    def test_compute_all_shortest_paths(self):
        graph = {
            "R1": [
                {"to": "R2", "cost": 2},
                {"to": "R3", "cost": 5}
            ],
            "R2": [
                {"to": "R3", "cost": 1}
            ],
            "R3": []
        }

        result = self.service.compute_all_shortest_paths(graph)

        self.assertEqual(result["R1"]["R3"]["cost"], 3)
        self.assertEqual(result["R1"]["R3"]["path"], ["R1", "R2", "R3"])

        self.assertEqual(result["R2"]["R3"]["cost"], 1)
        self.assertEqual(result["R2"]["R3"]["path"], ["R2", "R3"])

        self.assertEqual(result["R3"]["R3"]["cost"], 0)
        self.assertEqual(result["R3"]["R3"]["path"], ["R3"])

    def test_source_router_must_exist(self):
        graph = {
            "R1": [],
            "R2": []
        }

        with self.assertRaises(ValueError) as context:
            self.service.compute_shortest_paths(graph, "R9")

        self.assertIn("Source router R9 does not exist", str(context.exception))

    def test_negative_cost_is_rejected(self):
        graph = {
            "R1": [
                {"to": "R2", "cost": -1}
            ],
            "R2": []
        }

        with self.assertRaises(ValueError) as context:
            self.service.compute_shortest_paths(graph, "R1")

        self.assertIn("cannot be negative", str(context.exception))

    def test_link_to_unknown_router_is_rejected(self):
        graph = {
            "R1": [
                {"to": "R2", "cost": 1}
            ]
        }

        with self.assertRaises(ValueError) as context:
            self.service.compute_shortest_paths(graph, "R1")

        self.assertIn("unknown router R2", str(context.exception))


if __name__ == "__main__":
    unittest.main()