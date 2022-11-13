import pandas as pd
import seaborn as sns

# I finished this early, didn't save, and lost it. :( My IDEs never crash. :(

covid: pd.DataFrame = pd.read_csv(
    "https://raw.githubusercontent.com/RamiKrispin/coronavirus/master/csv/coronavirus.csv",
    parse_dates=["date"],
)

# Cheating here. Large figure sizes look kind of weird and distorted, but
# the text overlaps for the U.K. and South Africa for smaller plots.
# So, I'll rename them to save space without really losing information.
# Horizontal box plots also work here.
covid.country.replace(
    {"United Kingdom": "U.K.", "South Africa": "S. Africa"}, inplace=True
)

# Filtering for data we're interesting in plotting
covid = covid.loc[
    (covid.type == "confirmed")
    & (
        covid.country.isin(
            [
                "U.K",
                "Argentina",
                "Italy",
                "Colombia",
                "Mexico",
                "Peru",
                "Germany",
                "Iran",
                "Poland",
                "S. Africa",
            ]
        )
    ),
    ["date", "country", "cases"],
]

# Plot and customization
covid_plot: sns.FacetGrid = sns.catplot(
    x="country", y="cases", data=covid, kind="box", height=8
)

# I'm calling date() after getting the min/max date because
# datetime64.to_string() returns a string with the time included.
# And the time, of course, is just 0.
title: str = "Confirmed COVID19 cases ({} -> {})".format(
    covid.date.min().date(), covid.date.max().date()
)

# Labels.
covid_plot.ax.set_title(title, {"fontweight": "bold", "fontsize": 16})
covid_plot.ax.set_xlabel("Country", {"fontweight": "bold"})
covid_plot.ax.set_ylabel("Confirmed cases", {"fontweight": "bold"})
