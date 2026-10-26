#forcasting_pipeline.py
import logging

from configs.settings import LOG_PATH

from forecasting.prophet_engine import (
    run_forecast
)


# --------------------------------
# Logging Configuration
# --------------------------------

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_forecasting_pipeline():

    try:

        forecast = run_forecast()

        if forecast is None:

            logging.error(
                "Forecasting pipeline returned no forecast."
            )

            print(
                "Forecasting pipeline failed."
            )

            return None

        logging.info(
            "Forecasting Pipeline Completed Successfully."
        )

        print(
            "Forecasting Pipeline Completed Successfully."
        )

        return forecast

    except Exception as e:

        logging.exception(
            "Forecasting Pipeline Failed."
        )

        print(
            f"Forecasting Pipeline Failed: {e}"
        )

        return None


if __name__ == "__main__":

    run_forecasting_pipeline()