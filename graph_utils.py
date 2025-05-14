# graph_utils.py
import networkx as nx
import random
import numpy as np

def create_random_weighted_graph(num_nodes, edge_prob=0.15, seed=None):
    """Creates a random weighted directed graph."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    G = nx.DiGraph()
    if num_nodes <= 0:
        return G # Return empty graph if num_nodes is invalid

    nodes = list(range(num_nodes))
    G.add_nodes_from(nodes)

    max_weight = 10 # Max random weight for an edge

    for i in nodes:
        for j in nodes:
            if i != j and random.random() < edge_prob:
                weight = random.randint(1, max_weight)
                G.add_edge(i, j, weight=weight)

    # Ensure graph is not entirely disconnected (optional, but good for demo)
    if num_nodes > 1 and not nx.is_weakly_connected(G):
         # Add a few edges to try and connect components if needed
         for i in range(num_nodes - 1):
             if not G.has_edge(i, i + 1) and not G.has_edge(i+1, i):
                 weight = random.randint(1, max_weight)
                 if random.random() > 0.5:
                    G.add_edge(i, i + 1, weight=weight)
                 else:
                    G.add_edge(i+1, i, weight=weight)


    # Basic check for empty graph after potential modifications
    if G.number_of_nodes() == 0 and num_nodes > 0:
        G.add_node(0) # Add at least one node if it became empty


    return G

def calculate_layout(G, seed=None):
    """Calculates a 3D spring layout for the graph."""
    if not G: # Handle empty graph
        return {}

    if seed is not None:
        np.random.seed(seed)

    # Use spring layout in 3D
    # Adjust k for spacing, iterations for convergence
    pos = nx.spring_layout(G, dim=3, seed=seed, k=0.8/np.sqrt(len(G)), iterations=50)
    return pos