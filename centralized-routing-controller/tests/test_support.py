import os
import sys
import unittest

import mysql.connector


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.utils.db_config import DB_CONFIG


class ControllerDatabaseTestCase(unittest.TestCase):
    """
    Base class for controller tests.

    This class centralizes:
    - MySQL connection using the official controller configuration.
    - Cleanup of TEST_ data before and after each test.
    - Reusable helpers to query the database.

    Test data always uses the TEST_ prefix so tests can be repeated
    without damaging real project data.
    """

    TEST_PREFIX = "TEST_"

    def setUp(self):
        self.clean_test_data()

    def tearDown(self):
        self.clean_test_data()

    def get_connection(self):
        """
        Create a MySQL connection using the official controller configuration.
        """
        return mysql.connector.connect(**DB_CONFIG)

    def table_exists(self, table_name):
        """
        Verify whether a table exists in the configured database.
        """
        connection = self.get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s
            """,
            (DB_CONFIG["database"], table_name)
        )

        exists = cursor.fetchone()[0] > 0

        cursor.close()
        connection.close()

        return exists

    def clean_test_data(self):
        """
        Delete only automated test data.

        Important order:
        1. metricas_globales
        2. metricas_router
        3. rutas_calculadas
        4. enlaces
        5. eventos
        6. routers

        This avoids foreign key problems when deleting test routers.
        """
        if not self.table_exists("routers"):
            return

        connection = self.get_connection()
        cursor = connection.cursor()

        if self.table_exists("metricas_globales"):
            cursor.execute(
                """
                DELETE mg
                FROM metricas_globales mg
                INNER JOIN routers r ON mg.router_id = r.id
                WHERE r.nombre LIKE %s
                """,
                (f"{self.TEST_PREFIX}%",)
            )

            cursor.execute(
                """
                DELETE FROM metricas_globales
                WHERE router_nombre LIKE %s
                """,
                (f"{self.TEST_PREFIX}%",)
            )

        if self.table_exists("metricas_router"):
            cursor.execute(
                """
                DELETE mr
                FROM metricas_router mr
                INNER JOIN routers r ON mr.router_id = r.id
                WHERE r.nombre LIKE %s
                """,
                (f"{self.TEST_PREFIX}%",)
            )

            cursor.execute(
                """
                DELETE FROM metricas_router
                WHERE router_nombre LIKE %s
                """,
                (f"{self.TEST_PREFIX}%",)
            )

        if self.table_exists("rutas_calculadas"):
            cursor.execute(
                """
                DELETE rc
                FROM rutas_calculadas rc
                INNER JOIN routers ro ON rc.router_origen_id = ro.id
                WHERE ro.nombre LIKE %s
                """,
                (f"{self.TEST_PREFIX}%",)
            )

            cursor.execute(
                """
                DELETE rc
                FROM rutas_calculadas rc
                INNER JOIN routers rd ON rc.router_destino_id = rd.id
                WHERE rd.nombre LIKE %s
                """,
                (f"{self.TEST_PREFIX}%",)
            )

        if self.table_exists("enlaces"):
            cursor.execute(
                """
                DELETE e
                FROM enlaces e
                INNER JOIN routers ro ON e.router_origen_id = ro.id
                WHERE ro.nombre LIKE %s
                """,
                (f"{self.TEST_PREFIX}%",)
            )

            cursor.execute(
                """
                DELETE e
                FROM enlaces e
                INNER JOIN routers rd ON e.router_destino_id = rd.id
                WHERE rd.nombre LIKE %s
                """,
                (f"{self.TEST_PREFIX}%",)
            )

        if self.table_exists("eventos"):
            cursor.execute(
                """
                DELETE FROM eventos
                WHERE descripcion LIKE %s
                """,
                (f"%{self.TEST_PREFIX}%",)
            )

        cursor.execute(
            """
            DELETE FROM routers
            WHERE nombre LIKE %s
            """,
            (f"{self.TEST_PREFIX}%",)
        )

        connection.commit()

        cursor.close()
        connection.close()

    def fetch_one(self, query, params=None):
        """
        Execute a SELECT query and return one row as a dictionary.
        """
        connection = self.get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, params or ())
        row = cursor.fetchone()

        cursor.close()
        connection.close()

        return row

    def fetch_all(self, query, params=None):
        """
        Execute a SELECT query and return all rows as dictionaries.
        """
        connection = self.get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, params or ())
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return rows