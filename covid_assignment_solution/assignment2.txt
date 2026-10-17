"""COVID-19 state simulation for ET1556 Assignment 2."""
from pathlib import Path
import random
import pandas as pd

from sim_parameters import TRANSITION_PROBS, HOLDING_TIMES
from helper import create_plot

AGE_GROUPS = ["less_5", "5_to_14", "15_to_24", "25_to_64", "over_65"]
STATES = ["H", "I", "S", "M", "D"]
SIMULATED_FILE = "a2-covid-simulated-timeseries.csv"
SUMMARY_FILE = "a2-covid-summary-timeseries.csv"
PLOT_FILE = "a2-covid-simulation.png"


def _choose_next_state(country_age_group, current_state):
    """Sample the next state using the configured transition probabilities."""
    probabilities = TRANSITION_PROBS[country_age_group][current_state]
    states = list(probabilities.keys())
    weights = list(probabilities.values())
    return random.choices(states, weights=weights, k=1)[0]


def _age_group_sample_counts(country_row, sample_ratio):
    """Return rounded sample counts for each age group in a country."""
    total_samples = int(round(float(country_row["population"]) / sample_ratio))
    counts = {}
    for group in AGE_GROUPS:
        percentage = float(country_row[group])
        counts[group] = max(0, int(round(total_samples * percentage / 100.0)))
    return counts


def _simulate_person(person_id, country, age_group, dates):
    """Simulate one person's state for every date in the requested period."""
    rows = []
    state = "H"
    previous_state = "H"
    staying_days = 0

    for date in dates:
        rows.append({
            "person_id": person_id,
            "age_group_name": age_group,
            "country": country,
            "date": date.strftime("%Y-%m-%d"),
            "state": state,
            "staying_days": staying_days,
            "prev_state": previous_state,
        })

        holding_time = int(HOLDING_TIMES[age_group][state])
        # A holding time of zero means one day, as specified in the brief.
        required_days = max(holding_time, 1)
        if staying_days + 1 >= required_days:
            next_state = _choose_next_state(age_group, state)
            previous_state = state
            state = next_state
            # A self-transition begins a new holding period as well.
            staying_days = 0
        else:
            staying_days += 1

    return rows


def run(countries_csv_name, countries, sample_ratio, start_date, end_date):
    """Run the simulation and create both CSV outputs and the chart."""
    if sample_ratio <= 0:
        raise ValueError("sample_ratio must be greater than zero")
    if not countries:
        raise ValueError("Select at least one country")

    base_dir = Path(__file__).resolve().parent
    countries_path = base_dir / countries_csv_name
    if not countries_path.exists():
        raise FileNotFoundError(f"Could not find country dataset: {countries_path}")

    country_df = pd.read_csv(countries_path)
    required_columns = {"country", "population", *AGE_GROUPS}
    missing = required_columns.difference(country_df.columns)
    if missing:
        raise ValueError(f"Country dataset is missing columns: {sorted(missing)}")

    dates = pd.date_range(start=pd.to_datetime(start_date), end=pd.to_datetime(end_date), freq="D")
    if len(dates) == 0:
        raise ValueError("start_date must be on or before end_date")

    all_rows = []
    person_id = 0
    selected_country_rows = []
    for country in countries:
        matches = country_df[country_df["country"] == country]
        if matches.empty:
            raise ValueError(f"Country not found in dataset: {country}")
        country_row = matches.iloc[0]
        selected_country_rows.append(country)
        counts = _age_group_sample_counts(country_row, float(sample_ratio))

        for age_group in AGE_GROUPS:
            for _ in range(counts[age_group]):
                all_rows.extend(_simulate_person(person_id, country, age_group, dates))
                person_id += 1

    simulated_columns = [
        "person_id", "age_group_name", "country", "date",
        "state", "staying_days", "prev_state"
    ]
    simulated_df = pd.DataFrame(all_rows, columns=simulated_columns)
    simulated_df.to_csv(base_dir / SIMULATED_FILE, index=False)

    if simulated_df.empty:
        summary_df = pd.DataFrame(columns=["date", "country", "D", "H", "I", "M", "S"])
    else:
        counts_df = (
            simulated_df.groupby(["date", "country", "state"])
            .size()
            .unstack(fill_value=0)
        )
        for state_name in STATES:
            if state_name not in counts_df.columns:
                counts_df[state_name] = 0
        summary_df = counts_df[STATES].reset_index()
        summary_df = summary_df[["date", "country", "D", "H", "I", "M", "S"]]
        summary_df = summary_df.sort_values(["date", "country"]).reset_index(drop=True)

    summary_df.to_csv(base_dir / SUMMARY_FILE, index=False)
    create_plot(SUMMARY_FILE, selected_country_rows)
    return summary_df


if __name__ == "__main__":
    run(
        countries_csv_name="a2-countries.csv",
        countries=["Afghanistan", "Sweden", "Japan"],
        sample_ratio=1e6,
        start_date="2021-04-01",
        end_date="2022-04-30",
    )
