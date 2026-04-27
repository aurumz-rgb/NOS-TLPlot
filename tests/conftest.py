
# CONTRIBUTORS ignore this file as it is a part of pytest. The main files are nos-tlplot.py and app.py.

import pytest
import pandas as pd
import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session", autouse=True)
def mock_theme_options():
    import nos_tlplot
    if not hasattr(nos_tlplot, 'THEME_OPTIONS'):
        nos_tlplot.THEME_OPTIONS = {
            "traffic_light": {"Low": "#2ecc71", "Moderate": "#f1c40f", "High": "#e74c3c"},
            "gray": {"Low": "#cccccc", "Moderate": "#888888", "High": "#444444"}
        }

@pytest.fixture
def sample_df():
    """Provides a standard valid DataFrame for testing."""
    data = {
        "Author, Year": ["Study A", "Study B", "Study C"],
        "Representativeness": [1, 1, 0],
        "Non-exposed Selection": [1, 0, 1],
        "Exposure Ascertainment": [1, 1, 1],
        "Outcome Absent at Start": [1, 1, 0],
        "Comparability (Age/Gender)": [1, 2, 0],
        "Comparability (Other)": [1, 0, 1],
        "Outcome Assessment": [1, 1, 1],
        "Follow-up Length": [1, 1, 0],
        "Follow-up Adequacy": [1, 0, 1],
        "Total Score": [9, 7, 5],
        "Overall RoB": ["Low", "Moderate", "High"]
    }
    return pd.DataFrame(data)