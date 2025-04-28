# SDN Controller Simulation

This project simulates a basic Software-Defined Networking controller using Python.  
The controller manages a dynamic network topology, installs flow table entries, responds to link failures, and applies traffic engineering strategies like load balancing, traffic prioritization, and backup path setup for critical flows.  
There’s also a live visualization that shows the network state as you interact with it.

---

## Features

- Manage a dynamic network topology (add/remove nodes and links)
- Compute shortest paths between nodes
- Install flow tables dynamically based on active flows
- Load-balance traffic across multiple available paths
- Prioritize video and voice traffic differently
- Set up backup paths for critical flows
- Handle link failures by rerouting or recovering flows
- Visualize the network, active flows, and link utilization
- Simple CLI for operator interaction

---

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/sdn-controller-sim.git
    cd sdn-controller-sim
    ```

2. Set up a Python virtual environment (recommended):
    ```bash
    python -m venv .venv

    .\.venv\Scripts\activate 
    ```

3. Install the required libraries:
    ```bash
    pip install networkx matplotlib
    ```

---

## How to Run

Run the CLI:

```bash
python cli.py


EXAMPLES: 

add_node A
add_node B
add_node C
add_link A B 10
add_link B C 5
add_link A C 15


inject_flow A C video critical
inject_flow B C data
inject_flow A B voice

draw

fail_link A B

show_routes 1
show_routes 2
show_routes 3

remove_node C
draw

exit
