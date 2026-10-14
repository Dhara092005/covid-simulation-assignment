ET1556 Assignment 2 - COVID-19 Simulation

Files:
- assignment2.py: main simulation and CSV/chart generation
- streamlit_ui.py: Streamlit interface
- sim_parameters.py: supplied transition probabilities and holding times
- helper.py: supplied plotting helper
- a2-countries.csv: supplied country dataset
- assignment2.txt and streamlit_ui.txt: same source contents with .txt extensions for submission
- a2-covid-simulated-timeseries.csv: generated individual time-series output
- a2-covid-summary-timeseries.csv: generated country/date summary output
- a2-covid-simulation.png: generated plot
- test.py: supplied assignment test

Run the assignment test from this folder:
    python test.py

Run the Streamlit app (install Streamlit first if needed):
    python -m pip install streamlit
    streamlit run streamlit_ui.py

The simulation is stochastic, so the output values can differ each time it runs.
The code was tested with the supplied test configuration; the Streamlit interface
could not be run in this environment because Streamlit is not installed here.
