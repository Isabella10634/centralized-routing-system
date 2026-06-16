import mysql.connector

from app.utils.db_config import DB_CONFIG


class RouterDAO:
    """
    DAO responsible for all database operations related to routers.

    Sprint 1:
    - Insert routers.
    - Update router information.
    - Query registered routers.

    Sprint 3:
    - Update router heartbeat timestamp.
    - Mark routers as inactive when heartbeat timeout is exceeded.
    """

    def __init__(self):
        self.config = DB_CONFIG

    def connect(self):
        """
        Open a MySQL connection using the local database configuration.
        """
        return mysql.connector.connect(**self.config)

    def insert_router(self, nombre, ip, puerto, token, estado):
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        INSERT INTO routers (nombre, ip, puerto, token, estado, ultima_actividad)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """
        values = (nombre, ip, puerto, token, estado)

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

    def get_all_routers(self):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM routers"
        cursor.execute(query)
        routers = cursor.fetchall()

        cursor.close()
        connection.close()

        return routers

    def get_router_by_name(self, nombre):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM routers WHERE nombre = %s"
        cursor.execute(query, (nombre,))
        router = cursor.fetchone()

        cursor.close()
        connection.close()

        return router

    def router_exists(self, nombre):
        connection = self.connect()
        cursor = connection.cursor()

        query = "SELECT COUNT(*) FROM routers WHERE nombre = %s"
        cursor.execute(query, (nombre,))
        result = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return result > 0

    def update_router_status(self, nombre, nuevo_estado):
        connection = self.connect()
        cursor = connection.cursor()

        query = "UPDATE routers SET estado = %s WHERE nombre = %s"
        cursor.execute(query, (nuevo_estado, nombre))
        connection.commit()

        cursor.close()
        connection.close()

    def update_router_info(self, nombre, ip, puerto, token, estado):
        """
        Update router information when the router already exists.
        """
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        UPDATE routers
        SET ip = %s,
            puerto = %s,
            token = %s,
            estado = %s,
            ultima_actividad = NOW()
        WHERE nombre = %s
        """
        cursor.execute(query, (ip, puerto, token, estado, nombre))
        connection.commit()

        cursor.close()
        connection.close()

    def update_router_heartbeat(self, nombre):
        """
        Update the last activity timestamp of a router and mark it as active.

        Important:
        MySQL cursor.rowcount can be 0 if the row already had the same values
        within the same second. Therefore, router existence must be verified
        directly instead of relying only on rowcount.
        """
        connection = self.connect()
        cursor = connection.cursor()

        exists_query = """
        SELECT COUNT(*)
        FROM routers
        WHERE nombre = %s
        """
        cursor.execute(exists_query, (nombre,))
        exists = cursor.fetchone()[0] > 0

        if not exists:
            cursor.close()
            connection.close()
            return False

        update_query = """
        UPDATE routers
        SET estado = %s,
            ultima_actividad = NOW()
        WHERE nombre = %s
        """
        cursor.execute(update_query, ("activo", nombre))
        connection.commit()

        cursor.close()
        connection.close()

        return True

    def mark_inactive_routers(self, timeout_seconds):
        """
        Mark routers as inactive when their last activity is older than timeout_seconds.
        """
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        UPDATE routers
        SET estado = %s
        WHERE ultima_actividad IS NOT NULL
          AND TIMESTAMPDIFF(SECOND, ultima_actividad, NOW()) > %s
        """
        cursor.execute(query, ("inactivo", timeout_seconds))
        connection.commit()

        affected_rows = cursor.rowcount

        cursor.close()
        connection.close()

        return affected_rows