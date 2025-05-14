# plot_utils.py
import plotly.graph_objects as go
import networkx as nx # Needed for degree calculation in hover text

def create_3d_figure(G, pos, node_scores, current_iter, G_nodes_list, G_edges_list, alpha):
    """Creates the 3D Plotly figure for a specific iteration."""

    if not G or not pos: # Handle empty graph/pos
         return go.Figure()

    # --- Prepare Edge Data ---
    edge_x, edge_y, edge_z = [], [], []
    for u, v, data in G_edges_list:
        if u in pos and v in pos: # Ensure nodes exist in pos dict
            x0, y0, z0 = pos[u]
            x1, y1, z1 = pos[v]
            edge_x.extend([x0, x1, None]) # None separates lines
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])
        else:
            print(f"Warning: Node position missing for edge ({u}, {v})")


    trace_edges = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines',
        name='Edges'
    )

    # --- Prepare Node Data ---
    node_x = [pos[node][0] for node in G_nodes_list if node in pos]
    node_y = [pos[node][1] for node in G_nodes_list if node in pos]
    node_z = [pos[node][2] for node in G_nodes_list if node in pos]

    # Calculate node sizes and colors based on scores
    min_size, max_size = 8, 40 # Adjust min/max marker size
    current_scores_list = [node_scores.get(node, 0) for node in G_nodes_list] # Get scores safely
    min_score = min(current_scores_list) if current_scores_list else 0
    max_score = max(current_scores_list) if current_scores_list else 0

    if max_score == min_score or not current_scores_list: # Avoid division by zero / handle empty
        node_sizes = [15] * len(G_nodes_list)
    else:
        node_sizes = [
            min_size + (max_size - min_size) * (node_scores.get(node, 0) - min_score) / (max_score - min_score)
            for node in G_nodes_list
        ]

    node_colors = current_scores_list

    # Create hover text for nodes
    hover_texts = []
    for node in G_nodes_list:
        score = node_scores.get(node, 0)
        in_degree = G.in_degree(node, weight='weight')
        out_degree = G.out_degree(node, weight='weight')
        text = (f"<b>Node: {node}</b><br>"
                f"PageRank: {score:.5f}<br>"
                f"Weighted In-Degree: {in_degree:.2f}<br>"
                f"Weighted Out-Degree: {out_degree:.2f}")
        hover_texts.append(text)


    trace_nodes = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers',
        marker=dict(
            showscale=True,
            colorscale='Viridis', # Example colorscale
            reversescale=True,
            color=node_colors,
            size=node_sizes,
            colorbar=dict(
                thickness=15,
                title='PageRank', # Removed titleside
                xanchor='left',
                # titleside='right' # Removed as requested
            ),
            line=dict(width=0.5, color='black'), # Marker outline
            opacity=0.9
        ),
        text=hover_texts,
        hoverinfo='text', # Show only the custom text on hover
        name='Nodes'
    )

    # --- Layout Configuration ---
    layout = go.Layout(
        # Use dict for title configuration
        title=dict(
             text=f'<b>3D PageRank Visualization</b><br>Iteration: {current_iter}, Alpha (α): {alpha:.2f}, Nodes: {len(G_nodes_list)}',
             x=0.5, # Center title
             xanchor='center'
             # titlefont_size=16, # Removed as requested
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=10, l=10, r=10, t=50), # Adjust margins
        scene=dict(
            xaxis=dict(showbackground=False, showline=False, zeroline=False, showticklabels=False, title=''),
            yaxis=dict(showbackground=False, showline=False, zeroline=False, showticklabels=False, title=''),
            zaxis=dict(showbackground=False, showline=False, zeroline=False, showticklabels=False, title=''),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5) # Adjust initial viewpoint
            ),
            aspectratio=dict(x=1, y=1, z=1) # Ensure equal aspect ratio
        ),
        # annotations=[ # Add annotations if needed, e.g., for edge weights if desired later
        #     ...
        # ]
    )

    fig = go.Figure(data=[trace_edges, trace_nodes], layout=layout)
    return fig