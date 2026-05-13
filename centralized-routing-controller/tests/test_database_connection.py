import mysql.connector


def test_mysql_connection():
    config = {
        "host": "localhost",
        "user": "root",
        "password": "daniel",
        "database": "centralized_routing_controller"
    }

    connection = mysql.connector.connect(**config)

    assert connection.is_connected()

    cursor = connection.cursor()
    cursor.execute("SELECT 1")

    result = cursor.fetchone()

    assert result[0] == 1

    cursor.close()
    connection.close()