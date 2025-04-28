import matplotlib.pyplot as plt
import networkx as nx

import matplotlib.pyplot as plt
import networkx as nx

def draw_topology(topo: 'Topology', controller: 'Controller'):
    G = topo.available_graph()

    if len(G.nodes) == 0:
        print("Topology is empty — nothing to draw.")
        return

    # Create a consistent layout
    pos = nx.spring_layout(G, seed=42)  # fixed seed so positions are stable

    fig, ax = plt.subplots()

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=500, ax=ax)

    # Draw edges with utilization coloring
    edges = G.edges(data=True)
    colors = [data.get('utilization', 0) for (_, _, data) in edges]
    nx.draw_networkx_edges(G, pos, edge_color=colors, edge_cmap=plt.cm.viridis, width=2, ax=ax)
    nx.draw_networkx_labels(G, pos, ax=ax)

    # Draw active flows
    # Draw active flows
    for flow in controller.flows.values():
        for path in flow.primary:
            valid_path = all(G.has_edge(u, v) for u, v in zip(path, path[1:]))
            if valid_path:
                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=list(zip(path, path[1:])),
                    width=4,
                    style='dashed' if flow.critical else 'solid',
                    ax=ax
                )

    plt.title("SDN Topology & Active Flows")

    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(vmin=0, vmax=100))
    sm.set_array([])
    fig.colorbar(sm, ax=ax, label='Link Utilization (%)')

    plt.axis('off')

    plt.ion()
    plt.show()
    plt.pause(0.001)
    plt.ioff()
