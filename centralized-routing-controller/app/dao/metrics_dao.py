import mysql.connector

from app.utils.db_config import DB_CONFIG


class MetricsDAO:
    """
    DAO responsible for storing router metrics in MySQL.

    Supports:
    - metricas_router: previous operational metrics.
    - metricas_globales: documented Sprint 3 metrics.
    """

    def __init__(self):
        self.config = DB_CONFIG

    def connect(self):
        """
        Open a MySQL connection using the local database configuration.
        """
        return mysql.connector.connect(**self.config)

    def insert_metrics(
        self,
        router_id,
        router_name,
        uptime_seconds,
        heartbeat_count,
        routing_entries,
        timestamp
    ):
        """
        Insert one legacy metrics sample into metricas_router.

        Kept for compatibility with existing tests and previous Sprint 3 work.
        """
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        INSERT INTO metricas_router (
            router_id,
            router_nombre,
            uptime_seconds,
            heartbeat_count,
            routing_entries,
            timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            router_id,
            router_name,
            uptime_seconds,
            heartbeat_count,
            routing_entries,
            timestamp
        )

        cursor.execute(query, values)
        connection.commit()

        inserted_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return inserted_id

    def insert_global_metrics(
        self,
        router_id,
        router_name,
        queue_size,
        packets_forwarded,
        packets_discarded,
        timestamp
    ):
        """
        Insert one documented metrics sample into metricas_globales.
        """
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        INSERT INTO metricas_globales (
            router_id,
            router_nombre,
            timestamp,
            tamano_cola,
            paquetes_enviados,
            paquetes_descartados
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            router_id,
            router_name,
            timestamp,
            queue_size,
            packets_forwarded,
            packets_discarded
        )

        cursor.execute(query, values)
        connection.commit()

        inserted_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return inserted_id

    def get_metrics_by_router_name(self, router_name):
        """
        Return all legacy metrics samples for one router.
        """
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT *
        FROM metricas_router
        WHERE router_nombre = %s
        ORDER BY timestamp ASC
        """

        cursor.execute(query, (router_name,))
        metrics = cursor.fetchall()

        cursor.close()
        connection.close()

        return metrics

    def get_global_metrics_by_router_name(self, router_name):
        """
        Return all documented metrics samples for one router.
        """
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT *
        FROM metricas_globales
        WHERE router_nombre = %s
        ORDER BY timestamp ASC
        """

        cursor.execute(query, (router_name,))
        metrics = cursor.fetchall()

        cursor.close()
        connection.close()

        return metrics