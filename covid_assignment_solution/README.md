# COVID-19 Simulation Using Python

## 1. Project Overview

This project simulates the progression of COVID-19 across selected countries using Python. It uses country demographic data, age groups, transition probabilities, and holding times to simulate daily changes in individuals' health states.

The project generates individual-level simulation data, daily summary statistics, and a visualization of the simulation results. It also includes a Streamlit web application for running simulations interactively.

## 2. Project Files

| File Name | Description |
|---|---|
| `assignment2.py` | Main simulation program. Runs the simulation and generates the output data. |
| `streamlit_ui.py` | Provides a web interface for selecting countries, dates, and sample ratio. |
| `sim_parameters.py` | Defines health-state transition probabilities and holding times. |
| `helper.py` | Contains helper functions for processing summary data and generating plots. |
| `test.py` | Runs the provided simulation test for Afghanistan, Sweden, and Japan. |
| `a2-countries.csv` | Input dataset containing country demographic information. |
| `a2-covid-simulated-timeseries.csv` | Contains individual-level simulation records. |
| `a2-covid-summary-timeseries.csv` | Contains daily health-state counts for each simulated country. |
| `a2-covid-simulation.png` | Visualization generated from the simulation summary. |
| `requirements.txt` | Lists the Python packages required to run the project. |
| `assignment2.txt` | Text copy of the main simulation program. |
| `streamlit_ui.txt` | Text copy of the Streamlit application. |

## 3. Requirements

- Python 3
- Packages listed in `requirements.txt`
- PowerShell, Command Prompt, or another terminal

## 4. Installation

Clone the repository:

```bash
git clone https://github.com/Dhara092005/covid-simulation-assignment.git
```

Navigate to the project directory:

```bash
cd covid-simulation-assignment/covid_assignment_solution
```

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

## 5. Run the Simulation Test

Execute the test script:

```bash
python test.py
```

The provided test runs the simulation for Afghanistan, Sweden, and Japan from 1 April 2021 to 30 April 2022.

A successful test should finish with `OK` and display `Plotting Done!`.

## 6. Run the Streamlit Application

Start the web application:

```bash
python -m streamlit run streamlit_ui.py
```

Open the local URL displayed in the terminal in your browser.

Use the interface to select countries, specify the start and end dates, configure the sample ratio, and run the simulation.

## 7. Health States

The simulation uses the following health-state labels:

- `H` — Healthy
- `I` — Infected
- `S` — Severe
- `M` — Managed/Medical
- `D` — Dead

Transition probabilities and holding times are defined in `sim_parameters.py`.

## 8. Simulation Outputs

### Individual-Level Results

File: `a2-covid-simulated-timeseries.csv`

Contains individual-level records, including person ID, age group, country, date, current state, staying days, and previous state.

### Summary Results

File: `a2-covid-summary-timeseries.csv`

Contains daily counts of individuals in each health state for each simulated country.

### Visualization

File: `a2-covid-simulation.png`

Displays the plotted simulation results generated from the summary data.

## 9. Repository

GitHub: https://github.com/Dhara092005/covid-simulation-assignment

## 10. Author

Dhara
