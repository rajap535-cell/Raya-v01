import pandas as pd
import pytest

from risk_engine.rainfall import detect_rainfall_risk


def test_rainfall():

    df = pd.DataFrame({

        "Rainfall": [
            20,
            60,
            120
        ]

    })

    result = detect_rainfall_risk(df)

    assert result["Heavy Rainfall"] == 2
    assert result["Extreme Rainfall"] == 1


def test_no_rainfall_risk():

    df = pd.DataFrame({

        "Rainfall": [
            5,
            10,
            20
        ]

    })

    result = detect_rainfall_risk(df)

    assert result["Heavy Rainfall"] == 0
    assert result["Extreme Rainfall"] == 0


def test_empty_dataset():

    df = pd.DataFrame({

        "Rainfall": []

    })

    result = detect_rainfall_risk(df)

    assert result["Heavy Rainfall"] == 0
    assert result["Extreme Rainfall"] == 0


def test_missing_column():

    df = pd.DataFrame({

        "Rain": [
            10,
            50
        ]

    })

    with pytest.raises(KeyError):

        detect_rainfall_risk(df)