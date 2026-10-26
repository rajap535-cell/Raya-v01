import subprocess
import sys
from pathlib import Path


# ============================================================
# TASK 005 - MASTER PIPELINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# MODULES
# ============================================================

MODULES = [

    (
        "Continuous Climate Data Ingestion",
        BASE_DIR
        / "ingestion"
        / "continuous_ingestion.py"
    ),

    (
        "Climate Data Monitoring",
        BASE_DIR
        / "monitoring"
        / "data_monitor.py"
    ),

    (
        "Emerging Anomaly Detection",
        BASE_DIR
        / "anomaly_monitoring"
        / "emerging_anomaly.py"
    ),

    (
        "Forecast Monitoring",
        BASE_DIR
        / "forecast_monitoring"
        / "forecast_monitor.py"
    ),

    (
        "Future Climate Risk Monitoring",
        BASE_DIR
        / "future_risk"
        / "future_risk_monitor.py"
    )
]


# ============================================================
# RUN MODULE
# ============================================================

def run_module(name, script_path):

    print()
    print("=" * 60)
    print(f"RUNNING: {name}")
    print("=" * 60)

    if not script_path.exists():

        print(
            f"ERROR: Module file not found:"
        )

        print(
            script_path
        )

        return False

    result = subprocess.run(
        [
            sys.executable,
            str(script_path)
        ],
        cwd=BASE_DIR
    )

    if result.returncode != 0:

        print()
        print(
            f"FAILED: {name}"
        )

        return False

    print()
    print(
        f"COMPLETED: {name}"
    )

    return True


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_task5_pipeline():

    print()
    print("=" * 60)
    print(
        "TASK 005 - CLIMATE INTELLIGENCE MONITORING PIPELINE"
    )
    print("=" * 60)

    print()
    print(
        "Starting Task 005 pipeline..."
    )


    completed_modules = 0


    for name, script_path in MODULES:

        success = run_module(
            name,
            script_path
        )

        if not success:

            print()
            print("=" * 60)
            print(
                "TASK 005 PIPELINE FAILED"
            )
            print("=" * 60)

            print()
            print(
                f"Failed module: {name}"
            )

            return False

        completed_modules += 1


    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(
        "TASK 005 PIPELINE COMPLETED SUCCESSFULLY"
    )
    print("=" * 60)

    print()
    print(
        f"Modules completed: "
        f"{completed_modules}/{len(MODULES)}"
    )

    print()
    print(
        "Task 005 monitoring chain:"
    )

    print(
        "1. Continuous Data Ingestion       [OK]"
    )

    print(
        "2. Climate Data Monitoring         [OK]"
    )

    print(
        "3. Emerging Anomaly Detection     [OK]"
    )

    print(
        "4. Forecast Monitoring             [OK]"
    )

    print(
        "5. Future Climate Risk Monitoring  [OK]"
    )

    print()
    print(
        "Climate Intelligence monitoring is active."
    )

    return True


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":

    success = run_task5_pipeline()

    if success:

        sys.exit(0)

    else:

        sys.exit(1)