import mysql.connector
from app.utils.db_config import DB_CONFIG


class LogDAO:
    # DAO para registrar historial de eventos del sistema.
    def __init__(self):
        self.config = DB_CONFIG

    def connect(self):
        return mysql.connector.connect(**self.config)

    def insert_event(self, tipo, descripcion, timestamp):
        connection = self.connect()
        cursor = connection.cursor()

        query = """
        INSERT INTO eventos (tipo, descripcion, timestamp)
        VALUES (%s, %s, %s)
        """
        values = (tipo, descripcion, timestamp)

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

    def get_all_events(self):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM eventos"
        cursor.execute(query)
        events = cursor.fetchall()

        cursor.close()
        connection.close()

        return events