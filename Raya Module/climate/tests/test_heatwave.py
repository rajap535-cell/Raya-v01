import pandas as pd
import pytest

from risk_engine.heatwave import detect_heatwaves


def test_heatwave():

    df = pd.DataFrame({

        "Temp_Max": [
            35,
            42,
            47
        ]

    })

    result = detect_heatwaves(df)

    assert result["Heatwave Days"] == 2
    assert result["Severe Heatwave Days"] == 1


def test_no_heatwave():

    df = pd.DataFrame({

        "Temp_Max": [
            25,
            30,
            35
        ]

    })

    result = detect_heatwaves(df)

    assert result["Heatwave Days"] == 0
    assert result["Severe Heatwave Days"] == 0


def test_empty_dataset():

    df = pd.DataFrame({

        "Temp_Max": []

    })

    result = detect_heatwaves(df)

    assert result["Heatwave Days"] == 0
    assert result["Severe Heatwave Days"] == 0


def test_missing_column():

    df = pd.DataFrame({

        "Temperature": [
            30,
            45
        ]

    })

    with pytest.raises(KeyError):

        detect_heatwaves(df)