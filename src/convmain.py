"""Not actually main. Just convenience functions.
"""
import networkx as nx
from matplotlib.patches import Patch

from joshnettools.gamersdraw import draw_degree_centrality, add_network_leg
from joshnettools.randomnet import random_clust, random_density,\
    random_deg_cent, random_deg_assort, random_assort, dispatcher
from joshnettools.pvalueplots import p_value_plots


def draw_dc(rust_proj, suptitle="Size = degree centrality"):
    (fig, ax, _) = draw_degree_centrality(rust_proj, color="color",
                                          edge_color="#44475a", alpha=0.6)

    # Manually creating a legend
    # Create patches based on the attribute colors. I'm writing these out
    # manually so I don't spend an hour trying to play with sets to pull
    # them out from my network object.
    core_hand = Patch(color="#ff5555")
    core_hand.set_label("Core")
    mid_hand = Patch(color="#8be9fd")
    mid_hand.set_label("Middleware libraries")
    projects_hand = Patch(color="#ff79c6")
    projects_hand.set_label("Projects")

    # Misc options, labels, and setting the legend
    ax.legend(handles=[core_hand, mid_hand, projects_hand],
              loc="upper left",
              fontsize=14,
              facecolor="#282a36",
              edgecolor="#44475a",
              frameon=False)

    # As far as I know I can't set the text color without doing this.
    legend = ax.get_legend()
    for lab in legend.get_texts():
        lab.set_color("#f8f8f2")

    # Add degree centrality information to the plot.
    # I'm technically calculating degree centrality twice since I calculated
    # it in the initial plotting function. I handled this a bit poorly too.
    dc = sorted(nx.degree_centrality(rust_proj).items(),
                key=lambda cent: cent[1], reverse=True)[:10]
    dc = map(lambda cent: "{}: {}".format(cent[0], round(cent[1], 5)), dc)
    dc = "\n".join(dc)
    dc_text = "Highest degree centralities\n" + ("-"*32) + "\n" + dc
    # Numbers were guess and check and would likely break if figsize is
    # changed.
    ax.annotate(dc_text,
                (18, 1120),
                xycoords="figure points",
                fontsize=14,
                color="#f8f8f2",
                fontweight="bold")

    ax.set_frame_on(False)
    fig.suptitle(suptitle,
                 fontsize=24,
                 color="#f8f8f2",
                 fontweight="bold")
    fig.tight_layout()
    return fig, ax


def draw_everything(rust_proj, rust_df, path="../assets/"):
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

    print("Drawing degree centrality plot.")
    fig, ax = draw_dc(rust_proj)
    fig.savefig(path + "network_full_degcent.tiff")

    print("Drawing example ego graph.")
    # BurntSushi is awesome and ALSO makes a great ego graph for my data.
    burntego = nx.ego_graph(rust_proj, "BurntSushi")
    fig, ax = draw_dc(burntego, "BurntSushi ego graph + deg cent as size")
    fig.savefig(path + "network_ego_degcent.tiff")

    print("Calculating average clustering replicates.")
    N_reps = 10000
    clust_obs = nx.average_clustering(rust_proj, weight="weight")
    clust_reps = dispatcher(rust_df, random_clust, "pull_req_title",
                            "author", replicates=N_reps)

    print("Calculating network density replicates.")
    dens_obs = nx.density(rust_proj)
    dens_reps = dispatcher(rust_df, random_density, "pull_req_title",
                           "author", replicates=N_reps)

    print("Calculating random degree assortativity replicates.")
    deg_obs = nx.degree_pearson_correlation_coefficient(rust_proj,
                                                        weight="weight")
    deg_reps = dispatcher(rust_df, random_deg_assort, "pull_req_title",
                          "author", replicates=N_reps)

    print("Calculating random assortativity replicates.")
    assort_obs = nx.attribute_assortativity_coefficient(rust_proj,
                                                        "most_active_repo")
    assort_reps = dispatcher(rust_df, random_assort, "pull_req_title",
                             "author", replicates=N_reps,
                             assort="repository")

    print("Drawing p-values plots (without p-values though)")
    fig, ax = p_value_plots([clust_obs, dens_obs, deg_obs, assort_obs],
                            [clust_reps, dens_reps, deg_reps, assort_reps],
                            ["Average clustering",
                             "Density",
                             "Degree assortativity",
                             "Assortativity on most active repository"],
                            False,
                            False)
    # Suptitle breaks for some reason if bbox_inches isn't set to tight.
    # Also, I have no idea why it works above.
    fig.savefig(path + "metrics_dist.tiff", bbox_inches="tight")

    fig, ax = p_value_plots([clust_obs, dens_obs, deg_obs, assort_obs],
                            [clust_reps, dens_reps, deg_reps, assort_reps],
                            ["Average clustering",
                             "Density",
                             "Degree assortativity",
                             "Assortativity on most active repository"],
                            plot_p=False)
    fig.savefig(path + "metrics_dist_w_obs.tiff", bbox_inches="tight")

    print("Drawing lollypop plot of counts.")
    fig, ax = draw_lollypop(rust_df.repository.value_counts(),
                            "Frequency of scraped GitHub repositories")
    fig.savefig(path + "lollypopcounts.tiff", bbox_inches="tight")
