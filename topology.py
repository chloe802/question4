import networkx as nx

class Topology:
    def __init__(self):
        self.graph = nx.Graph()

    def add_node(self, node):
        self.graph.add_node(node)

    def remove_node(self, node):
        self.graph.remove_node(node)

    def add_link(self, u, v, weight=1):
        self.graph.add_edge(u, v, weight=weight, utilization=0)

    def remove_link(self, u, v):
        self.graph.remove_edge(u, v)

    def get_shortest_paths(self, src, dst):
        # returns all shortest paths (list of node lists)
        return list(nx.all_shortest_paths(self.graph, src, dst, weight='weight'))

    def fail_link(self, u, v):
        if self.graph.has_edge(u, v):
            self.graph[u][v]['failed'] = True

    def restore_link(self, u, v):
        if self.graph.has_edge(u, v):
            self.graph[u][v]['failed'] = False

    def available_graph(self):
        # returns a subgraph excluding failed links
        G = self.graph.copy()
        for u, v, data in list(G.edges(data=True)):
            if data.get('failed', False):
                G.remove_edge(u, v)
        return G
