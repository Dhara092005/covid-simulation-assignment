"""COVID-19 state simulation for ET1556 Assignment 2.

The simulation follows the transition probabilities and holding times in
``sim_parameters.py``. It writes the assignment-required individual and
summary CSV files and asks ``helper.create_plot`` to create the chart.

This is a simplified educational model, not a medical or epidemiological
forecast.
"""

from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Any

import pandas as pd

from helper import create_plot
from sim_parameters import HOLDING_TIMES, TRANSITION_PROBS

AGE_GROUPS = ("less_5", "5_to_14", "15_to_24", "25_to_64", "over_65")
STATES = ("H", "I", "S", "M", "D")
SUMMARY_STATE_ORDER = ("D", "H", "I", "M", "S")
SIMULATED_FILE = "a2-covid-simulated-timeseries.csv"
SUMMARY_FILE = "a2-covid-summary-timeseries.csv"
PLOT_FILE = "a2-covid-simulation.png"
SIMULATED_COLUMNS = (
    "person_id",
    "age_group_name",
    "country",
    "date",
    "state",
    "staying_days",
    "prev_state",
)
SUMMARY_COLUMNS = ("date", "country", *SUMMARY_STATE_ORDER)


def _choose_next_state(country_age_group: str, current_state: str) -> str:
    """Choose one next state using the configured probability weights."""
    probabilities = TRANSITION_PROBS[country_age_group][current_state]
    possible_states = list(probabilities.keys())
    weights = list(probabilities.values())
    return random.choices(possible_states, weights=weights, k=1)[0]


def _age_group_sample_counts(country_row: pd.Series, sample_ratio: float) -> dict[str, int]:
    """Calculate rounded sample counts for each age group in a country."""
    total_samples = int(round(float(country_row["population"]) / sample_ratio))
    counts: dict[str, int] = {}

    for group in AGE_GROUPS:
        percentage = float(country_row[group])
        counts[group] = max(0, int(round(total_samples * percentage / 100.0)))

    return counts


def _simulate_person(
    person_id: int,
    country: str,
    age_group: str,
    dates: pd.DatetimeIndex,
) -> list[dict[str, Any]]:
    """Simulate one person's state timeline for the supplied dates.

    The state is recorded before the transition decision for the next day,
    matching the assignment's daily time-series convention. A holding time
    of zero is treated as one day, and a self-transition resets the holding
    period, as required by the assignment.
    """
    rows: list[dict[str, Any]] = []
    state = "H"
    previous_state = "H"
    staying_days = 0

    for date in dates:
        rows.append(
            {
                "person_id": person_id,
                "age_group_name": age_group,
                "country": country,
                "date": date.strftime("%Y-%m-%d"),
                "state": state,
                "staying_days": staying_days,
                "prev_state": previous_state,
            }
        )

        holding_time = int(HOLDING_TIMES[age_group][state])
        required_days = max(holding_time, 1)

        if staying_days + 1 >= required_days:
            previous_state = state
            state = _choose_next_state(age_group, state)
            staying_days = 0
        else:
            staying_days += 1

    return rows


def _validate_inputs(
    countries: list[str] | tuple[str, ...],
    sample_ratio: float,
    start_date: str,
    end_date: str,
) -> tuple[float, pd.DatetimeIndex]:
    """Validate run arguments and return a numeric ratio and daily dates."""
    try:
        numeric_ratio = float(sample_ratio)
    except (TypeError, ValueError) as exc:
        raise ValueError("sample_ratio must be a positive number") from exc

    if not math.isfinite(numeric_ratio) or numeric_ratio <= 0:
        raise ValueError("sample_ratio must be a positive finite number")
    if isinstance(countries, str) or not countries:
        raise ValueError("Select at least one country using a list of country names")

    try:
        start = pd.to_datetime(start_date, errors="raise")
        end = pd.to_datetime(end_date, errors="raise")
    except (TypeError, ValueError) as exc:
        raise ValueError("start_date and end_date must be valid dates") from exc

    if start > end:
        raise ValueError("start_date must be on or before end_date")

    dates = pd.date_range(start=start, end=end, freq="D")
    return numeric_ratio, dates


def run(countries_csv_name, countries, sample_ratio, start_date, end_date):
    """Run the simulation and create both CSV outputs and the chart.

    Parameters match the assignment interface. The output files are saved
    beside this module using the required assignment filenames.
    """
    sample_ratio, dates = _validate_inputs(
        countries=countries,
        sample_ratio=sample_ratio,
        start_date=start_date,
        end_date=end_date,
    )

    base_dir = Path(__file__).resolve().parent
    countries_path = base_dir / countries_csv_name
    if not countries_path.is_file():
        raise FileNotFoundError(f"Could not find country dataset: {countries_path}")

    country_df = pd.read_csv(countries_path)
    required_columns = {"country", "population", *AGE_GROUPS}
    missing = required_columns.difference(country_df.columns)
    if missing:
        raise ValueError(f"Country dataset is missing columns: {sorted(missing)}")

    for column in ("population", *AGE_GROUPS):
        country_df[column] = pd.to_numeric(country_df[column], errors="coerce")
    if country_df["population"].isna().any() or (country_df["population"] < 0).any():
        raise ValueError("Country dataset contains an invalid population value")
    for group in AGE_GROUPS:
        values = country_df[group]
        if values.isna().any() or (values < 0).any():
            raise ValueError(f"Country dataset contains invalid percentages in '{group}'")

    all_rows: list[dict[str, Any]] = []
    person_id = 0
    selected_countries: list[str] = []

    for country in countries:
        matches = country_df[country_df["country"] == country]
        if matches.empty:
            raise ValueError(f"Country not found in dataset: {country}")

        country_row = matches.iloc[0]
        selected_countries.append(country)
        counts = _age_group_sample_counts(country_row, sample_ratio)

        for age_group in AGE_GROUPS:
            for _ in range(counts[age_group]):
                all_rows.extend(_simulate_person(person_id, country, age_group, dates))
                person_id += 1

    simulated_df = pd.DataFrame(all_rows, columns=SIMULATED_COLUMNS)
    simulated_df.to_csv(base_dir / SIMULATED_FILE, index=False)

    if simulated_df.empty:
        summary_df = pd.DataFrame(columns=SUMMARY_COLUMNS)
    else:
        counts_df = (
            simulated_df.groupby(["date", "country", "state"])
            .size()
            .unstack(fill_value=0)
        )
        for state_name in STATES:
            if state_name not in counts_df.columns:
                counts_df[state_name] = 0

        summary_df = counts_df[list(SUMMARY_STATE_ORDER)].reset_index()
        summary_df = summary_df[list(SUMMARY_COLUMNS)]
        summary_df = summary_df.sort_values(["date", "country"]).reset_index(drop=True)

    summary_df.to_csv(base_dir / SUMMARY_FILE, index=False)
    create_plot(SUMMARY_FILE, selected_countries)
    return summary_df


if __name__ == "__main__":
    run(
        countries_csv_name="a2-countries.csv",
        countries=["Afghanistan", "Sweden", "Japan"],
        sample_ratio=1e6,
        start_date="2021-04-01",
        end_date="2022-04-30",
    )
