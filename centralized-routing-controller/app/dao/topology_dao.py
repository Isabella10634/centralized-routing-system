import mysql.connector
from app.utils.db_config import DB_CONFIG


class TopologyDAO:
    # DAO encargado de la tabla enlaces.
    def __init__(self):
        self.config = DB_CONFIG

    def connect(self):
        return mysql.connector.connect(**self.config)

    def link_exists(self, router_origen_id, router_destino_id):
        # Verifica si el enlace ya existe para evitar duplicados.
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
        # Si el enlace ya existe, se actualiza su costo/estado.
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
        # Metodo unificado: inserta o actualiza según corresponda.
        if self.link_exists(router_origen_id, router_destino_id):
            self.update_link(router_origen_id, router_destino_id, costo, estado)
        else:
            self.insert_link(router_origen_id, router_destino_id, costo, estado)

    def get_all_links(self):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM enlaces"
        cursor.execute(query)
        links = cursor.fetchall()

        cursor.close()
        connection.close()

        return links

    def get_links_by_origin(self, router_origen_id):
        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM enlaces WHERE router_origen_id = %s"
        cursor.execute(query, (router_origen_id,))
        links = cursor.fetchall()

        cursor.close()
        connection.close()

        return links

    def update_link_cost(self, router_origen_id, router_destino_id, nuevo_costo):
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