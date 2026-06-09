from datetime import datetime

from app.dao.log_dao import LogDAO
from app.dao.routing_table_dao import RoutingTableDAO
from app.dao.topology_dao import TopologyDAO
from app.services.dijkstra_service import DijkstraService
from app.services.routing_table_service import RoutingTableService
from app.utils.constants import EVENT_TYPE_ROUTE_CALCULATION, EVENT_TYPE_ERROR


class RoutingController:
    """
    Controller responsible for Sprint 2 routing operations.

    Sprint 2 responsibilities:
    - Read active topology from MySQL.
    - Build the graph required by Dijkstra.
    - Compute shortest paths from one router or from all routers.
    - Generate routing/forwarding tables from shortest paths.
    - Persist calculated routing tables in MySQL.

    Later Sprint 2 responsibilities:
    - Send UPDATE_TABLE messages to routers.
    """

    def __init__(self):
        self.topology_dao = TopologyDAO()
        self.log_dao = LogDAO()
        self.dijkstra_service = DijkstraService()
        self.routing_table_service = RoutingTableService()
        self.routing_table_dao = RoutingTableDAO()

    def get_active_topology_graph(self):
        """
        Return the current active topology graph from the database.
        """
        return self.topology_dao.get_active_topology_graph()

    def calculate_shortest_paths_from_router(self, router_name):
        """
        Calculate shortest paths from one source router.

        Args:
            router_name (str): Source router name.

        Returns:
            dict: Response with graph and Dijkstra result.
        """
        try:
            graph = self.get_active_topology_graph()
            shortest_paths = self.dijkstra_service.compute_shortest_paths(
                graph,
                router_name
            )

            self.log_dao.insert_event(
                EVENT_TYPE_ROUTE_CALCULATION,
                f"Rutas calculadas desde router {router_name}",
                datetime.now()
            )

            return {
                "type": "ROUTES_CALCULATED",
                "router_id": router_name,
                "graph": graph,
                "shortest_paths": shortest_paths
            }

        except Exception as error:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                f"Error calculando rutas desde router {router_name}: {error}",
                datetime.now()
            )

            return {
                "type": "ERROR",
                "message": str(error)
            }

    def calculate_all_shortest_paths(self):
        """
        Calculate shortest paths from every active router.

        Returns:
            dict: Response with graph and all Dijkstra results.
        """
        try:
            graph = self.get_active_topology_graph()
            all_shortest_paths = self.dijkstra_service.compute_all_shortest_paths(graph)

            self.log_dao.insert_event(
                EVENT_TYPE_ROUTE_CALCULATION,
                "Rutas calculadas para todos los routers activos",
                datetime.now()
            )

            return {
                "type": "ALL_ROUTES_CALCULATED",
                "graph": graph,
                "shortest_paths": all_shortest_paths
            }

        except Exception as error:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                f"Error calculando rutas globales: {error}",
                datetime.now()
            )

            return {
                "type": "ERROR",
                "message": str(error)
            }

    def generate_routing_tables(self):
        """
        Generate routing/forwarding tables for all active routers.

        This method does not persist the generated tables. Use
        calculate_and_store_routing_tables() when persistence is required.

        Returns:
            dict: Response with graph, shortest paths and routing tables.
        """
        try:
            graph = self.get_active_topology_graph()
            all_shortest_paths = self.dijkstra_service.compute_all_shortest_paths(graph)

            routing_tables = self.routing_table_service.generate_all_tables(
                all_shortest_paths
            )

            self.log_dao.insert_event(
                EVENT_TYPE_ROUTE_CALCULATION,
                "Tablas de routing generadas para todos los routers activos",
                datetime.now()
            )

            return {
                "type": "ROUTING_TABLES_GENERATED",
                "graph": graph,
                "shortest_paths": all_shortest_paths,
                "routing_tables": routing_tables
            }

        except Exception as error:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                f"Error generando tablas de routing: {error}",
                datetime.now()
            )

            return {
                "type": "ERROR",
                "message": str(error)
            }

    def calculate_and_store_routing_tables(self):
        """
        Generate and persist routing tables from the current active topology.

        Flow:
        MySQL topology -> graph -> Dijkstra -> routing tables -> MySQL persistence

        Returns:
            dict: Response with generated tables and number of saved entries.
        """
        try:
            calculation_datetime = datetime.now()

            generated_response = self.generate_routing_tables()

            if generated_response["type"] != "ROUTING_TABLES_GENERATED":
                return generated_response

            saved_entries = self.routing_table_dao.save_routing_tables(
                generated_response["routing_tables"],
                calculation_datetime
            )

            self.log_dao.insert_event(
                EVENT_TYPE_ROUTE_CALCULATION,
                f"Tablas de routing persistidas correctamente. Entradas guardadas: {saved_entries}",
                calculation_datetime
            )

            return {
                "type": "ROUTING_TABLES_STORED",
                "saved_entries": saved_entries,
                "graph": generated_response["graph"],
                "shortest_paths": generated_response["shortest_paths"],
                "routing_tables": generated_response["routing_tables"]
            }

        except Exception as error:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                f"Error persistiendo tablas de routing: {error}",
                datetime.now()
            )

            return {
                "type": "ERROR",
                "message": str(error)
            }

    def get_stored_routing_tables(self):
        """
        Return calculated routing table entries stored in MySQL.
        """
        try:
            routes = self.routing_table_dao.get_all_calculated_routes()

            return {
                "type": "STORED_ROUTING_TABLES",
                "routes": routes
            }

        except Exception as error:
            self.log_dao.insert_event(
                EVENT_TYPE_ERROR,
                f"Error consultando rutas calculadas: {error}",
                datetime.now()
            )

            return {
                "type": "ERROR",
                "message": str(error)
            }