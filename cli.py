import cmd, sys
import networkx as nx
from controller import Controller, Flow
from visual import draw_topology

class SDNCli(cmd.Cmd):
    intro = "Welcome to the SDN Controller CLI. Type help or ? to list commands.\n"
    prompt = "sdn> "

    def __init__(self):
        super().__init__()
        self.ctrl = Controller()

    def do_add_node(self, arg):
        """add_node <name>"""
        self.ctrl.topo.add_node(arg)
        print(f"Node {arg} added.")

    def do_remove_node(self, arg):
        """remove_node <name>"""
        self.ctrl.topo.remove_node(arg)
        print(f"Node {arg} removed.")

    def do_add_link(self, arg):
        """add_link <u> <v> <weight>"""
        u, v, w = arg.split()
        self.ctrl.topo.add_link(u, v, weight=float(w))
        print(f"Link {u}↔{v} weight={w} added.")

    def do_remove_link(self, arg):
        """remove_link <u> <v>"""
        u, v = arg.split()
        self.ctrl.topo.remove_link(u, v)
        print(f"Link {u}↔{v} removed.")

    def do_inject_flow(self, arg):
        """inject_flow <src> <dst> <class> [critical]"""
        parts = arg.split()
        critical = len(parts)==4 and parts[3].lower()=="critical"
        flow = self.ctrl.install_flow(self.ctrl.flows.setdefault(len(self.ctrl.flows)+1,
                        Flow(parts[0], parts[1], parts[2], critical)))
        print(f"Flow {flow.id} injected: primary={flow.primary} backup={flow.backup}")

    def do_fail_link(self, arg):
        """fail_link <u> <v>"""
        u, v = arg.split()
        self.ctrl.handle_link_failure(u, v)
        print(f"Link {u}↔{v} failed and flows reconfigured.")

    def do_show_routes(self, arg):
        """show_routes <flow_id>"""
        flow, tables = self.ctrl.query_flow(int(arg))
        print(f"Flow {flow.id}: primary={flow.primary}, backup={flow.backup}")
        print("Flow tables:")
        for sw, entries in tables.items():
            print(f"  Switch {sw}:")
            for e in entries:
                print(f"    match={e['match']} → action={e['action']} prio={e['priority']}")

    def do_draw(self, arg):
        """draw"""
        draw_topology(self.ctrl.topo, self.ctrl)

    def do_exit(self, arg):
        """exit"""
        print("Goodbye.")
        return True

if __name__ == '__main__':
    SDNCli().cmdloop()
