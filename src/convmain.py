"""Not actually main. Just convenience functions.
"""
from matplotlib.patches import Patch

from joshnettools.gamersdraw import draw_degree_centrality

def draw_everything(rust_proj, path="../assets/"):
    print("Drawing degree centrality plot.")
    fig, ax, dc = draw_degree_centrality(rust_proj, color="color",
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

    # Misc options and setting the legend
    ax.set_frameon(False)
    ax.set_title("Size = degree centrality",
                 fontdict={"fontsize": 24,
                           "color": "#f8f8f2",
                           "fontweight": "bold"})
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

    fig.save_fig(path + "deg_cent.tiff")