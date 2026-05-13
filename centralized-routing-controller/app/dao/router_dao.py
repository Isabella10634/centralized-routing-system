import mysql.connector
from app.utils.db_config import DB_CONFIG


class RouterDAO:
    # DAO encargado de todas las operaciones sobre la tabla routers.
    def __init__(self):
        self.config = DB_CONFIG

    def connect(self):
        # Abre una conexión a MySQL usando la configuración local.
        return mysql.connector.connect(**self.config)

    def insert_router(self, nombre, ip, puerto, token, estado):
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        INSERT INTO routers (nombre, ip, puerto, token, estado)
        VALUES (%s, %s, %s, %s, %s)
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
        # Se usa para no duplicar routers al volver a registrar uno ya existente.
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
        # Si el router ya existe, se actualizan sus datos en vez de insertarlo otra vez.
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        UPDATE routers
        SET ip = %s, puerto = %s, token = %s, estado = %s
        WHERE nombre = %s
        """
        cursor.execute(query, (ip, puerto, token, estado, nombre))
        connection.commit()

        cursor.close()
        connection.close()