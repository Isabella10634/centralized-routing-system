import mysql.connector

from app.utils.db_config import DB_CONFIG


class TopologyDAO:
    """
    DAO responsible for all database operations related to the enlaces table.

    Sprint 1 responsibilities:
    - Save router links.
    - Update link cost/status.
    - Retrieve stored links.

    Sprint 2 responsibilities:
    - Build the active topology graph required by Dijkstra.
    """

    def __init__(self):
        self.config = DB_CONFIG

    def connect(self):
        """
        Open a MySQL connection using the controller database configuration.
        """
        return mysql.connector.connect(**self.config)

    def link_exists(self, router_origen_id, router_destino_id):
        """
        Check whether a directed link already exists between two routers.
        """
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        SELECT COUNT(*)
        FROM enlaces
        WHERE router_origen_id = %s AND router_destino_id = %s
        """
        cursor.execute(query, (router_origen_id, router_destino_id))
        result = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return result > 0

    def insert_link(self, router_origen_id, router_destino_id, costo, estado):
        """
        Insert a new directed link into the topology.
        """
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        INSERT INTO enlaces (router_origen_id, router_destino_id, costo, estado)
        VALUES (%s, %s, %s, %s)
        """
        values = (router_origen_id, router_destino_id, costo, estado)

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

    def update_link(self, router_origen_id, router_destino_id, costo, estado):
        """
        Update cost and status of an existing directed link.
        """
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        UPDATE enlaces
        SET costo = %s, estado = %s
        WHERE router_origen_id = %s AND router_destino_id = %s
        """
        cursor.execute(query, (costo, estado, router_origen_id, router_destino_id))
        connection.commit()

        cursor.close()
        connection.close()

    def save_link(self, router_origen_id, router_destino_id, costo, estado):
        """
        Insert or update a directed link depending on whether it already exists.
        """
        if self.link_exists(router_origen_id, router_destino_id):
            self.update_link(router_origen_id, router_destino_id, costo, estado)
        else:
            self.insert_link(router_origen_id, router_destino_id, costo, estado)

    def get_all_links(self):
        """
        Return all stored links.
        """
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM enlaces"
        cursor.execute(query)
        links = cursor.fetchall()

        cursor.close()
        connection.close()

        return links

    def get_links_by_origin(self, router_origen_id):
        """
        Return all links that start from a specific router ID.
        """
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM enlaces WHERE router_origen_id = %s"
        cursor.execute(query, (router_origen_id,))
        links = cursor.fetchall()

        cursor.close()
        connection.close()

        return links

    def update_link_cost(self, router_origen_id, router_destino_id, nuevo_costo):
        """
        Update the cost of an existing directed link.
        """
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        UPDATE enlaces
        SET costo = %s
        WHERE router_origen_id = %s AND router_destino_id = %s
        """
        cursor.execute(query, (nuevo_costo, router_origen_id, router_destino_id))
        connection.commit()

        cursor.close()
        connection.close()

    def update_link_status(self, router_origen_id, router_destino_id, nuevo_estado):
        """
        Update the status of an existing directed link.
        """
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        UPDATE enlaces
        SET estado = %s
        WHERE router_origen_id = %s AND router_destino_id = %s
        """
        cursor.execute(query, (nuevo_estado, router_origen_id, router_destino_id))
        connection.commit()

        cursor.close()
        connection.close()

    def get_active_topology_graph(self):
        """
        Build the active weighted directed graph used by Dijkstra.

        The graph includes all active routers, even if they do not have outgoing
        links yet. This is important because a router with no neighbors is still
        part of the topology.

        Returns:
            dict: Graph indexed by router name.

            Example:
            {
                "R1": [
                    {"to": "R2", "cost": 10},
                    {"to": "R3", "cost": 5}
                ],
                "R2": [],
                "R3": []
            }
        """
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        routers_query = """
        SELECT id, nombre
        FROM routers
        WHERE estado = 'activo'
        ORDER BY nombre
        """
        cursor.execute(routers_query)
        routers = cursor.fetchall()

        graph = {}

        router_id_to_name = {}

        for router in routers:
            router_id = router["id"]
            router_name = router["nombre"]

            router_id_to_name[router_id] = router_name
            graph[router_name] = []

        links_query = """
        SELECT
            router_origen_id,
            router_destino_id,
            costo
        FROM enlaces
        WHERE estado = 'activo'
        ORDER BY router_origen_id, router_destino_id
        """
        cursor.execute(links_query)
        links = cursor.fetchall()

        for link in links:
            origin_id = link["router_origen_id"]
            destination_id = link["router_destino_id"]

            if origin_id in router_id_to_name and destination_id in router_id_to_name:
                origin_name = router_id_to_name[origin_id]
                destination_name = router_id_to_name[destination_id]

                graph[origin_name].append(
                    {
                        "to": destination_name,
                        "cost": link["costo"]
                    }
                )

        cursor.close()
        connection.close()

        return graph