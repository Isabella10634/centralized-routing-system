import sys

from app.controllers.forwarding_controller import ForwardingController
from app.views.forwarding_view import ForwardingView


def main():
    """
    CLI entry point for Sprint 2 packet forwarding simulation.

    Usage:
        python -m app.cli.packet_sim_cli R1 R2
        python -m app.cli.packet_sim_cli R1 R3
        python -m app.cli.packet_sim_cli R2 R3
    """
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python -m app.cli.packet_sim_cli <router_name> <destination>")
        print("")
        print("Examples:")
        print("  python -m app.cli.packet_sim_cli R1 R2")
        print("  python -m app.cli.packet_sim_cli R1 R3")
        print("  python -m app.cli.packet_sim_cli R2 R3")
        sys.exit(1)

    router_name = sys.argv[1]
    destination = sys.argv[2]

    controller = ForwardingController(router_name)
    result = controller.simulate_packet_forwarding(destination)

    ForwardingView.display(result)


if __name__ == "__main__":
    main()