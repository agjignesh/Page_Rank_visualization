# How to run

clone the repositry
In the terminal write: streamlit run app.py

# Understanding the PageRank Algorithm

PageRank is a foundational algorithm, famously used by Google Search, to rank the importance of web pages based on the structure of the web's links. It models a "random surfer" navigating the web.

**The Core Idea:**

A page is considered important if:
1.  **Many pages link to it.** (Popularity)
2.  **Important pages link to it.** (Endorsement from authority)

**The Random Surfer Model:**

Imagine a user randomly clicking links on web pages.
*   They start on a random page.
*   At each step, they have two choices:
    *   **Follow a link:** With probability **α (alpha, the damping factor)**, they randomly choose one of the outgoing links from the current page and follow it.
    *   **Teleport:** With probability **(1 - α)**, they get bored or stuck and jump to *any* page on the web completely at random (usually modeled as a uniform probability distribution across all pages).

The PageRank score of a page represents the long-term probability that this random surfer will end up on that particular page after many clicks.

**Weighted Graphs:**

In this visualization, the links (edges) have **weights**. This modifies the surfer's behavior when *following links*:
*   Instead of choosing any outgoing link with equal probability, the surfer is *more likely* to follow links with higher weights.
*   The probability of moving from page A to page B (if a link exists) is calculated as:
    `Prob(A -> B) = Weight(A, B) / Total Weight of all outgoing links from A`

**The Algorithm (Power Iteration):**

PageRank scores are typically calculated iteratively:

1.  **Initialization:** Assign an initial PageRank score to all pages (e.g., `1 / Total Number of Pages`).
2.  **Iteration:** Repeat the following calculation for each page until the scores stabilize (converge):
    *   `NewScore(Page P) = (1 - α) / N + α * Σ [ Score(Page Q) / OutLinks(Q) ]`
    *   Where:
        *   `N` is the total number of pages.
        *   The summation `Σ` is over all pages `Q` that link *to* page `P`.
        *   `OutLinks(Q)` is the number of outgoing links from page `Q`.
    *   **Weighted Modification:** In our case, `Score(Page Q) / OutLinks(Q)` is replaced by the sum of `Score(Page Q) * (Weight(Q, P) / Total Outgoing Weight(Q))` for all Q linking to P.
3.  **Handling Dangling Nodes:** Pages with no outgoing links ("dangling nodes") pose a problem because the surfer gets stuck. Their PageRank score is typically redistributed among all pages according to the teleportation probability or a specific dangling node distribution.
4.  **Convergence:** The iteration stops when the scores change very little between consecutive steps (below a defined `tolerance`).

**Parameters You Can Control:**

*   **Number of Nodes:** Changes the size of the randomly generated web graph.
*   **Damping Factor (α):** Controls the balance between following links (high α) and random teleportation (low α). A typical value is 0.85. Lower α leads to more uniform scores, higher α gives more influence to link structure.
*   **Max Iterations:** The maximum number of calculation steps allowed. Prevents infinite loops if convergence is slow or fails.
*   **Tolerance:** How small the change in scores must be to consider the algorithm converged. Smaller tolerance means higher precision but potentially more iterations.

**This Visualization:**

Use the controls to generate a graph, then step through the iterations. Observe how the node sizes and colors (representing PageRank scores) change until they settle into the final ranking. Hover over nodes to see their exact scores and connectivity.
