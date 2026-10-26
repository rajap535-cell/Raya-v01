import logging
import pandas as pd


REQUIRED_COLUMNS = [
    "Date",
    "Temp_Max",
    "Temp_Min",
    "Rainfall",
    "WindSpeed"
]


def validate_data(df):
    """
    Validate climate data before it enters the pipeline.
    """

    # 1. Check empty dataset
    if df.empty:
        logging.error("Dataset is empty.")
        raise ValueError("Dataset is empty.")

    # 2. Check required columns
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        logging.error(
            f"Missing columns: {missing_columns}"
        )
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # 3. Convert Date column
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # 4. Check invalid dates
    if df["Date"].isna().any():
        logging.error("Invalid dates found.")
        raise ValueError("Invalid dates found.")

    # 5. Check missing values
    missing_values = df[REQUIRED_COLUMNS].isna().sum()

    if missing_values.sum() > 0:
        logging.error(
            f"Missing values found:\n{missing_values}"
        )
        raise ValueError(
            f"Missing values found:\n{missing_values}"
        )

    # 6. Check duplicate dates
    if df["Date"].duplicated().any():
        logging.error("Duplicate dates found.")
        raise ValueError("Duplicate dates found.")

    # 7. Check chronological order
    if not df["Date"].is_monotonic_increasing:
        logging.warning(
            "Dates are not in chronological order. Sorting data."
        )

        df.sort_values(
            "Date",
            inplace=True
        )

        df.reset_index(
            drop=True,
            inplace=True
        )

    # 8. Check numeric columns
    numeric_columns = [
        "Temp_Max",
        "Temp_Min",
        "Rainfall",
        "WindSpeed"
    ]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            logging.error(
                f"Column {column} is not numeric."
            )
            raise ValueError(
                f"Column {column} must be numeric."
            )

    logging.info(
        "Climate data validation successful."
    )

    return True