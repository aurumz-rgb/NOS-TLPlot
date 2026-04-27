
# CONTRIBUTORS ignore this file as it is a part of pytest. The main files are nos-tlplot.py and app.py.

import pytest
import pandas as pd
import os
import tempfile
import nos_tlplot

class TestDataProcessing:
    def test_process_detailed_nos_valid(self, sample_df):
        """Test that valid data is processed correctly and columns are added."""
        processed_df = nos_tlplot.process_detailed_nos(sample_df)
        

        assert "Selection" in processed_df.columns
        assert "Comparability" in processed_df.columns
        assert "Outcome/Exposure" in processed_df.columns
        

        assert processed_df.loc[0, "Selection"] == 4

        assert processed_df.loc[0, "Comparability"] == 2

    def test_process_detailed_nos_missing_column(self, sample_df):
        """Test that missing required columns raise a ValueError."""
        df_missing = sample_df.drop(columns=["Total Score"])
        with pytest.raises(ValueError, match="Missing required columns"):
            nos_tlplot.process_detailed_nos(df_missing)

    def test_process_detailed_nos_invalid_numeric(self, sample_df):
        """Test that non-numeric data in score columns raises ValueError."""
        df_invalid = sample_df.copy()
        df_invalid["Representativeness"] = "invalid_string"
        with pytest.raises(ValueError, match="must be numeric"):
            nos_tlplot.process_detailed_nos(df_invalid)
    
    def test_process_detailed_nos_out_of_range(self, sample_df):
        """Test that scores out of 0-5 range raise ValueError."""
        df_invalid = sample_df.copy()
        df_invalid["Representativeness"] = 99  # Invalid score
        with pytest.raises(ValueError, match="invalid star values"):
            nos_tlplot.process_detailed_nos(df_invalid)


class TestPlotGeneration:
    """Test that every plot function generates a valid file without crashing."""
    
    @pytest.fixture
    def processed_df(self, sample_df):
        return nos_tlplot.process_detailed_nos(sample_df)

    @pytest.fixture
    def large_df(self, processed_df):
        """Create a DF with >5 studies to test limit logic."""
        return pd.concat([processed_df] * 3, ignore_index=True)

    def _assert_plot_created(self, func, df, filename):
        """Helper to run plot function and check file existence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, filename)
            func(df, output_path, theme="traffic_light")
            assert os.path.exists(output_path), f"{filename} was not created"
            assert os.path.getsize(output_path) > 0, f"{filename} is empty"

    def test_professional_plot(self, processed_df):
        self._assert_plot_created(nos_tlplot.professional_plot, processed_df, "prof_plot.png")

    def test_star_distribution_hist(self, processed_df):
        self._assert_plot_created(nos_tlplot.plot_star_distribution_hist, processed_df, "star_hist.png")

    def test_domain_heatmap(self, processed_df):
        self._assert_plot_created(nos_tlplot.plot_domain_heatmap, processed_df, "heatmap.png")

    def test_lollipop_chart(self, processed_df):
        self._assert_plot_created(nos_tlplot.plot_lollipop_total, processed_df, "lollipop.png")

    def test_score_table(self, processed_df):
        self._assert_plot_created(nos_tlplot.plot_score_table, processed_df, "table.png")

    def test_donut_chart(self, processed_df):
        self._assert_plot_created(nos_tlplot.plot_donut_domain_risk, processed_df, "donut.png")

    def test_line_ordered_scores(self, processed_df):
        self._assert_plot_created(nos_tlplot.plot_line_ordered_scores, processed_df, "line.png")

    def test_pie_chart(self, processed_df):
        self._assert_plot_created(nos_tlplot.plot_pie_overall_rob, processed_df, "pie.png")

    def test_stacked_area_chart(self, processed_df):
        self._assert_plot_created(nos_tlplot.plot_stacked_area_risk, processed_df, "stacked.png")


    def test_dot_profile_success(self, processed_df):
        """Dot profile should work for <= 5 studies."""
        self._assert_plot_created(nos_tlplot.plot_dot_profile, processed_df, "dot_success.png")

    def test_dot_profile_fail(self, large_df):
        """Dot profile should fail/return early for > 5 studies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "dot_fail.png")
            # This should print an error and return without creating a file
            nos_tlplot.plot_dot_profile(large_df, output_path, theme="traffic_light")
            assert not os.path.exists(output_path), "Dot profile created despite > 5 studies limit"

    def test_radar_chart_success(self, processed_df):
        """Radar should work for <= 5 studies."""
        self._assert_plot_created(nos_tlplot.plot_domain_radar, processed_df, "radar_success.png")

    def test_radar_chart_fail(self, large_df):
        """Radar should fail/return early for > 5 studies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "radar_fail.png")
            nos_tlplot.plot_domain_radar(large_df, output_path, theme="traffic_light")
            assert not os.path.exists(output_path), "Radar chart created despite > 5 studies limit"

    def test_theme_radar_success(self, processed_df):
        """Theme radar should work for <= 5 studies."""
        self._assert_plot_created(nos_tlplot.plot_theme_radar, processed_df, "theme_radar_success.png")

    def test_theme_radar_fail(self, large_df):
        """Theme radar should fail/return early for > 5 studies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "theme_radar_fail.png")
            nos_tlplot.plot_theme_radar(large_df, output_path, theme="traffic_light")
            assert not os.path.exists(output_path), "Theme radar created despite > 5 studies limit"