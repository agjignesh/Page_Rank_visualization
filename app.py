# app.py
import streamlit as st
import pandas as pd
import time # <-- Import time

# Import functions from our utility files
from graph_utils import create_random_weighted_graph, calculate_layout
from pagerank_utils import pagerank_weighted_iterative
from plot_utils import create_3d_figure

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Interactive 3D PageRank", page_icon="🕸️")

# --- Load Explanation Content ---
try:
    with open("content.md", "r") as f:
        explanation_content = f.read()
except FileNotFoundError:
    explanation_content = "*(content.md not found)*\n\nPlease refer to the comments in `app.py` or create `content.md` for a detailed explanation."

# --- Initialize Session State ---
if 'graph' not in st.session_state:
    st.session_state.graph = None
    st.session_state.pos = None
    st.session_state.pagerank_history = []
    st.session_state.current_iteration = 0
    st.session_state.params = {} # To store params used for calculation
    st.session_state.needs_recalc = True # Flag to trigger recalculation
    st.session_state.nodes_list = []
    st.session_state.edges_list = []
    st.session_state.is_animating = False # Flag to track animation state


# --- Sidebar Controls ---
st.sidebar.header("⚙️ Graph & Algorithm Controls")

# Graph Parameters
num_nodes = st.sidebar.slider("Number of Nodes", 5, 50, 15, 1, key="num_nodes_slider")
edge_prob = st.sidebar.slider("Edge Probability", 0.0, 1.0, 0.15, 0.01, key="edge_prob_slider", help="Approximate density of links.")
graph_seed = st.sidebar.number_input("Graph Random Seed", value=42, step=1, key="graph_seed_input", help="Ensures same random graph for the same seed.")

# PageRank Parameters
alpha = st.sidebar.slider("Damping Factor (α)", 0.0, 1.0, 0.85, 0.01, key="alpha_slider", help="Probability the surfer follows links.")
max_iter_calc = st.sidebar.select_slider("Max Iterations (for Calculation)", options=[10, 20, 50, 100, 200], value=100, key="max_iter_calc_slider", help="Maximum steps for calculation.")
tol = st.sidebar.select_slider("Tolerance", options=[1.0e-4, 1.0e-5, 1.0e-6, 1.0e-7, 1.0e-8], value=1.0e-6, key="tol_slider", help="Convergence threshold.")

# --- Button to Trigger Calculation / Recalculation ---
st.sidebar.markdown("---") # Separator
recalc_pressed = st.sidebar.button("🔄 Generate Graph & Calculate PageRank", key="calc_button")

# --- Check if parameters changed ---
current_params = {
    'num_nodes': num_nodes,
    'edge_prob': edge_prob,
    'graph_seed': graph_seed,
    'alpha': alpha,
    'max_iter': max_iter_calc, # Use calculation max_iter here
    'tol': tol
}

# Mark for recalculation if params changed OR if the button was explicitly pressed
# And reset animation flag if recalculating
if current_params != st.session_state.get('params', {}) or recalc_pressed:
    st.session_state.needs_recalc = True
    st.session_state.params = current_params
    st.session_state.is_animating = False # Stop animation if params change

# Perform recalculation if needed
if st.session_state.needs_recalc:
    with st.spinner("Generating graph and calculating PageRank..."):
        # 1. Create Graph
        st.session_state.graph = create_random_weighted_graph(num_nodes, edge_prob, graph_seed)
        st.session_state.nodes_list = list(st.session_state.graph.nodes())
        st.session_state.edges_list = list(st.session_state.graph.edges(data=True))

        # 2. Calculate Layout
        st.session_state.pos = calculate_layout(st.session_state.graph, seed=graph_seed) if st.session_state.graph.number_of_nodes() > 0 else {}

        # 3. Calculate PageRank History
        if st.session_state.graph.number_of_nodes() > 0:
             _, st.session_state.pagerank_history = pagerank_weighted_iterative(
                 st.session_state.graph,
                 alpha=alpha,
                 max_iter=max_iter_calc, # Use calculation max_iter
                 tol=tol,
                 weight='weight'
             )
        else:
            st.session_state.pagerank_history = [{}]

        # 4. Reset iteration and flag
        st.session_state.current_iteration = 0
        st.session_state.needs_recalc = False
        st.session_state.is_animating = False # Ensure animation stops


# --- Animation Controls (Sidebar) ---
st.sidebar.markdown("---")
st.sidebar.subheader("▶️ Animation")
animation_speed = st.sidebar.slider("Animation Speed (sec/step)", 0.1, 2.0, 0.5, 0.1, key="anim_speed_slider", help="Pause between animation frames.")
animate_pressed = st.sidebar.button("Run Animation", key="anim_button", disabled=st.session_state.needs_recalc or not st.session_state.pagerank_history)


# --- Main Area Layout ---
st.title("🕸️ Interactive 3D PageRank Explorer")

