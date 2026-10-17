"""Regression tests for the COVID-19 simulation implementation."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import assignment2


class TestSimulationHelpers(unittest.TestCase):
    def test_sample_counts_follow_age_percentages(self):
        country_row = pd.Series(
            {
                "population": 10_000_000,
                "less_5": 20,
                "5_to_14": 20,
                "15_to_24": 20,
                "25_to_64": 20,
                "over_65": 20,
            }
        )
        self.assertEqual(
            assignment2._age_group_sample_counts(country_row, 1_000_000),
            {group: 2 for group in assignment2.AGE_GROUPS},
        )

    @patch("assignment2.random.choices", return_value=["I"])
    def test_transition_selector_uses_configured_states(self, mock_choices):
        result = assignment2._choose_next_state("less_5", "H")
        self.assertEqual(result, "I")
        mock_choices.assert_called_once()

    @patch("assignment2._choose_next_state", return_value="I")
    def test_person_starts_healthy_and_transitions_after_one_day(self, _mock_transition):
        dates = pd.date_range("2021-04-01", periods=2, freq="D")
        rows = assignment2._simulate_person(7, "Sweden", "less_5", dates)
        self.assertEqual([row["state"] for row in rows], ["H", "I"])
        self.assertEqual(rows[0]["prev_state"], "H")
        self.assertEqual(rows[1]["prev_state"], "H")
        self.assertEqual([row["person_id"] for row in rows], [7, 7])

    def test_invalid_sample_ratio_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "sample_ratio"):
            assignment2._validate_inputs(["Sweden"], 0, "2021-04-01", "2021-04-02")

    def test_start_date_after_end_date_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "on or before"):
            assignment2._validate_inputs(["Sweden"], 1e6, "2021-04-03", "2021-04-02")

    def test_run_writes_required_outputs_and_summary_schema(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp_path = Path(temporary_directory)
            pd.DataFrame(
                [
                    {
                        "country": "Testland",
                        "population": 5_000_000,
                        "less_5": 20,
                        "5_to_14": 20,
                        "15_to_24": 20,
                        "25_to_64": 20,
                        "over_65": 20,
                    }
                ]
            ).to_csv(temp_path / "countries.csv", index=False)

            with patch.object(assignment2, "__file__", str(temp_path / "assignment2.py")), patch.object(
                assignment2, "create_plot"
            ) as mock_create_plot:
                summary = assignment2.run(
                    countries_csv_name="countries.csv",
                    countries=["Testland"],
                    sample_ratio=1_000_000,
                    start_date="2021-04-01",
                    end_date="2021-04-03",
                )

            self.assertEqual(list(summary.columns), list(assignment2.SUMMARY_COLUMNS))
            self.assertEqual(len(summary), 3)
            self.assertTrue((temp_path / assignment2.SIMULATED_FILE).is_file())
            self.assertTrue((temp_path / assignment2.SUMMARY_FILE).is_file())
            mock_create_plot.assert_called_once_with(assignment2.SUMMARY_FILE, ["Testland"])

            saved_summary = pd.read_csv(temp_path / assignment2.SUMMARY_FILE)
            self.assertEqual(list(saved_summary.columns), list(assignment2.SUMMARY_COLUMNS))


if __name__ == "__main__":
    unittest.main()
