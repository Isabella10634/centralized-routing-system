import socket
import threading
import time


from app.network.tcp_server import TCPServer

HOST = "localhost"
PORT = 6000


def run_server():
    server = TCPServer(HOST, PORT)
    server.start()



def test_controller_tcp_server():

    # levantar controller en un hilo separado
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # esperar un momento para que el socket abra
    time.sleep(2)

    # intentar conectarse al socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    result = client_socket.connect_ex((HOST, PORT))

    client_socket.close()

    # connect_ex devuelve 0 si la conexión fue exitosa
    assert result == 0