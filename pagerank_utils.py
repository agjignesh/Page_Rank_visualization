# pagerank_utils.py
import numpy as np

def pagerank_weighted_iterative(G, alpha=0.85, personalization=None,
                                max_iter=100, tol=1.0e-6, weight='weight',
                                dangling=None, initial_scores=None):
    """
    Calculate PageRank using power iteration for a weighted graph.

    Args:
        G (nx.DiGraph): The graph.
        alpha (float): Damping factor.
        personalization (dict, optional): Personalization vector.
        max_iter (int): Maximum iterations.
        tol (float): Tolerance for convergence.
        weight (str): Edge attribute key for weights.
        dangling (dict, optional): Distribution for dangling nodes.
        initial_scores (dict, optional): Starting PageRank scores.

    Returns:
        tuple: (dict: final PageRank scores, list: history of scores per iteration)
    """
    
    N = len(G)
    if N == 0:
        return {}, []

    # Initial vector
    if initial_scores is None:
        x = {n: 1.0 / N for n in G}
    else:
        s = float(sum(initial_scores.values()))
        if s == 0: # Handle case where initial scores are all zero
             x = {n: 1.0 / N for n in G}
        else:
            x = {k: v / s for k, v in initial_scores.items()}

    history = [x.copy()] # Store initial state

    # Personalization vector (uniform if not specified)
    if personalization is None:
        p = {n: 1.0 / N for n in G}
    else:
        missing = set(G) - set(personalization)
        if missing:
            raise ValueError(f"Personalization vector missing nodes: {missing}")
        s = float(sum(personalization.values()))
        if s == 0:
             p = {n: 1.0 / N for n in G} # Fallback if personalization sums to 0
        else:
            p = {k: v / s for k, v in personalization.items()}


    # Dangling nodes (nodes with no outgoing weighted links)
    dangling_nodes = [n for n in G if G.out_degree(n, weight=weight) == 0.0]
    if dangling is None:
        # Use personalization vector if dangling vector not specified
        dangling_weights = p
    else:
        missing = set(G) - set(dangling)
        if missing:
             raise ValueError(f"Dangling vector missing nodes: {missing}")
        s = float(sum(dangling.values()))
        if s == 0:
            dangling_weights = p # Fallback if dangling sums to 0
        else:
            dangling_weights = {k: v / s for k, v in dangling.items()}


    # Power iteration
    converged = False
    for iteration in range(max_iter):
        xlast = x
        x = {n: 0.0 for n in G} # Initialize current iteration scores to zero
        danglesum = alpha * sum(xlast[n] for n in dangling_nodes)

        # Process incoming links for each node
        for n in G:
            for j in G.predecessors(n): # j is a node pointing to n
                out_degree_j = G.out_degree(j, weight=weight)
                if out_degree_j > 0:
                    edge_weight = G[j][n].get(weight, 1.0) # Default weight 1 if missing
                    x[n] += alpha * xlast[j] * (edge_weight / out_degree_j)

            # Add contribution from dangling nodes and personalization/teleportation
            x[n] += danglesum * dangling_weights.get(n, 0) + (1.0 - alpha) * p.get(n, 0)

        history.append(x.copy()) # Store current iteration state

        # Check convergence (L1 norm)
        err = sum(abs(x[n] - xlast[n]) for n in x)
        if err < N * tol:
            converged = True
            # print(f"Converged after {iteration + 1} iterations.") # For debugging
            break

    if not converged:
        print(f"Warning: PageRank did not converge within {max_iter} iterations.")

    return x, history