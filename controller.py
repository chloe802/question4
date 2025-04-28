import itertools
from topology import Topology

class Flow:
    _id_iter = itertools.count(1)

    def __init__(self, src, dst, cls, critical=False):
        self.id = next(Flow._id_iter)
        self.src = src
        self.dst = dst
        self.cls = cls
        self.critical = critical
        self.primary = []
        self.backup = []

class Controller:
    def __init__(self):
        self.topo = Topology()
        self.flows = {}           # flow_id -> Flow
        self.flow_tables = {}     # switch -> list of flow entries

    def install_flow(self, flow: Flow):
        G = self.topo.available_graph()
        # 1) compute all shortest paths
        paths = list(nx.all_shortest_paths(G, flow.src, flow.dst, weight='weight'))
        # 2) load-balance primary across paths
        flow.primary = paths
        # 3) if critical, pick a backup disjoint path
        if flow.critical:
            sp = paths[0]
            # remove edges in primary, then shortest path for backup
            G2 = G.copy()
            G2.remove_edges_from(zip(sp, sp[1:]))
            try:
                flow.backup = nx.shortest_path(G2, flow.src, flow.dst, weight='weight')
            except nx.NetworkXNoPath:
                flow.backup = []
        self.flows[flow.id] = flow
        self._push_to_switches(flow)

    def _push_to_switches(self, flow: Flow):
        # for every switch on path, add or update entries
        for path in flow.primary + ([flow.backup] if flow.backup else []):
            if not path: continue
            for u, v in zip(path, path[1:]):
                entry = {
                    'match': (flow.src, flow.dst, flow.cls),
                    'action': ('OUTPUT', v),
                    'priority': 10 if flow.critical else 1
                }
                self.flow_tables.setdefault(u, []).append(entry)

    def handle_link_failure(self, u, v):
        self.topo.fail_link(u, v)
        # reconfigure all flows
        for flow in self.flows.values():
            self.flow_tables.clear()
            self.install_flow(flow)

    def query_flow(self, fid):
        return self.flows.get(fid), self.flow_tables
