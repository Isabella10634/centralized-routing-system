from test_support import ControllerDatabaseTestCase


class TestDatabaseConnection(ControllerDatabaseTestCase):
    """
    Sprint 1 database validation tests.

    These tests verify that the controller can connect to MySQL and that
    the minimum required Sprint 1 tables exist.
    """

    def test_mysql_connection_is_available(self):
        connection = self.get_connection()

        self.assertTrue(connection.is_connected())

        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        self.assertEqual(result[0], 1)

        cursor.close()
        connection.close()

    def test_sprint_1_required_tables_exist(self):
        required_tables = {"routers", "enlaces", "eventos"}

        rows = self.fetch_all("SHOW TABLES")
        existing_tables = set()

        for row in rows:
            existing_tables.add(next(iter(row.values())))

        self.assertTrue(
            required_tables.issubset(existing_tables),
            f"Missing required tables: {required_tables - existing_tables}"
        )


if __name__ == "__main__":
    import unittest
    unittest.main()