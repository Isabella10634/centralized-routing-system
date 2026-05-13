from app.dao.router_dao import RouterDAO
from app.dao.topology_dao import TopologyDAO
from app.dao.log_dao import LogDAO
from app.network.tcp_server import TCPServer


def main():
    router_dao = RouterDAO()
    topology_dao = TopologyDAO()
    log_dao = LogDAO()

    print("Controller started successfully.")
    print("Connection to MySQL database established.")

    print("Routers:", router_dao.get_all_routers())
    print("Links:", topology_dao.get_all_links())
    print("Events:", log_dao.get_all_events())

    server = TCPServer()
    server.start()


if __name__ == "__main__":
    main()