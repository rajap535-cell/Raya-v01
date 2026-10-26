import pandas as pd


def split_data(df, train_ratio=0.8):

    if df.empty:
        raise ValueError(
            "Cannot split an empty dataset."
        )

    if not 0 < train_ratio < 1:
        raise ValueError(
            "train_ratio must be between 0 and 1."
        )

    required_columns = [
        "ds",
        "y"
    ]

    for column in required_columns:

        if column not in df.columns:
            raise ValueError(
                f"Missing required column: {column}"
            )

    # Ensure correct date type
    df = df.copy()

    df["ds"] = pd.to_datetime(
        df["ds"]
    )

    # Sort chronologically
    df = df.sort_values(
        "ds"
    ).reset_index(drop=True)

    split_index = int(
        len(df) * train_ratio
    )

    if split_index == 0 or split_index == len(df):
        raise ValueError(
            "Dataset is too small for train-test split."
        )

    train_df = df.iloc[
        :split_index
    ].copy()

    test_df = df.iloc[
        split_index:
    ].copy()

    return (
        train_df,
        test_df
    )