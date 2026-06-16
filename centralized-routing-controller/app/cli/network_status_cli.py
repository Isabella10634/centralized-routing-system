import mysql.connector

from app.utils.db_config import DB_CONFIG


class NetworkStatusCLI:
    """
    CLI utility to display the current network status.

    Shows:
    - Registered routers.
    - Active/inactive status.
    - Last activity.
    - Legacy operational metrics.
    - Documented Sprint 3 metrics.
    """

    def __init__(self):
        self.config = DB_CONFIG

    def connect(self):
        """
        Open a MySQL connection using the controller database configuration.
        """
        return mysql.connector.connect(**self.config)

    def get_network_status(self):
        """
        Return router status enriched with both legacy and documented metrics.

        Legacy metrics:
        - uptime_seconds
        - heartbeat_count
        - routing_entries

        Documented metrics:
        - tamano_cola
        - paquetes_enviados
        - paquetes_descartados

        The field metrics_timestamp always returns the newest available
        metrics timestamp, whether it comes from metricas_router or
        metricas_globales.
        """
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT
            r.nombre AS router_name,
            r.ip,
            r.puerto,
            r.estado,
            r.ultima_actividad,

            mr.uptime_seconds,
            mr.heartbeat_count,
            mr.routing_entries,
            mr.timestamp AS legacy_metrics_timestamp,

            mg.tamano_cola,
            mg.paquetes_enviados,
            mg.paquetes_descartados,
            mg.timestamp AS documented_metrics_timestamp,

            CASE
                WHEN mg.timestamp IS NULL AND mr.timestamp IS NULL THEN NULL
                WHEN mg.timestamp IS NULL THEN mr.timestamp
                WHEN mr.timestamp IS NULL THEN mg.timestamp
                WHEN mg.timestamp >= mr.timestamp THEN mg.timestamp
                ELSE mr.timestamp
            END AS metrics_timestamp

        FROM routers r

        LEFT JOIN metricas_router mr
            ON mr.id = (
                SELECT mri.id
                FROM metricas_router mri
                WHERE mri.router_id = r.id
                ORDER BY mri.timestamp DESC, mri.id DESC
                LIMIT 1
            )

        LEFT JOIN metricas_globales mg
            ON mg.id = (
                SELECT mgi.id
                FROM metricas_globales mgi
                WHERE mgi.router_id = r.id
                ORDER BY mgi.timestamp DESC, mgi.id DESC
                LIMIT 1
            )

        ORDER BY r.nombre ASC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return rows

    def display_network_status(self):
        """
        Print network status in a readable table format.
        """
        rows = self.get_network_status()

        print("")
        print("NETCORE - Network Status")
        print("=" * 160)

        if not rows:
            print("No routers registered.")
            print("=" * 160)
            return

        header = (
            f"{'Router':<10}"
            f"{'IP':<16}"
            f"{'Port':<8}"
            f"{'Status':<12}"
            f"{'Last activity':<22}"
            f"{'Uptime':<10}"
            f"{'HB':<8}"
            f"{'Routes':<8}"
            f"{'Queue':<8}"
            f"{'Forwarded':<12}"
            f"{'Discarded':<12}"
            f"{'Last metrics':<22}"
        )

        print(header)
        print("-" * 160)

        for row in rows:
            router_name = self.format_value(row["router_name"])
            ip = self.format_value(row["ip"])
            port = self.format_value(row["puerto"])
            status = self.format_value(row["estado"])
            last_activity = self.format_datetime(row["ultima_actividad"])

            uptime_seconds = self.format_value(row["uptime_seconds"])
            heartbeat_count = self.format_value(row["heartbeat_count"])
            routing_entries = self.format_value(row["routing_entries"])

            queue_size = self.format_value(row["tamano_cola"])
            packets_forwarded = self.format_value(row["paquetes_enviados"])
            packets_discarded = self.format_value(row["paquetes_descartados"])

            metrics_timestamp = self.format_datetime(row["metrics_timestamp"])

            line = (
                f"{router_name:<10}"
                f"{ip:<16}"
                f"{port:<8}"
                f"{status:<12}"
                f"{last_activity:<22}"
                f"{uptime_seconds:<10}"
                f"{heartbeat_count:<8}"
                f"{routing_entries:<8}"
                f"{queue_size:<8}"
                f"{packets_forwarded:<12}"
                f"{packets_discarded:<12}"
                f"{metrics_timestamp:<22}"
            )

            print(line)

        print("=" * 160)
        print("")

    @staticmethod
    def format_value(value):
        """
        Format None values for display.
        """
        if value is None:
            return "-"

        return str(value)

    @staticmethod
    def format_datetime(value):
        """
        Format datetime values for display.
        """
        if value is None:
            return "-"

        return value.strftime("%Y-%m-%d %H:%M:%S")


def main():
    cli = NetworkStatusCLI()
    cli.display_network_status()


if __name__ == "__main__":
    main()