# Explanation Section (Collapsible)
with st.expander("What is PageRank? Click to learn more...", expanded=False):
    st.markdown(explanation_content)

# Check if data is ready before showing controls/plot
if st.session_state.needs_recalc or not st.session_state.pagerank_history or st.session_state.graph is None:
    st.warning("Please click '🔄 Generate Graph & Calculate PageRank' in the sidebar to start.")
    st.stop()

# --- Step-by-Step Controls & Visualization ---
max_history_index = len(st.session_state.pagerank_history) - 1

st.header("📊 Visualization & Iteration Control")
st.markdown(f"Use the controls to explore the **{max_history_index}** calculated iterations.")

# Layout for controls and plot
control_col, plot_col = st.columns([1, 3]) # Controls on left, plot on right

# --- Iteration Controls (Left Column) ---
with control_col:
    st.subheader("Step-by-Step")
    # Disable buttons if at bounds
    disable_prev = st.session_state.current_iteration <= 0
    disable_next = st.session_state.current_iteration >= max_history_index

    # Buttons trigger a rerun to update plot via standard flow
    if st.button("⏮️ Reset (Iter 0)", key="reset_button"):
        st.session_state.current_iteration = 0
        st.session_state.is_animating = False # Stop animation
        st.rerun()

    if st.button("⏪ Previous Step", disabled=disable_prev, key="prev_button"):
        st.session_state.current_iteration -= 1
        st.session_state.is_animating = False # Stop animation
        st.rerun()

    if st.button("Next Step ⏩", disabled=disable_next, key="next_button"):
        st.session_state.current_iteration += 1
        st.session_state.is_animating = False # Stop animation
        st.rerun()

    if st.button("⏭️ Go to Final", key="final_button"):
         st.session_state.current_iteration = max_history_index
         st.session_state.is_animating = False # Stop animation
         st.rerun()

    # Display current iteration number - will update on rerun or after animation
    iteration_metric_placeholder = st.empty()
    iteration_metric_placeholder.metric("Current Iteration", f"{st.session_state.current_iteration} / {max_history_index}")


    # Display Final Scores
    st.subheader("🏆 Final Scores")
    final_scores = st.session_state.pagerank_history[-1]
    if final_scores:
        final_df = pd.DataFrame(list(final_scores.items()), columns=['Node', 'PageRank'])
        final_df = final_df.sort_values(by='PageRank', ascending=False).reset_index(drop=True)
        final_df['Rank'] = final_df.index + 1
        st.dataframe(final_df[['Rank', 'Node', 'PageRank']].set_index('Rank'), height=300)
    else:
        st.write("No scores to display.")

# --- Plot Area (Right Column) ---
with plot_col:
    st.subheader("Interactive 3D Graph")
    plot_placeholder = st.empty() # <-- Placeholder for the plot

    # Animation Logic - runs ONLY when button is pressed
    if animate_pressed:
        st.session_state.is_animating = True
        # Start animation from iteration 0
        start_iter = 0
        st.session_state.current_iteration = start_iter
        for i in range(start_iter, max_history_index + 1):
             # Update session state for consistency (though metric might not visually update live)
             st.session_state.current_iteration = i

             # Get scores for the current animation step
             current_scores = st.session_state.pagerank_history[i]

             # Create and display the figure in the placeholder
             fig = create_3d_figure(
                 st.session_state.graph,
                 st.session_state.pos,
                 current_scores,
                 i, # Pass the loop iterator 'i' as current_iter
                 st.session_state.nodes_list,
                 st.session_state.edges_list,
                 alpha # Pass current alpha
             )
             plot_placeholder.plotly_chart(fig, use_container_width=True)

             # Update the iteration metric display placeholder directly
             iteration_metric_placeholder.metric("Current Iteration", f"{i} / {max_history_index} (Animating...)")

             # Pause for animation effect
             time.sleep(animation_speed)
        st.session_state.is_animating = False
        # Update metric one last time after animation finishes
        iteration_metric_placeholder.metric("Current Iteration", f"{st.session_state.current_iteration} / {max_history_index}")


    # Standard Plot Display (when not animating or after animation finishes)
    # This ensures the plot reflects the current state if animation is not running
    elif not st.session_state.is_animating:
        if 0 <= st.session_state.current_iteration < len(st.session_state.pagerank_history):
            current_scores = st.session_state.pagerank_history[st.session_state.current_iteration]
            fig = create_3d_figure(
                st.session_state.graph,
                st.session_state.pos,
                current_scores,
                st.session_state.current_iteration,
                st.session_state.nodes_list,
                st.session_state.edges_list,
                alpha
            )
            plot_placeholder.plotly_chart(fig, use_container_width=True)
        else:
            # This case might occur briefly if history is cleared before redraw
            plot_placeholder.warning("Graph data not available or iteration index out of bounds.")


# --- Footer ---
st.markdown("---")
st.caption("Built with Streamlit, NetworkX, and Plotly.")