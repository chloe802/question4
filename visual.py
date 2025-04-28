import matplotlib.pyplot as plt
import networkx as nx

def draw_topology(topo: 'Topology', controller: 'Controller'):
    G = topo.available_graph()
    pos = nx.spring_layout(G)
    # draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=500)
    # color links by utilization
    edges = G.edges(data=True)
    colors = [data.get('utilization', 0) for (_,_,data) in edges]
    nx.draw_networkx_edges(G, pos, edge_color=colors, edge_cmap=plt.cm.viridis, width=2)
    nx.draw_networkx_labels(G, pos)
    # overlay flows
    for flow in controller.flows.values():
        for path in flow.primary:
            nx.draw_networkx_edges(G, pos, edgelist=list(zip(path, path[1:])),
                                   width=4, style='dashed' if flow.critical else 'solid')
    plt.title("SDN Topology & Active Flows")
    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis,
                               norm=plt.Normalize(vmin=0, vmax=100))
    sm.set_array([])
    plt.colorbar(sm, label='Link Utilization (%)')
    plt.axis('off')
    plt.show()
