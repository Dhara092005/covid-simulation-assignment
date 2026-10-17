# COVID-19 Simulation Lab

A Python and Streamlit project that simulates daily COVID-19 health-state transitions for sampled populations across selected countries and age groups. It exports individual-level and country-level time series and visualizes the state distribution over time.

> **Scope note:** This is a simplified educational stochastic model, not a clinical tool or a real-world epidemiological forecast. Transition probabilities and holding times are the assignment-provided assumptions.

## Features

- Age-group-aware population sampling from `a2-countries.csv`.
- Daily state transitions for healthy (`H`), infected without symptoms (`I`), infected with symptoms (`S`), immune (`M`), and deceased (`D`).
- Transition probabilities and holding times retained in `sim_parameters.py`.
- Interactive Streamlit controls for country selection, sample ratio, and date range.
- Per-country stacked-area charts and summary metrics.
- CSV exports for individual timelines and daily country summaries.
- Input validation and unit/integration tests.

## Project structure

```text
.
├── assignment2.py                  # Required simulation entry point and run(...)
├── streamlit_ui.py                 # Streamlit dashboard
├── sim_parameters.py               # Assignment transition probabilities/holding times
├── helper.py                       # Chart generation (create_plot)
├── a2-countries.csv                # Provided country population/age data
├── tests/
│   └── test_simulation.py          # Project tests
├── test.py                         # Assignment-provided test entry point
├── requirements.txt
├── assignment2.txt                 # Assignment submission copy of assignment2.py
├── streamlit_ui.txt                # Assignment submission copy of streamlit_ui.py
└── a2-covid-*.csv / .png           # Generated assignment outputs
```

## Requirements

- Python 3.10 or newer
- Packages listed in `requirements.txt`

## Setup

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell prevents activation, you can install using `py -m pip install -r requirements.txt` in the environment you intend to use.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the dashboard

From the project directory:

```bash
streamlit run streamlit_ui.py
```

Open the local URL printed in the terminal (usually `http://localhost:8501`). Select one or more countries, a sample ratio, and a date range, then click **Run simulation**.

## Run the simulation without Streamlit

The assignment-compatible entry point is `assignment2.run`:

```python
import assignment2

summary = assignment2.run(
    countries_csv_name="a2-countries.csv",
    countries=["Afghanistan", "Sweden", "Japan"],
    sample_ratio=1e6,
    start_date="2021-04-01",
    end_date="2022-04-30",
)
print(summary.head())
```

The function keeps the required output names and writes files beside `assignment2.py`:

- `a2-covid-simulated-timeseries.csv` — one row per person per date.
- `a2-covid-summary-timeseries.csv` — one row per country per date, with state counts.
- `a2-covid-simulation.png` — generated state-distribution chart.

The model is stochastic, so repeated runs can produce different results. The transition probabilities and holding-time values in `sim_parameters.py` are preserved as supplied for the assignment.

## Tests

Run the project tests:

```bash
python -m unittest discover -s tests -v
```

Run the assignment-provided test separately:

```bash
python test.py
```

The assignment test generates the required CSV files and chart using the supplied sample settings.

## Model assumptions and limitations

- Every simulated person starts in the healthy (`H`) state.
- State transition probabilities depend on age group and are read from `sim_parameters.py`.
- Holding times are fixed per state; a value of zero is treated as one day before a transition attempt.
- Country differences in public-health policy, vaccination, healthcare capacity, and date-specific infection rates are not modelled.
- The sample represents a scaled-down population. Counts in charts are simulated sample counts, not the actual number of people in a country.
