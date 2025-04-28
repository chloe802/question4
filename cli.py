import cmd, sys
import networkx as nx
from controller import Controller, Flow
from visual import draw_topology

class SDNCli(cmd.Cmd):
    intro = "Welcome to the SDN Controller CLI. Type help or ? to list commands.\n"
    prompt = "sdn> "

    # define the command line interface class for interacting with the sdn controller
    class SDNCli(cmd.Cmd):
        # introductory message when cli starts
        intro = "Welcome to the SDN Controller CLI. Type help or ? to list commands.\n"
        # prompt displayed for user input
        prompt = "sdn> "

        # initialize the sdncli with a controller object
        def __init__(self):
            super().__init__()
            self.ctrl = Controller()

        # add a node to the network topology
        def do_add_node(self, arg):
            """add_node <name>"""
            if not arg:
                print("Usage: add_node <name>")
                return
            self.ctrl.topo.add_node(arg)
            print(f"Node {arg} added.")

        # remove a node from the network topology
        def do_remove_node(self, arg):
            """remove_node <name>"""
            if not arg:
                print("Usage: remove_node <name>")
                return
            self.ctrl.topo.remove_node(arg)
            print(f"Node {arg} removed.")

        # add a link between two nodes in the topology
        def do_add_link(self, arg):
            """add_link <u> <v> <weight>"""
            parts = arg.split()
            if len(parts) != 3:
                print("Usage: add_link <u> <v> <weight>")
                return
            u, v, w = parts
            self.ctrl.topo.add_link(u, v, weight=float(w))
            print(f"Link {u}↔{v} weight={w} added.")

        # remove a link between two nodes in the topology
        def do_remove_link(self, arg):
            """remove_link <u> <v>"""
            parts = arg.split()
            if len(parts) != 2:
                print("Usage: remove_link <u> <v>")
                return
            u, v = parts
            self.ctrl.topo.remove_link(u, v)
            print(f"Link {u}↔{v} removed.")

        # inject a new flow into the network with optional critical flag
        def do_inject_flow(self, arg):
            """inject_flow <src> <dst> <class> [critical]"""
            parts = arg.split()
            if len(parts) < 3:
                print("Usage: inject_flow <src> <dst> <class> [critical]")
                return
            critical = len(parts) == 4 and parts[3].lower() == "critical"
            flow = self.ctrl.install_flow(
                self.ctrl.flows.setdefault(
                    len(self.ctrl.flows) + 1,
                    Flow(parts[0], parts[1], parts[2], critical)
                )
            )
            print(f"Flow {flow.id} injected: primary={flow.primary} backup={flow.backup}")

        # simulate a link failure between two nodes
        def do_fail_link(self, arg):
            """fail_link <u> <v>"""
            parts = arg.split()
            if len(parts) != 2:
                print("Usage: fail_link <u> <v>")
                return
            u, v = parts
            self.ctrl.handle_link_failure(u, v)
            print(f"Link {u}↔{v} failed and flows reconfigured.")

        # show the routing information for a given flow id
        def do_show_routes(self, arg):
            """show_routes <flow_id>"""
            if not arg.isdigit():
                print("Usage: show_routes <flow_id>")
                return
            flow, tables = self.ctrl.query_flow(int(arg))
            print(f"Flow {flow.id}: primary={flow.primary}, backup={flow.backup}")
            print("Flow tables:")
            for sw, entries in tables.items():
                print(f"  Switch {sw}:")
                for e in entries:
                    print(f"    match={e['match']} → action={e['action']} prio={e['priority']}")

        # draw the current network topology and flows
        def do_draw(self, arg):
            """draw"""
            draw_topology(self.ctrl.topo, self.ctrl)

        # exit the command line interface
        def do_exit(self, arg):
            """exit"""
            print("Goodbye.")
            return True

    # start the command loop if the script is run directly
    if __name__ == '__main__':
        SDNCli().cmdloop()
