# SDN Controller Simulation

This project simulates a simple Software-Defined Networking (SDN) controller using Python. It manages network topology, configures flow tables on switches, handles link failures, and applies basic traffic engineering policies.

## Features

- Maintain a dynamic network topology (nodes, links)
- Compute shortest and backup paths for traffic flows
- Load balance flows over multiple paths when available
- Prioritize "video" and "voice" traffic differently
- Handle critical flows with backup paths
- Track and display link utilization
- Visualize network state with active flows
- Operator CLI to manage network and inject flows

## Running the Project

Run the CLI:
    ```bash
    python cli.py
    ```
Use CLI commands like:
    - `add_node <name>`
    - `add_link <node1> <node2> <weight>`
    - `inject_flow <src> <dst> <class> [critical]`
    - `fail_link <node1> <node2>`
    - `draw`
    - `show_routes <flow_id>`

Example session:

```bash
sdn> add_node A
sdn> add_node B
sdn> add_link A B 10
sdn> inject_flow A B video critical
sdn> draw
