"""Plot the country-level COVID-19 simulation summary."""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

OUTPUT_NAME = "a2-covid-simulation.png"
STATE_LABELS = {
    "H": "Healthy",
    "I": "Infected (without symptoms)",
    "S": "Infected (with symptoms)",
    "M": "Immune",
    "D": "Deceased",
}
STATE_COLORS = {
    "H": "#2E8B57",
    "I": "#E69F00",
    "S": "#D55E5E",
    "M": "#36A6A0",
    "D": "#64748B",
}


def get_filepath(filename: str | Path) -> Path:
    """Resolve a filename relative to this project's directory."""
    path = Path(filename)
    return path if path.is_absolute() else Path(__file__).resolve().parent / path


def save_plot(fig, filename: str = OUTPUT_NAME) -> Path:
    """Save a figure at high resolution and return the output path."""
    filepath = get_filepath(filename)
    fig.savefig(filepath, dpi=220, bbox_inches="tight", facecolor="white")
    return filepath


def read_dataset(filename: str | Path) -> pd.DataFrame:
    """Read a CSV file located in the project directory."""
    filepath = get_filepath(filename)
    if not filepath.is_file():
        raise FileNotFoundError(f"Could not find summary CSV: {filepath}")
    return pd.read_csv(filepath)


def create_plot(summary_csv: str, countries: list[str]) -> None:
    """Create a readable stacked-area chart for each selected country.

    The public function name and output filename are kept compatible with
    the assignment. Values represent simulated sample counts, not national
    population totals.
    """
    summary_df = read_dataset(summary_csv)
    required_columns = {"country", "date", "H", "I", "S", "M", "D"}
    missing = required_columns.difference(summary_df.columns)
    if missing:
        raise ValueError(f"Summary CSV is missing columns: {sorted(missing)}")

    if not countries:
        raise ValueError("At least one country is required to create a plot")

    if summary_df.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.text(0.5, 0.5, "No simulation records to plot", ha="center", va="center")
        ax.set_axis_off()
        save_plot(fig)
        plt.close(fig)
        return

    summary_df = summary_df.copy()
    summary_df["date"] = pd.to_datetime(summary_df["date"], errors="raise")
    available_countries = set(summary_df["country"].dropna().unique())
    plotted_countries = [country for country in countries if country in available_countries]

    if not plotted_countries:
        raise ValueError("None of the selected countries are present in the summary CSV")

    state_order = ("H", "I", "S", "M", "D")
    figure_height = max(4.2, 3.5 * len(plotted_countries))
    fig, axes = plt.subplots(
        nrows=len(plotted_countries),
        ncols=1,
        figsize=(12, figure_height),
        sharex=True,
        squeeze=False,
        constrained_layout=True,
    )

    for ax, country in zip(axes[:, 0], plotted_countries):
        country_df = (
            summary_df[summary_df["country"] == country]
            .sort_values("date")
            .drop_duplicates(subset=["date"])
        )
        dates = country_df["date"]
        values = [country_df[state].fillna(0).to_numpy() for state in state_order]
        labels = [STATE_LABELS[state] for state in state_order]
        colors = [STATE_COLORS[state] for state in state_order]

        ax.stackplot(dates, *values, labels=labels, colors=colors, alpha=0.9, linewidth=0)
        ax.set_title(country, loc="left", fontsize=12, fontweight="bold", pad=8)
        ax.set_ylabel("Simulated people")
        ax.grid(axis="y", alpha=0.22, linestyle="--")
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.margins(x=0)

    axes[-1, 0].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    axes[-1, 0].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    axes[-1, 0].set_xlabel("Date")
    plt.setp(axes[-1, 0].get_xticklabels(), rotation=30, ha="right")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=len(state_order),
        frameon=False,
        bbox_to_anchor=(0.5, 1.02),
    )
    fig.suptitle("COVID-19 Simulation: Daily State Distribution", fontsize=15, fontweight="bold")
    save_plot(fig)
    plt.close(fig)
