import math
import os
from html import escape

from app.controllers.routing_controller import RoutingController


def _calculate_router_positions(router_names, width, height, radius):
    """
    Calculate circular positions for routers in the SVG diagram.
    """
    center_x = width / 2
    center_y = height / 2

    positions = {}

    total = len(router_names)

    for index, router_name in enumerate(router_names):
        angle = (2 * math.pi * index / total) - (math.pi / 2)

        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)

        positions[router_name] = (x, y)

    return positions


def _shorten_line(start_x, start_y, end_x, end_y, offset):
    """
    Shorten a directed edge so the arrow does not enter the router circle.
    """
    dx = end_x - start_x
    dy = end_y - start_y

    distance = math.sqrt(dx * dx + dy * dy)

    if distance == 0:
        return start_x, start_y, end_x, end_y

    unit_x = dx / distance
    unit_y = dy / distance

    new_start_x = start_x + unit_x * offset
    new_start_y = start_y + unit_y * offset
    new_end_x = end_x - unit_x * offset
    new_end_y = end_y - unit_y * offset

    return new_start_x, new_start_y, new_end_x, new_end_y


def _build_svg(graph):
    """
    Build an SVG drawing for the active topology graph.
    """
    width = 900
    height = 650
    radius = 230
    node_radius = 34

    router_names = sorted(graph.keys())
    positions = _calculate_router_positions(router_names, width, height, radius)

    svg_parts = []

    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    )

    svg_parts.append(
        """
        <defs>
            <marker id="arrow" markerWidth="10" markerHeight="10"
                    refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
                <path d="M0,0 L0,6 L9,3 z" fill="#333333" />
            </marker>
        </defs>
        """
    )

    svg_parts.append(
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff" />'
    )

    svg_parts.append(
        '<text x="450" y="40" text-anchor="middle" '
        'font-family="Arial" font-size="24" font-weight="bold">'
        'NETCORE - Active Network Topology'
        '</text>'
    )

    svg_parts.append(
        '<text x="450" y="68" text-anchor="middle" '
        'font-family="Arial" font-size="14" fill="#555555">'
        'Directed weighted graph used by Dijkstra'
        '</text>'
    )

    for source_router in router_names:
        neighbors = graph[source_router]

        for neighbor in neighbors:
            destination_router = neighbor["to"]
            cost = neighbor["cost"]

            if destination_router not in positions:
                continue

            start_x, start_y = positions[source_router]
            end_x, end_y = positions[destination_router]

            line_start_x, line_start_y, line_end_x, line_end_y = _shorten_line(
                start_x,
                start_y,
                end_x,
                end_y,
                node_radius + 4
            )

            middle_x = (line_start_x + line_end_x) / 2
            middle_y = (line_start_y + line_end_y) / 2

            svg_parts.append(
                f'<line x1="{line_start_x:.2f}" y1="{line_start_y:.2f}" '
                f'x2="{line_end_x:.2f}" y2="{line_end_y:.2f}" '
                f'stroke="#333333" stroke-width="2.2" '
                f'marker-end="url(#arrow)" />'
            )

            svg_parts.append(
                f'<rect x="{middle_x - 18:.2f}" y="{middle_y - 14:.2f}" '
                f'width="36" height="22" rx="6" ry="6" '
                f'fill="#ffffff" stroke="#999999" />'
            )

            svg_parts.append(
                f'<text x="{middle_x:.2f}" y="{middle_y + 5:.2f}" '
                f'text-anchor="middle" font-family="Arial" '
                f'font-size="13" font-weight="bold" fill="#111111">'
                f'{escape(str(cost))}'
                f'</text>'
            )

    for router_name in router_names:
        x, y = positions[router_name]

        svg_parts.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{node_radius}" '
            f'fill="#e8f1ff" stroke="#1f4e79" stroke-width="3" />'
        )

        svg_parts.append(
            f'<text x="{x:.2f}" y="{y + 6:.2f}" text-anchor="middle" '
            f'font-family="Arial" font-size="18" font-weight="bold" '
            f'fill="#1f4e79">{escape(router_name)}</text>'
        )

    svg_parts.append("</svg>")

    return "\n".join(svg_parts)


def _print_ascii_topology(graph):
    """
    Print the topology in text form for terminal evidence.
    """
    print("")
    print("NETCORE - Active Topology")
    print("=" * 70)

    if not graph:
        print("No active routers found.")
        print("=" * 70)
        return

    for router_name in sorted(graph.keys()):
        neighbors = graph[router_name]

        if not neighbors:
            print(f"{router_name} -> No outgoing active links")
            continue

        links_text = []

        for neighbor in neighbors:
            links_text.append(f"{neighbor['to']} (cost {neighbor['cost']})")

        print(f"{router_name} -> {', '.join(links_text)}")

    print("=" * 70)


def main():
    """
    CLI command to generate a visual SVG diagram of the active topology.

    Usage:
        python -m app.cli.topology_diagram_cli

    Output:
        centralized-routing-controller/outputs/network_topology.svg
    """
    routing_controller = RoutingController()
    graph = routing_controller.get_active_topology_graph()

    _print_ascii_topology(graph)

    output_directory = os.path.join(os.getcwd(), "outputs")
    os.makedirs(output_directory, exist_ok=True)

    output_path = os.path.join(output_directory, "network_topology.svg")

    svg_content = _build_svg(graph)

    with open(output_path, "w", encoding="utf-8") as svg_file:
        svg_file.write(svg_content)

    print("")
    print("Topology diagram generated successfully.")
    print(f"File: {output_path}")
    print("")
    print("Open it with:")
    print(f'  start "{output_path}"')


if __name__ == "__main__":
    main()