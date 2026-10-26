import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


def calculate_metrics(
    actual,
    predicted
):

    actual = np.asarray(
        actual,
        dtype=float
    )

    predicted = np.asarray(
        predicted,
        dtype=float
    )

    if len(actual) == 0:
        raise ValueError(
            "Actual values cannot be empty."
        )

    if len(actual) != len(predicted):
        raise ValueError(
            "Actual and predicted values must have the same length."
        )

    # MAE
    mae = mean_absolute_error(
        actual,
        predicted
    )

    # RMSE
    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted
        )
    )

    # Safe MAPE
    non_zero_actual = actual != 0

    if np.any(non_zero_actual):

        mape = np.mean(
            np.abs(
                (
                    actual[non_zero_actual]
                    - predicted[non_zero_actual]
                )
                / actual[non_zero_actual]
            )
        ) * 100

    else:

        mape = np.nan

    # R2
    if len(actual) >= 2:

        r2 = r2_score(
            actual,
            predicted
        )

    else:

        r2 = np.nan

    return {
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape,
        "R2": r2
    }


def save_metrics(
    metrics,
    output_path="logs/model_evaluation.txt"
):

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "Prophet Model Evaluation Results\n"
        )

        file.write(
            "================================\n\n"
        )

        file.write(
            f"MAE  : {metrics['MAE']:.4f}\n"
        )

        file.write(
            f"RMSE : {metrics['RMSE']:.4f}\n"
        )

        file.write(
            f"MAPE : {metrics['MAPE']:.4f}%\n"
        )

        file.write(
            f"R2   : {metrics['R2']:.4f}\n"
        )

    return output_path