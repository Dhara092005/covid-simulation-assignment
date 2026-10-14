"""Streamlit interface for the COVID-19 simulation assignment."""
from pathlib import Path
import pandas as pd
import streamlit as st
import assignment2

BASE_DIR = Path(__file__).resolve().parent
COUNTRIES_FILE = BASE_DIR / "a2-countries.csv"
PLOT_FILE = BASE_DIR / "a2-covid-simulation.png"

st.set_page_config(page_title="COVID-19 Simulation", layout="wide")
st.title("COVID-19 Infection Simulation")
st.write("Choose the simulation settings and select one or more countries.")

if not COUNTRIES_FILE.exists():
    st.error(f"Country dataset not found: {COUNTRIES_FILE.name}")
    st.stop()

country_df = pd.read_csv(COUNTRIES_FILE)
country_options = sorted(country_df["country"].dropna().unique().tolist())

with st.form("simulation_settings"):
    sample_ratio = st.number_input(
        "Sample Ratio", min_value=1.0, value=1_000_000.0, step=100_000.0,
        help="For example, 1,000,000 represents approximately one sample per million people."
    )
    start_date = st.date_input("Start Date", value=pd.Timestamp("2021-04-01").date())
    end_date = st.date_input("End Date", value=pd.Timestamp("2022-04-30").date())
    selected_countries = st.multiselect(
        "Countries", options=country_options,
        default=[c for c in ["Afghanistan", "Sweden", "Japan"] if c in country_options]
    )
    run_clicked = st.form_submit_button("Run")

if run_clicked:
    if not selected_countries:
        st.error("Please select at least one country.")
    elif start_date > end_date:
        st.error("Start Date must be on or before End Date.")
    else:
        with st.spinner("Running simulation. This may take a little while..."):
            try:
                assignment2.run(
                    countries_csv_name="a2-countries.csv",
                    countries=selected_countries,
                    sample_ratio=sample_ratio,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                )
                st.success("Simulation completed. Output CSV files and chart have been created.")
            except Exception as exc:
                st.exception(exc)

if PLOT_FILE.exists():
    st.subheader("Simulation chart")
    st.image(str(PLOT_FILE), caption="COVID-19 infection states over time", use_container_width=True)

summary_path = BASE_DIR / "a2-covid-summary-timeseries.csv"
simulated_path = BASE_DIR / "a2-covid-simulated-timeseries.csv"
if summary_path.exists():
    st.download_button("Download summary CSV", data=summary_path.read_bytes(), file_name=summary_path.name, mime="text/csv")
if simulated_path.exists():
    st.download_button("Download simulated timeseries CSV", data=simulated_path.read_bytes(), file_name=simulated_path.name, mime="text/csv")
