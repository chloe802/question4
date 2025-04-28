import networkx as nx
import random

# define the topology class to manage the network graph
class Topology:
    # initialize the topology with an empty graph
    def __init__(self):
        self.graph = nx.Graph()

    # add a node to the network graph
    def add_node(self, node):
        self.graph.add_node(node)

    # remove a node from the network graph
    def remove_node(self, node):
        self.graph.remove_node(node)

    # add a link between two nodes with weight and utilization
    def add_link(self, u, v, weight=1.0):
        self.graph.add_edge(u, v, weight=weight, utilization=0)

    # remove a link between two nodes
    def remove_link(self, u, v):
        self.graph.remove_edge(u, v)

    # fail a link by removing it from the graph
    def fail_link(self, u, v):
        self.remove_link(u, v)

    # return a copy of the current available graph
    def available_graph(self):
        return self.graph.copy()

# define the flow class to represent individual network flows
class Flow:
    # initialize a flow with source, destination, class, and criticality
    def __init__(self, src, dst, traffic_class, critical=False):
        self.src = src
        self.dst = dst
        self.traffic_class = traffic_class
        self.critical = critical
        self.id = None
        self.primary = []
        self.backup = []

# define the controller class to manage flows and topology
class Controller:
    # initialize the controller with a topology, flows, and flow tables
    def __init__(self):
        self.topo = Topology()
        self.flows = {}
        self.tables = {}

    # compute multiple shortest paths between source and destination
    def compute_paths(self, src, dst, k=2):
        """Find k shortest paths (for load balancing and backup)."""
        G = self.topo.available_graph()
        try:
            paths = list(nx.shortest_simple_paths(G, src, dst, weight='weight'))
            return paths[:k]
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    # install a flow into the network and assign primary and backup paths
    def install_flow(self, flow):
        flow.id = len(self.flows)
        paths = self.compute_paths(flow.src, flow.dst, k=3)

        if not paths:
            print(f"No available path for flow {flow.src} -> {flow.dst}")
            return flow

        # policy to prioritize certain types of traffic
        if flow.traffic_class.lower() == "video":
            paths = sorted(paths, key=lambda p: self.path_utilization(p))  # least loaded
        elif flow.traffic_class.lower() == "voice":
            paths = sorted(paths, key=lambda p: self.path_delay(p))  # shortest
        else:
            random.shuffle(paths)  # load balance randomly

        flow.primary = [paths[0]]

        if flow.critical and len(paths) > 1:
            flow.backup = [paths[1]]

        # update link utilization along the primary path
        for path in flow.primary:
            self.increment_utilization(path)

        # build flow tables for the flow
        self.build_flow_tables(flow)

        return flow

    # calculate the total utilization along a given path
    def path_utilization(self, path):
        G = self.topo.graph
        return sum(G[u][v]['utilization'] for u, v in zip(path, path[1:]))

    # calculate the total delay along a given path
    def path_delay(self, path):
        G = self.topo.graph
        return sum(G[u][v]['weight'] for u, v in zip(path, path[1:]))

    # increment link utilization along a path
    def increment_utilization(self, path):
        G = self.topo.graph
        for u, v in zip(path, path[1:]):
            if G.has_edge(u, v):
                G[u][v]['utilization'] += 10  # assume each flow adds 10%

    # decrement link utilization along a path
    def decrement_utilization(self, path):
        G = self.topo.graph
        for u, v in zip(path, path[1:]):
            if G.has_edge(u, v):
                G[u][v]['utilization'] = max(0, G[u][v]['utilization'] - 10)

    # handle a link failure by rerouting affected flows
    def handle_link_failure(self, u, v):
        """Handle link failure: reroute any affected flows."""
        print(f"Handling failure of link {u}↔{v}")
        self.topo.fail_link(u, v)

        for flow in self.flows.values():
            affected = False
            for path in flow.primary:
                if (u, v) in zip(path, path[1:]) or (v, u) in zip(path, path[1:]):
                    affected = True
                    break
            if affected:
                # decrement utilization from old path
                for path in flow.primary:
                    self.decrement_utilization(path)

                if flow.backup:
                    flow.primary = flow.backup
                    flow.backup = []
                    print(f"Flow {flow.id} switched to backup path.")
                else:
                    new_paths = self.compute_paths(flow.src, flow.dst)
                    if new_paths:
                        flow.primary = [new_paths[0]]
                        print(f"Flow {flow.id} rerouted dynamically.")
                    else:
                        print(f"Flow {flow.id} dropped (no alternative path).")
                # update flow table and utilization
                self.build_flow_tables(flow)
                for path in flow.primary:
                    self.increment_utilization(path)

    # build the flow tables for switches based on the flow paths
    def build_flow_tables(self, flow):
        self.tables[flow.id] = {}
        for path in flow.primary:
            for u, v in zip(path, path[1:]):
                if u not in self.tables[flow.id]:
                    self.tables[flow.id][u] = []
                self.tables[flow.id][u].append({
                    'match': f"src={flow.src}, dst={flow.dst}, class={flow.traffic_class}",
                    'action': f"forward to {v}",
                    'priority': 100 if flow.critical else 10
                })

    # return flow information and corresponding flow table entries
    def query_flow(self, flow_id):
        flow = self.flows[flow_id]
        table = self.tables.get(flow.id, {})
        return flow, table