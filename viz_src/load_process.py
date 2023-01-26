"""Load and process Rust repository network data."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx

from networkx import Graph
from typing import Optional


def set_repos_attributes(repos_df: pd.DataFrame, projection: Graph):
    """Add attributes to the Rust repos graph.

    Parameters
    ----------
    repos_df : pandas.DataFrame
        Loaded Rust network data in a DataFrame.
    projection : networkx.classes.graph.Graph
        Projection of repos_df graph.

    Returns
    -------
    None.
    """
    projection.name = "Rust repositories graph"

    # Repository user contributed to the most (in terms of the data rather
    # than the user as a whole.) Contributed is defined as partaking in
    # PR conversations.
    auth_repos: pd.Series = repos_df.groupby(
        ["author", "repository"]
    ).repository.count()
    auth_max_repo: dict[int, str] = {
        node: auth_repos[node].idxmax() for node in projection.nodes()
    }

    # Get the most active repository contributed to per user
    # In other words, the repository that is most prominent among
    # those the user contributed to total.
    # So if the user contributed to three repositories the most_active
    # attribute would be the repository that is most active among the three.
    repocount: pd.DataFrame = repos_df.repository.value_counts().reset_index()
    repocount.columns = ["repo", "count"]

    # Create a DataFrame where each author is mapped to an array of the
    # repositories they contributed to in some way.
    auth_contrib: pd.DataFrame = repos_df.groupby("author").repository.unique()
    # Pull out the most active repository per user using repocount.
    # The trick is to sort each users' repositories by the repocount index.
    # The repocount index is in descending order of top repositories.
    # So, repositories that show up more will have a lower index which allows
    # us to sort easier.
    most_active: dict[int, str] = {
        node: sorted(
            auth_contrib[node], key=lambda repo: repocount[repocount.repo == repo].index
        )[0]
        for node in projection.nodes()
    }

    # Pull out the most prominent organization per user
    # The logic is similar to the above.
    orgs: pd.DataFrame = repos_df.organizations.explode().value_counts().reset_index()
    orgs.columns = ["org", "count"]
    auth_orgs: dict[int, list[str]] = {
        node: sorted(
            repos_df.loc[repos_df.author == node, "organizations"].values[0],
            key=lambda uorg: orgs[orgs.org == uorg].index[0],
        )
        for node in projection.nodes()
    }

    # Centrality measures [possibly?]

    # Colors!
    colors_map: dict[str, str] = {
        "core": "#ff5555",
        "middle": "#8be9fd",
        "projects": "#ff79c6",
    }

    repos_type_map: dict[str, str] = {
        "amethyst/amethyst": "projects",
        "hyperium/hyper": "middle",
        "nix-rust/nix": "core",
        "rust-random/rand": "middle",
        "sfackler/rust-openssl": "core",
        "serde-rs/serde": "middle",
        "bevyengine/bevy": "projects",
        "retep998/winapi-rs": "core",
        "rayon-rs/rayon": "middle",
        "seanmonstar/reqwest": "projects",
        "crossbeam-rs/crossbeam": "middle",
        "rust-lang/regex": "core",
        "PistonDevelopers/piston": "projects",
        "rust-num/num": "middle",
        "dtolnay/syn": "core",
        "rust-lang/hashbrown": "core",
        "bitflags/bitflags": "middle",
        "BurntSushi/aho-corasick": "core",
    }

    # Finally, add the attributes from above.
    # This is a slow way to do this. Oops.
    nx.set_node_attributes(
        projection,
        {
            node: {
                "most_active_repo": most_active[node],
                "max_repo": auth_max_repo[node],
                "organizations": auth_orgs[node],
                # (Rubbing chin emoji...this looks ugly)
                "color": colors_map[repos_type_map[most_active[node]]],
                "rtype": repos_type_map[most_active[node]],
            }
            for node in projection.nodes()
        },
    )


def process_repos_data(
    path: Optional[str] = "rust_repos.json",
    top: Optional[str] = "pull_req_title",
    bottom: Optional[str] = "author",
) -> tuple[pd.DataFrame, nx.Graph]:
    """Load Rust repository data and project the result as a graph.

    Parameters
    ----------
    path : str, optional
        Path to Rust repository data. The default is "rust_repos.json".
    top : str, optional
        Nodes to project. The default is "pull_req_title".
    bottom : str, optional
        Nodes to project onto. The default is "author".

    Returns
    -------
    repos_df : pandas.DataFrame
        Loaded data as a DataFrame.
    projection : networkx.classes.graph.Graph
        Projected graph.
    """
    # Load the serialized network then convert to a graph.
    repos_df: pd.DataFrame = pd.read_json(path, convert_dates=["date_created"])
    repos_G: nx.Graph = nx.from_pandas_edgelist(repos_df, top, bottom, edge_attr=True)

    # Create a projected graph if the graph of edges (top, bottom) are
    # bipartite
    assert nx.bipartite.is_bipartite(repos_G)
    Bnodes: set[str] = set(repos_df[bottom].values)
    projection: nx.Graph = nx.bipartite.weighted_projected_graph(repos_G, Bnodes)

    # Next, I have to manually add node attributes. Attributes don't transfer
    # over from the DataFrame for some reason.
    set_repos_attributes(repos_df, projection)

    return repos_df, projection
