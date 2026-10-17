import os
from datetime import date

import pandas as pd
import streamlit as st

from assignment2 import run as run_simulation


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="COVID-19 Simulation Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

COUNTRIES_FILE = "a2-countries.csv"
SUMMARY_FILE = "a2-covid-summary-timeseries.csv"
TIMESERIES_FILE = "a2-covid-simulated-timeseries.csv"
PLOT_FILE = "a2-covid-simulation.png"

DEFAULT_START = date(2020, 1, 1)
DEFAULT_END = date(2020, 3, 31)
DEFAULT_RATIO = 100_000


# --------------------------------------------------
# Custom styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fb;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    .dashboard-header {
        padding: 1.5rem 1.7rem;
        background: linear-gradient(120deg, #142b4a, #2367a8);
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
    }

    .dashboard-header h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }

    .dashboard-header p {
        color: #e4efff;
        margin: 0.5rem 0 0 0;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5eaf2;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(20, 43, 74, 0.04);
    }

    div.stButton > button {
        border-radius: 9px;
        font-weight: 600;
    }

    .section-note {
        color: #64748b;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Session state
# --------------------------------------------------
defaults = {
    "sample_ratio": DEFAULT_RATIO,
    "simulation_results": None,
    "result_countries": [],
    "result_start": None,
    "result_end": None,
    "result_ratio": None,
    "simulation_error": None,
    "simulation_complete": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# Load available countries
# --------------------------------------------------
@st.cache_data
def load_countries(filename):
    if not os.path.exists(filename):
        return []

    countries_df = pd.read_csv(filename)

    if "country" not in countries_df.columns:
        return []

    return sorted(
        countries_df["country"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )


available_countries = load_countries(COUNTRIES_FILE)


# --------------------------------------------------
# Data loading helpers
# --------------------------------------------------
def load_summary_data():
    if not os.path.exists(SUMMARY_FILE):
        return pd.DataFrame()

    try:
        df = pd.read_csv(SUMMARY_FILE)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        return df

    except Exception as exc:
        st.warning(f"Could not read the summary CSV: {exc}")
        return pd.DataFrame()


def load_individual_data():
    if not os.path.exists(TIMESERIES_FILE):
        return pd.DataFrame()

    try:
        return pd.read_csv(TIMESERIES_FILE)
    except Exception:
        return pd.DataFrame()


def format_number(value):
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return "—"


# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    """
    <div class="dashboard-header">
        <h1>🦠 COVID-19 Simulation Dashboard</h1>
        <p>
            Simulate disease progression, explore country-level trends,
            and analyze the results over a selected date range.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Sidebar controls
# --------------------------------------------------
st.sidebar.title("⚙️ Simulation Settings")
st.sidebar.caption("Configure your simulation below.")

st.sidebar.subheader("🌍 Countries")

if available_countries:
    selected_countries = st.sidebar.multiselect(
        "Select countries",
        options=available_countries,
        default=available_countries[:1],
        key="simulation_countries",
        help="Choose one or more countries to simulate.",
    )
else:
    selected_countries = []
    st.sidebar.error(
        f"Could not find countries in {COUNTRIES_FILE}. "
        "Check that the file exists and contains a 'country' column."
    )


# Sample ratio controls
st.sidebar.subheader("🔢 Sample Ratio")

st.sidebar.caption(
    "A larger ratio simulates fewer people. "
    "A smaller ratio simulates more people and may take longer."
)

left, right = st.sidebar.columns(2)

with left:
    if st.button("− 100,000", key="ratio_decrease", use_container_width=True):
        st.session_state["sample_ratio"] = max(
            1,
            st.session_state["sample_ratio"] - 100_000,
        )

with right:
    if st.button("+ 100,000", key="ratio_increase", use_container_width=True):
        st.session_state["sample_ratio"] += 100_000

sample_ratio = st.sidebar.number_input(
    "Sample ratio",
    min_value=1,
    step=100_000,
    value=int(st.session_state["sample_ratio"]),
    key="ratio_input",
    help="Higher values generally result in fewer simulated individuals.",
)

# Keep the ratio in session state for the next rerun.
st.session_state["sample_ratio"] = int(sample_ratio)

st.sidebar.caption(f"Current sample ratio: **{int(sample_ratio):,}**")


# Date controls
st.sidebar.subheader("📅 Simulation Dates")

start_date = st.sidebar.date_input(
    "Start Date",
    value=DEFAULT_START,
    format="DD-MM-YYYY",
    key="simulation_start",
)

end_date = st.sidebar.date_input(
    "End Date",
    value=DEFAULT_END,
    format="DD-MM-YYYY",
    key="simulation_end",
)

if start_date > end_date:
    st.sidebar.error("Start Date must be on or before End Date.")

st.sidebar.divider()

run_clicked = st.sidebar.button(
    "▶ Run Simulation",
    type="primary",
    use_container_width=True,
    disabled=(
        not selected_countries
        or start_date > end_date
        or not available_countries
    ),
)

if st.sidebar.button("↻ Clear Results", use_container_width=True):
    st.session_state["simulation_results"] = None
    st.session_state["result_countries"] = []
    st.session_state["result_start"] = None
    st.session_state["result_end"] = None
    st.session_state["result_ratio"] = None
    st.session_state["simulation_error"] = None
    st.session_state["simulation_complete"] = False
    st.rerun()


# --------------------------------------------------
# Run simulation
# --------------------------------------------------
if run_clicked:
    st.session_state["simulation_error"] = None
    st.session_state["simulation_complete"] = False

    try:
        with st.spinner("Running the COVID-19 simulation... Please wait."):
            result = run_simulation(
                countries_csv_name=COUNTRIES_FILE,
                countries=list(selected_countries),
                sample_ratio=int(sample_ratio),
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
            )

        st.session_state["simulation_results"] = (
            result.copy() if isinstance(result, pd.DataFrame) else None
        )
        st.session_state["result_countries"] = list(selected_countries)
        st.session_state["result_start"] = start_date.isoformat()
        st.session_state["result_end"] = end_date.isoformat()
        st.session_state["result_ratio"] = int(sample_ratio)
        st.session_state["simulation_complete"] = True

        st.success("Simulation completed successfully!")

    except Exception as exc:
        st.session_state["simulation_error"] = str(exc)


if st.session_state["simulation_error"]:
    st.error(
        "Simulation failed. Check the error details below and your "
        "assignment2.py and helper.py files."
    )
    st.code(st.session_state["simulation_error"])


# --------------------------------------------------
# Results data
# --------------------------------------------------
if st.session_state["simulation_results"] is not None:
    summary_df = st.session_state["simulation_results"].copy()
else:
    summary_df = load_summary_data()

if not summary_df.empty:
    if "date" in summary_df.columns:
        summary_df["date"] = pd.to_datetime(
            summary_df["date"], errors="coerce"
        )

    # Use the saved run settings after a simulation has been performed.
    result_countries = st.session_state["result_countries"]
    result_start = st.session_state["result_start"]
    result_end = st.session_state["result_end"]

    if result_countries and "country" in summary_df.columns:
        summary_df = summary_df[
            summary_df["country"].astype(str).isin(result_countries)
        ]

    if result_start and "date" in summary_df.columns:
        summary_df = summary_df[
            summary_df["date"] >= pd.Timestamp(result_start)
        ]

    if result_end and "date" in summary_df.columns:
        summary_df = summary_df[
            summary_df["date"] <= pd.Timestamp(result_end)
        ]


# --------------------------------------------------
# Selected date range — always visible
# --------------------------------------------------
st.subheader("📅 Selected Simulation Period")

date_col1, date_col2, date_col3 = st.columns([1, 1, 1])

with date_col1:
    st.metric(
        "Start Date",
        start_date.strftime("%d-%m-%Y"),
    )

with date_col2:
    st.metric(
        "End Date",
        end_date.strftime("%d-%m-%Y"),
    )

with date_col3:
    total_days = (end_date - start_date).days + 1
    st.metric("Duration", f"{total_days:,} days")


# --------------------------------------------------
# Navigation
# --------------------------------------------------
overview_tab, trends_tab, data_tab, about_tab = st.tabs(
    [
        "📊 Overview",
        "📈 Time-Series Analysis",
        "🗃️ Data Explorer",
        "ℹ️ About",
    ]
)


# --------------------------------------------------
# Overview tab
# --------------------------------------------------
with overview_tab:
    st.subheader("Simulation Overview")

    if summary_df.empty:
        st.info(
            "No results are available for the selected period yet. "
            "Choose your countries and dates in the sidebar, then click "
            "**Run Simulation**."
        )
    else:
        st.caption(
            "The metrics and charts below use the currently displayed "
            "simulation results."
        )

        states = ["H", "I", "S", "M", "D"]

        for state in states:
            if state not in summary_df.columns:
                summary_df[state] = 0

        total_deaths = summary_df["D"].sum()
        total_healthy = summary_df["H"].sum()
        total_infected = summary_df["I"].sum()
        total_susceptible = summary_df["S"].sum()
        total_mild = summary_df["M"].sum()

        metric1, metric2, metric3, metric4, metric5 = st.columns(5)

        metric1.metric("Deaths (sum)", format_number(total_deaths))
        metric2.metric("Infected (sum)", format_number(total_infected))
        metric3.metric("Healthy (sum)", format_number(total_healthy))
        metric4.metric("Mild (sum)", format_number(total_mild))
        metric5.metric(
            "Susceptible (sum)",
            format_number(total_susceptible),
        )

        st.divider()

        if "date" in summary_df.columns and "country" in summary_df.columns:
            chart_states = [
                state for state in states if state in summary_df.columns
            ]

            chart_state = st.selectbox(
                "Choose a state to visualize",
                options=chart_states,
                format_func=lambda x: {
                    "H": "Healthy",
                    "I": "Infected",
                    "S": "Susceptible",
                    "M": "Mild",
                    "D": "Deaths",
                }.get(x, x),
                key="overview_state",
            )

            chart_data = (
                summary_df.dropna(subset=["date"])
                .groupby(["date", "country"], as_index=False)[chart_state]
                .sum()
            )

            pivot = chart_data.pivot(
                index="date",
                columns="country",
                values=chart_state,
            ).sort_index()

            st.subheader(
                {
                    "H": "Healthy Individuals",
                    "I": "Infected Individuals",
                    "S": "Susceptible Individuals",
                    "M": "Mild Cases",
                    "D": "Deaths",
                }.get(chart_state, chart_state)
            )

            st.line_chart(pivot)

            # Country comparison for the latest available date
            st.subheader("Country Comparison")

            latest_date = summary_df["date"].max()
            latest_data = summary_df[summary_df["date"] == latest_date]

            if not latest_data.empty:
                compare_cols = [
                    c for c in ["H", "I", "S", "M", "D"]
                    if c in latest_data.columns
                ]

                if compare_cols:
                    compare_df = latest_data.set_index("country")[compare_cols]
                    st.bar_chart(compare_df)

                st.caption(
                    f"Comparison date: {latest_date.strftime('%d-%m-%Y')}"
                )


# --------------------------------------------------
# Time-series analysis tab
# --------------------------------------------------
with trends_tab:
    st.subheader("📈 Time-Series Analysis")

    if summary_df.empty:
        st.info("Run a simulation to display time-series charts.")
    elif "date" in summary_df.columns and "country" in summary_df.columns:
        available_states = [
            c for c in ["H", "I", "S", "M", "D"]
            if c in summary_df.columns
        ]

        chosen_states = st.multiselect(
            "Select states",
            options=available_states,
            default=[
                c for c in ["I", "D"] if c in available_states
            ],
            key="trend_states",
        )

        chosen_countries = st.multiselect(
            "Filter countries",
            options=sorted(
                summary_df["country"].dropna().astype(str).unique()
            ),
            default=sorted(
                summary_df["country"].dropna().astype(str).unique()
            ),
            key="trend_countries",
        )

        filtered = summary_df[
            summary_df["country"].astype(str).isin(chosen_countries)
        ].copy()

        if chosen_states and not filtered.empty:
            for state in chosen_states:
                filtered[state] = pd.to_numeric(
                    filtered[state], errors="coerce"
                )

            long_df = filtered.melt(
                id_vars=["date", "country"],
                value_vars=chosen_states,
                var_name="State",
                value_name="Count",
            )

            long_df["Series"] = (
                long_df["country"].astype(str)
                + " — "
                + long_df["State"].astype(str)
            )

            pivot = long_df.pivot_table(
                index="date",
                columns="Series",
                values="Count",
                aggfunc="sum",
            ).sort_index()

            st.line_chart(pivot)
        else:
            st.info("Choose at least one state and one country to plot.")


# --------------------------------------------------
# Data explorer tab
# --------------------------------------------------
with data_tab:
    st.subheader("🗃️ Data Explorer")

    if summary_df.empty:
        st.info("No summary data is available yet.")
    else:
        st.write("### Summary Time-Series Data")

        search_country = st.text_input(
            "Search country",
            placeholder="Type a country name...",
            key="data_search_country",
        )

        display_df = summary_df.copy()

        if search_country and "country" in display_df.columns:
            display_df = display_df[
                display_df["country"].astype(str).str.contains(
                    search_country,
                    case=False,
                    na=False,
                )
            ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        summary_csv = display_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download displayed summary CSV",
            data=summary_csv,
            file_name="covid_summary_filtered.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.divider()
        st.write("### Individual Simulation Data")

        individual_df = load_individual_data()

        if individual_df.empty:
            st.caption(
                "The individual-level CSV is not available yet. "
                "Run the simulation to generate it."
            )
        else:
            st.dataframe(
                individual_df.head(1000),
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "⬇️ Download individual-level CSV",
                data=individual_df.to_csv(index=False).encode("utf-8"),
                file_name="covid_individual_timeseries.csv",
                mime="text/csv",
                use_container_width=True,
            )

        if os.path.exists(PLOT_FILE):
            st.divider()
            st.write("### Simulation Plot")

            with open(PLOT_FILE, "rb") as plot_file:
                st.download_button(
                    "⬇️ Download simulation plot",
                    data=plot_file.read(),
                    file_name="covid_simulation.png",
                    mime="image/png",
                    use_container_width=True,
                )


# --------------------------------------------------
# About tab
# --------------------------------------------------
with about_tab:
    st.subheader("ℹ️ About This Dashboard")

    st.markdown(
        """
        This dashboard provides an interface for running and exploring
        the COVID-19 simulation implemented in `assignment2.py`.

        **Available features**
        - Select one or more countries.
        - Choose the simulation start and end dates.
        - Adjust the sample ratio.
        - Run the simulation and inspect the results.
        - Compare simulated disease states over time.
        - Explore and download generated CSV data.

        **State labels used in the simulation**
        - `H` — Healthy
        - `I` — Infected
        - `S` — Susceptible
        - `M` — Mild
        - `D` — Deaths

        The dashboard uses the simulation logic and transition parameters
        defined by your project files. Results may vary between runs if
        the simulation uses random sampling.
        """
    )

    st.caption(
        "Make sure assignment2.py, helper.py, sim_parameters.py, "
        "and a2-countries.csv are in the project folder."
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()

st.caption(
    "COVID-19 Simulation Dashboard · Built with Streamlit and Python"
)