import json
import socket
import threading
import time
import mysql.connector

from app.network.tcp_server import TCPServer


HOST = "127.0.0.1"
PORT = 7000


def run_server():
    server = TCPServer(HOST, PORT)
    server.start()


def test_router_registry():

    # iniciar controller
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    time.sleep(2)

    # crear cliente TCP simulando router
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((HOST, PORT))

    # mensaje AUTH
    auth_message = {
        "type": "AUTH",
        "router_id": "TEST_ROUTER",
        "ip": "127.0.0.1",
        "port": 9999,
        "token": "test_token"
    }

    client_socket.send(json.dumps(auth_message).encode("utf-8"))

    # recibir respuesta
    response = client_socket.recv(1024)

    parsed_response = json.loads(response.decode("utf-8"))

    assert parsed_response["type"] == "AUTH_OK"

    client_socket.close()

    # esperar inserción DB
    time.sleep(1)

    # verificar en MySQL
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="daniel",
        database="centralized_routing_controller"
    )

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM routers WHERE nombre = %s",
        ("TEST_ROUTER",)
    )

    router = cursor.fetchone()

    assert router is not None
    assert router["nombre"] == "TEST_ROUTER"

    cursor.close()
    connection.close()