"""Not actually main. Just convenience functions."""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
from networkx import Graph
from matplotlib.figure import Figure
from matplotlib.axes import Axes, Subplot
from np.typing import NDArray
from typing import Iterable

from joshnettools.gamersdraw import (
    draw_degree_centrality,
    add_network_leg,
    draw_lollypop,
    draw_diameter_radius,
)
from joshnettools.randomnet import (
    random_clust,
    random_density,
    random_deg_cent,
    random_deg_assort,
    random_assort,
    dispatcher,
)
from joshnettools.pvalueplots import p_value_plots
from joshnettools.main import print_useful_metrics, largest_connected_component


def draw_dc(
    rust_proj: Graph, suptitle: str = "Size = degree centrality"
) -> tuple[Figure, Axes]:
    """Plot the rust_proj network with a degree centrality chart.

    Parameters
    ----------
    rust_proj: networkx.classes.graph.Graph
        Rust pull request conversations network.
    suptitle: str, optional
        Title. The default is "Size = degree centrality".

    Returns
    -------
    fig: matplotlib.figure.Figure
        Plot's Figure.
    ax: matplotlib.axes.Axes
        Axes associated with plot.
    """
    fig: Figure
    ax: Axes
    (fig, ax, _) = draw_degree_centrality(
        rust_proj, color="color", edge_color="#44475a", alpha=0.6
    )

    # Add legend and title using awesome convenience function.
    add_network_leg(
        fig,
        ax,
        suptitle=suptitle,
        col_labels=[
            ("#ff5555", "Core"),
            ("#8be9fd", "Middleware libraries"),
            ("#ff79c6", "Projects"),
        ],
    )

    # Add degree centrality information to the plot.
    # I'm technically calculating degree centrality twice since I calculated
    # it in the initial plotting function. I handled this a bit poorly too.
    # ----------------------
    # Sort the centralities and slice for the top ten highest
    dc: list[dict[int, float]] = sorted(
        nx.degree_centrality(rust_proj).items(), key=lambda cent: cent[1], reverse=True
    )[:10]
    # Construct strings of node: deg cent; concatanate into a single string
    dc_map: Iterable[str] = map(
        lambda cent: "{}: {}".format(cent[0], round(cent[1], 5)), dc
    )
    dc_str: str = "\n".join(dc_map)
    dc_text: str = "Highest degree centralities\n" + ("-" * 32) + "\n" + dc_str
    # Numbers were guess and check and would likely break if figsize is
    # changed.
    ax.annotate(
        dc_text,
        (18, 1250),
        xycoords="figure points",
        fontsize=14,
        color="#f8f8f2",
        fontweight="bold",
    )

    fig.tight_layout()
    return fig, ax


def draw_everything(
    rust_proj: nx.Graph, rust_df: pd.DataFrame, path: str = "../assets/"
):
    """Draws several plots that I shall use for my data science class.

    Parameters
    ----------
    rust_proj : networkx.classes.graph.Graph
        Graph projection of Rust repository data.
    rust_df : pandas.DataFrame
        DataFrame used to create rust_proj.
    path : str, optional
        Location to save plots. The default is "../assets/".

    Returns
    -------
    None.

    """
    # Note that I'll purposely overwrite fig, ax in each of the plots with
    # the subsequent plots in order to give the garbage collector a hint
    # of what to reclaim.

    # Degree centrality plot
    print("Drawing degree centrality plot.")

    fig: plt.Figure
    ax: plt.Axes
    fig, ax = draw_dc(rust_proj, "Rust pull req convos network with degree centrality")
    fig.savefig(path + "network_full_degcent.png", bbox_inches="tight")

    # Ego graph
    print("Drawing example ego graph.")
    # BurntSushi is awesome and ALSO makes a great ego graph for my data.
    burntego: nx.Graph = nx.ego_graph(rust_proj, "BurntSushi")
    fig, ax = draw_dc(burntego, "BurntSushi ego graph of pull req convos")
    fig.savefig(path + "network_ego_degcent.png", bbox_inches="tight")

    # Random graph replicates histograms
    print("Calculating average clustering replicates.")
    N_reps: int = 10000
    processes: int = 7

    clust_obs: np.floating = nx.average_clustering(rust_proj, weight="weight")
    clust_reps: NDArray[np.floating] = dispatcher(
        rust_df,
        random_clust,
        "pull_req_title",
        "author",
        replicates=N_reps,
        processes=processes,
    )

    print("Calculating network density replicates.")
    dens_obs: np.floating = nx.density(rust_proj)
    dens_reps: NDArray[np.floating] = dispatcher(
        rust_df,
        random_density,
        "pull_req_title",
        "author",
        replicates=N_reps,
        processes=processes,
    )

    print("Calculating random degree assortativity replicates.")
    deg_obs: np.floating = nx.degree_pearson_correlation_coefficient(
        rust_proj, weight="weight"
    )
    deg_reps: NDArray[np.floating] = dispatcher(
        rust_df,
        random_deg_assort,
        "pull_req_title",
        "author",
        replicates=N_reps,
        processes=processes,
    )

    print("Calculating random assortativity replicates.")
    assort_obs: np.floating = nx.attribute_assortativity_coefficient(
        rust_proj, "most_active_repo"
    )
    assort_reps: NDArray[np.floating] = dispatcher(
        rust_df,
        random_assort,
        "pull_req_title",
        "author",
        replicates=N_reps,
        processes=processes,
        assort="repository",
    )

    p_val_titles: list[str] = [
        "Average clustering",
        "Density",
        "Degree assortativity",
        "Assortativity on most active repository",
    ]
    print("Drawing p-values plots (without p-values though)")
    fig, ax = p_value_plots(
        [clust_obs, dens_obs, deg_obs, assort_obs],
        [clust_reps, dens_reps, deg_reps, assort_reps],
        p_val_titles,
        False,
        False,
    )
    # Suptitle breaks for some reason if bbox_inches isn't set to tight.
    # Also, I have no idea why it works above.
    fig.savefig(path + "metrics_dist.png", bbox_inches="tight")

    fig, ax = p_value_plots(
        [clust_obs, dens_obs, deg_obs, assort_obs],
        [clust_reps, dens_reps, deg_reps, assort_reps],
        p_val_titles,
        plot_p=False,
        suptitle="Random graph replicates of selected "
        + "measures with observed stats",
    )
    fig.savefig(path + "metrics_dist_w_obs.png", bbox_inches="tight")

    # Diameter Radius
    print("Drawing diameter and radius.")
    fig, ax = draw_diameter_radius(
        largest_connected_component(rust_proj), edge_color="#44475a", barycenter=False
    )
    add_network_leg(
        fig,
        ax,
        suptitle="Diameter/radius of Rust PR network",
        col_labels=[
            ("#ff5555", "Radius"),
            ("#f1fa8c", "Diameter"),
            ("#8be9fd", "Neither"),
        ],
    )
    fig.savefig(path + "network_diarad.png", bbox_inches="tight")

    # Lollypop plot
    print("Drawing lollypop plot of counts.")
    fig, ax = draw_lollypop(
        rust_df.repository.value_counts(), "Count of scraped Rust repository PR convos"
    )
    fig.savefig(path + "lollypopcounts.png", bbox_inches="tight")


def rust_print_useful(rust_proj: nx.Graph):
    """Print useful metrics for the Rust repo graph projection.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    print_useful_metrics(rust_proj, ["most_active_repo", "max_repo", "rtype"])
