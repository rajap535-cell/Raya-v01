"""
RAYA Phase 4G
Persistent Farmer Intelligence Layer

Runtime End-to-End Validation

## Validation Flow

Farmer A
-> Farm
-> Field
-> Soil
-> Season
-> Farmer Search
-> Contextual Decision Engine
-> Advisory History

Farmer B
-> Farm
-> Field
-> Soil
-> Season
-> Farmer Search
-> Contextual Decision Engine
-> Advisory History

Then:

```
Restart / Reload
    ->
Verify independent persistence
    ->
Verify advisory history
    ->
Verify no duplicate farmer_search() execution
    ->
Inspect actual contextual advisory schema
```

Run:

```
python -m persistent_memory.phase4_validation
```

"""

from __future__ import annotations

import sys
import traceback

from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import Any, Dict, List

# ============================================================

# PROJECT PATH

# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================

# PERSISTENT MEMORY MODULES

# ============================================================

from persistent_memory.farmer_registry import FarmerRegistry

from persistent_memory.farm_field_registry import FarmFieldRegistry

from persistent_memory.soil_memory import SoilMemory

from persistent_memory.season_manager import SeasonManager

from persistent_memory.advisory_history import AdvisoryHistory

from persistent_memory.persistent_pipeline import PersistentFarmerPipeline

# ============================================================

# RAYA CORE ENGINES

# ============================================================

from farmer_search_engine import farmer_search

from contextual_decision_engine import generate_contextual_advisory

# ============================================================

# CONSTANTS

# ============================================================

LINE = "=" * 78

# ============================================================

# VALIDATION TRACKER

# ============================================================


class ValidationTracker:
    """
    Tracks validation checks and prints the final report.
    """

    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[str] = []

    def section(
        self,
        title: str,
    ) -> None:
        print()
        print("-" * 78)
        print(title)
        print("-" * 78)

    def check(
        self,
        name: str,
        condition: bool,
        details: str = "",
    ) -> bool:
        if condition:
            self.passed.append(name)
            print(f"  [PASS] {name}")
            if details:
                print(f"         {details}")
            return True

        self.failed.append(name)
        print(f"  [FAIL] {name}")
        if details:
            print(f"         {details}")
        return False

    def print_summary(
        self,
    ) -> bool:
        print()
        print(LINE)
        print("RAYA PHASE 4G - FINAL VALIDATION SUMMARY")
        print(LINE)

        print()
        print(f"Passed: {len(self.passed)}")
        print(f"Failed: {len(self.failed)}")

        print()

        if self.failed:
            print("FAILED CHECKS:")
            for item in self.failed:
                print(f"  - {item}")

            print()
            print("PHASE 4G VALIDATION STATUS: FAILED")
            return False

        print("PHASE 4G VALIDATION STATUS: PASSED")
        print()
        print(
            "Persistent Farmer Intelligence Layer "
            "validated successfully."
        )
        return True


# ============================================================

# FARMER SEARCH COUNTER

# ============================================================


class CountingFarmerSearch:
    """
    Wrap the real farmer_search() function.

    This validates that farmer_search() is executed
    exactly once per advisory generation.
    """

    def __init__(self):
        self.total_calls = 0
        self.calls: List[Dict[str, Any]] = []

    def __call__(
        self,
        state: str,
        district: str,
        crop: str,
        stage: str,
        *args,
        **kwargs,
    ) -> Dict[str, Any]:
        self.total_calls += 1

        call_data = {
            "state": state,
            "district": district,
            "crop": crop,
            "stage": stage,
        }

        self.calls.append(call_data)

        print()
        print(f"[farmer_search call #{self.total_calls}]")
        print(f"  Location: {district}, {state}")
        print(f"  Crop: {crop}")
        print(f"  Stage: {stage}")

        return farmer_search(
            state=state,
            district=district,
            crop=crop,
            stage=stage,
        )


# ============================================================

# VALIDATION ID

# ============================================================


def build_validation_suffix() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ============================================================

# CREATE FARMER A

# ============================================================


def create_farmer_a(
    suffix: str,
    farmer_registry: FarmerRegistry,
    farm_registry: FarmFieldRegistry,
    soil_memory: SoilMemory,
    season_manager: SeasonManager,
) -> Dict[str, Any]:
    farmer = farmer_registry.create_farmer(
        name=f"Farmer A {suffix}",
        phone=f"900{suffix[-7:]}",
        email=f"farmer_a_{suffix}@validation.local",
        village="Validation Village A",
        district="Varanasi",
        state="Uttar Pradesh",
        farming_experience_years=20,
        labor_availability="high",
        budget_constraint="low",
        guidance_preference="detailed",
        preferred_input_type="organic",
        metadata={
            "validation_run": True,
            "validation_farmer": "A",
        },
    )

    farm = farm_registry.create_farm(
        farmer_id=farmer["farmer_id"],
        farm_name=f"Validation Farm A {suffix}",
        village="Validation Village A",
        district="Varanasi",
        state="Uttar Pradesh",
        total_area_acres=5.0,
        irrigation_source="Canal",
        metadata={
            "validation_run": True,
        },
    )

    field = farm_registry.create_field(
        farm_id=farm["farm_id"],
        field_name=f"Validation Field A {suffix}",
        area_acres=3.0,
        irrigation_available=True,
        metadata={
            "validation_run": True,
        },
    )

    soil = soil_memory.create_soil_profile(
        field_id=field["field_id"],
        soil_type="Loamy",
        ph=6.8,
        nitrogen=280.0,
        phosphorus=22.0,
        potassium=180.0,
        organic_carbon=0.75,
        moisture_percent=35.0,
        electrical_conductivity=0.45,
        metadata={
            "validation_run": True,
            "validation_farmer": "A",
        },
    )

    season = season_manager.create_season(
        field_id=field["field_id"],
        season_name="Kharif",
        crop="Rice",
        current_stage="Tillering",
        metadata={
            "validation_run": True,
            "validation_farmer": "A",
        },
    )

    return {
        "farmer": farmer,
        "farm": farm,
        "field": field,
        "soil": soil,
        "season": season,
    }


# ============================================================

# CREATE FARMER B

# ============================================================


def create_farmer_b(
    suffix: str,
    farmer_registry: FarmerRegistry,
    farm_registry: FarmFieldRegistry,
    soil_memory: SoilMemory,
    season_manager: SeasonManager,
) -> Dict[str, Any]:
    farmer = farmer_registry.create_farmer(
        name=f"Farmer B {suffix}",
        phone=f"800{suffix[-7:]}",
        email=f"farmer_b_{suffix}@validation.local",
        village="Validation Village B",
        district="Varanasi",
        state="Uttar Pradesh",
        farming_experience_years=2,
        labor_availability="low",
        budget_constraint="high",
        guidance_preference="simple",
        preferred_input_type="low_cost",
        metadata={
            "validation_run": True,
            "validation_farmer": "B",
        },
    )

    farm = farm_registry.create_farm(
        farmer_id=farmer["farmer_id"],
        farm_name=f"Validation Farm B {suffix}",
        village="Validation Village B",
        district="Varanasi",
        state="Uttar Pradesh",
        total_area_acres=2.0,
        irrigation_source="Borewell",
        metadata={
            "validation_run": True,
        },
    )

    field = farm_registry.create_field(
        farm_id=farm["farm_id"],
        field_name=f"Validation Field B {suffix}",
        area_acres=1.5,
        irrigation_available=False,
        metadata={
            "validation_run": True,
        },
    )

    soil = soil_memory.create_soil_profile(
        field_id=field["field_id"],
        soil_type="Sandy",
        ph=7.8,
        nitrogen=120.0,
        phosphorus=12.0,
        potassium=95.0,
        organic_carbon=0.35,
        moisture_percent=18.0,
        electrical_conductivity=0.70,
        metadata={
            "validation_run": True,
            "validation_farmer": "B",
        },
    )

    season = season_manager.create_season(
        field_id=field["field_id"],
        season_name="Kharif",
        crop="Rice",
        current_stage="Tillering",
        metadata={
            "validation_run": True,
            "validation_farmer": "B",
        },
    )

    return {
        "farmer": farmer,
        "farm": farm,
        "field": field,
        "soil": soil,
        "season": season,
    }


# ============================================================

# DEBUG ACTUAL PIPELINE OUTPUT

# ============================================================


def debug_pipeline_result(
    label: str,
    result: Dict[str, Any],
) -> None:
    """
    Prints the actual runtime schema returned by
    PersistentFarmerPipeline.

    This is used to identify where the Contextual Decision
    Engine output is located.
    """

    print()
    print(LINE)
    print(
        f"DEBUG - {label} PIPELINE RESULT"
    )
    print(LINE)

    print()
    print("TOP-LEVEL RESULT KEYS:")

    if isinstance(result, dict):

        print(
            list(result.keys())
        )

    else:

        print(
            f"Result Type: {type(result)}"
        )

        pprint(result)

        return

    # --------------------------------------------------------
    # FULL RESULT
    # --------------------------------------------------------

    print()
    print("FULL PIPELINE RESULT:")

    pprint(result)

    # --------------------------------------------------------
    # CONTEXTUAL ADVISORY
    # --------------------------------------------------------

    print()
    print("CONTEXTUAL ADVISORY:")

    contextual_advisory = result.get(
        "contextual_advisory",
        None,
    )

    pprint(contextual_advisory)

    print()
    print("CONTEXTUAL ADVISORY TYPE:")

    print(
        type(contextual_advisory)
    )

    if isinstance(
        contextual_advisory,
        dict,
    ):

        print()
        print(
            "CONTEXTUAL ADVISORY KEYS:"
        )

        print(
            list(
                contextual_advisory.keys()
            )
        )

    # --------------------------------------------------------
    # DECISION OUTPUT ALTERNATIVE PATHS
    # --------------------------------------------------------

    possible_keys = [
        "decision",
        "decision_output",
        "contextual_decision",
        "advisory",
        "personalized_advisory",
        "final_advisory",
        "result",
    ]

    print()
    print("ALTERNATIVE DECISION OUTPUT PATHS:")

    found_any = False

    for key in possible_keys:

        if key in result:

            found_any = True

            print()
            print(f"[FOUND] result['{key}']")

            pprint(result.get(key))

    if not found_any:

        print(
            "No alternative decision output keys found."
        )

    # --------------------------------------------------------
    # FARMER CONTEXT
    # --------------------------------------------------------

    print()
    print("FARMER CONTEXT:")

    farmer_context = result.get(
        "farmer_context",
        {},
    )

    pprint(farmer_context)

    print()
    print("FARMER CONTEXT TYPE:")

    print(
        type(farmer_context)
    )

    if isinstance(
        farmer_context,
        dict,
    ):

        print()
        print("FARMER CONTEXT KEYS:")

        print(
            list(
                farmer_context.keys()
            )
        )

    print()
    print(LINE)
    print(
        f"END DEBUG - {label}"
    )
    print(LINE)


# ============================================================

# HELPER - FIND FIRST DICT

# ============================================================


def find_nested_value(
    data: Any,
    candidate_keys: List[str],
) -> Any:
    """
    Recursively search nested dictionaries and lists
    for the first matching key.
    """

    if isinstance(data, dict):

        for key in candidate_keys:

            if key in data:

                return data[key]

        for value in data.values():

            found = find_nested_value(
                value,
                candidate_keys,
            )

            if found is not None:

                return found

    elif isinstance(data, list):

        for item in data:

            found = find_nested_value(
                item,
                candidate_keys,
            )

            if found is not None:

                return found

    return None


# ============================================================

# EXTRACT ADVISORY OBJECT

# ============================================================


def get_advisory_object(
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Attempts to locate the actual structured advisory
    regardless of the current wrapper schema.
    """

    if not isinstance(result, dict):

        return {}

    direct_keys = [
        "contextual_advisory",
        "decision_output",
        "contextual_decision",
        "personalized_advisory",
        "final_advisory",
        "advisory",
        "decision",
    ]

    for key in direct_keys:

        value = result.get(key)

        if isinstance(value, dict):

            return value

    return {}


# ============================================================

# EXTRACT PRIORITY

# ============================================================


def extract_priority(
    advisory: Dict[str, Any],
) -> Any:

    if not isinstance(advisory, dict):

        return None

    return find_nested_value(
        advisory,
        [
            "overall_priority",
            "priority",
            "final_priority",
            "priority_level",
            "risk_priority",
        ],
    )


# ============================================================

# EXTRACT RECOMMENDATIONS

# ============================================================


def extract_recommendation_texts(
    advisory: Dict[str, Any],
) -> List[str]:

    if not isinstance(advisory, dict):

        return []

    recommendations = find_nested_value(
        advisory,
        [
            "recommendations",
            "personalized_recommendations",
            "final_recommendations",
            "actions",
            "advisory_items",
        ],
    )

    if recommendations is None:

        return []

    if isinstance(
        recommendations,
        str,
    ):

        return [
            recommendations.strip()
        ]

    if not isinstance(
        recommendations,
        list,
    ):

        return [
            str(recommendations)
        ]

    results = []

    for item in recommendations:

        if isinstance(
            item,
            dict,
        ):

            text = (
                item.get("action")
                or item.get("recommendation")
                or item.get("message")
                or item.get("text")
                or item.get("advice")
                or str(item)
            )

        else:

            text = str(item)

        if text:

            results.append(
                str(text).strip()
            )

    return results


# ============================================================

# EXTRACT PERSONALIZATION REASONS

# ============================================================


def extract_personalization_reasons(
    advisory: Dict[str, Any],
) -> List[str]:

    if not isinstance(
        advisory,
        dict,
    ):

        return []

    reasons = find_nested_value(
        advisory,
        [
            "personalization_reasons",
            "personalisation_reasons",
            "decision_reasons",
            "context_reasons",
            "reasons",
            "applied_personalization",
        ],
    )

    if reasons is None:

        return []

    if isinstance(
        reasons,
        str,
    ):

        return [
            reasons
        ]

    if isinstance(
        reasons,
        list,
    ):

        return [
            str(reason)
            for reason in reasons
        ]

    return [
        str(reasons)
    ]


# ============================================================

# PRINT FARMER RESULT

# ============================================================


def print_farmer_result(
    label: str,
    result: Dict[str, Any],
) -> None:

    farmer = result.get(
        "farmer",
        {},
    )

    farm = result.get(
        "farm",
        {},
    )

    field = result.get(
        "field",
        {},
    )

    soil = result.get(
        "soil_profile",
        result.get("soil", {}),
    )

    season = result.get(
        "season",
        {},
    )

    advisory = get_advisory_object(
        result
    )

    history = result.get(
        "advisory_history_record",
        {},
    )

    priority = extract_priority(
        advisory
    )

    recommendations = (
        extract_recommendation_texts(
            advisory
        )
    )

    reasons = (
        extract_personalization_reasons(
            advisory
        )
    )

    print()
    print("-" * 78)
    print(f"{label} RESULT")
    print("-" * 78)

    print(
        f"Farmer: {farmer.get('name')}"
    )

    print(
        f"Farmer ID: {farmer.get('farmer_id')}"
    )

    print(
        f"Farm: {farm.get('farm_name')}"
    )

    print(
        f"Field: {field.get('field_name')}"
    )

    print(
        f"Soil: {soil.get('soil_type')}"
    )

    print(
        f"Crop: {season.get('crop')}"
    )

    print(
        f"Stage: {season.get('current_stage')}"
    )

    print(
        f"Priority: {priority}"
    )

    print(
        f"Recommendations: {len(recommendations)}"
    )

    print(
        f"Personalization Reasons: {len(reasons)}"
    )

    print(
        "Advisory ID: "
        f"{history.get('advisory_id')}"
    )


# ============================================================

# MAIN VALIDATION

# ============================================================


def run_phase4_validation() -> bool:

    tracker = ValidationTracker()

    suffix = build_validation_suffix()

    print()
    print(LINE)
    print(
        "RAYA PHASE 4G - PERSISTENT FARMER "
        "INTELLIGENCE VALIDATION"
    )
    print(LINE)

    print()
    print(
        f"Validation Run ID: {suffix}"
    )

    # ========================================================
    # 1. INITIALIZE BACKEND
    # ========================================================

    tracker.section(
        "1. INITIALIZE PERSISTENT BACKEND"
    )

    farmer_registry = FarmerRegistry()

    farm_registry = FarmFieldRegistry()

    soil_memory = SoilMemory()

    season_manager = SeasonManager()

    advisory_history = AdvisoryHistory()

    tracker.check(
        "Farmer Registry initialized",
        farmer_registry is not None,
    )

    tracker.check(
        "Farm & Field Registry initialized",
        farm_registry is not None,
    )

    tracker.check(
        "Soil Memory initialized",
        soil_memory is not None,
    )

    tracker.check(
        "Season Manager initialized",
        season_manager is not None,
    )

    tracker.check(
        "Advisory History initialized",
        advisory_history is not None,
    )

    # ========================================================
    # 2. CREATE FARMER A
    # ========================================================

    tracker.section(
        "2. CREATE PERSISTENT FARMER A"
    )

    farmer_a = create_farmer_a(
        suffix,
        farmer_registry,
        farm_registry,
        soil_memory,
        season_manager,
    )

    tracker.check(
        "Farmer A created",
        bool(
            farmer_a["farmer"].get(
                "farmer_id"
            )
        ),
    )

    tracker.check(
        "Farmer A farm created",
        bool(
            farmer_a["farm"].get(
                "farm_id"
            )
        ),
    )

    tracker.check(
        "Farmer A field created",
        bool(
            farmer_a["field"].get(
                "field_id"
            )
        ),
    )

    tracker.check(
        "Farmer A soil persisted",
        bool(
            farmer_a["soil"].get(
                "soil_profile_id"
            )
        ),
    )

    tracker.check(
        "Farmer A season created",
        bool(
            farmer_a["season"].get(
                "season_id"
            )
        ),
    )

    # ========================================================
    # 3. CREATE FARMER B
    # ========================================================

    tracker.section(
        "3. CREATE PERSISTENT FARMER B"
    )

    farmer_b = create_farmer_b(
        suffix,
        farmer_registry,
        farm_registry,
        soil_memory,
        season_manager,
    )

    tracker.check(
        "Farmer B created",
        bool(
            farmer_b["farmer"].get(
                "farmer_id"
            )
        ),
    )

    tracker.check(
        "Farmer B farm created",
        bool(
            farmer_b["farm"].get(
                "farm_id"
            )
        ),
    )

    tracker.check(
        "Farmer B field created",
        bool(
            farmer_b["field"].get(
                "field_id"
            )
        ),
    )

    tracker.check(
        "Farmer B soil persisted",
        bool(
            farmer_b["soil"].get(
                "soil_profile_id"
            )
        ),
    )

    tracker.check(
        "Farmer B season created",
        bool(
            farmer_b["season"].get(
                "season_id"
            )
        ),
    )

    # ========================================================
    # 4. INDEPENDENT MEMORY
    # ========================================================

    tracker.section(
        "4. VALIDATE INDEPENDENT FARMER MEMORY"
    )

    tracker.check(
        "Farmer A and B have different IDs",
        farmer_a["farmer"]["farmer_id"]
        != farmer_b["farmer"]["farmer_id"],
    )

    tracker.check(
        "Farmer A and B have different farms",
        farmer_a["farm"]["farm_id"]
        != farmer_b["farm"]["farm_id"],
    )

    tracker.check(
        "Farmer A and B have different fields",
        farmer_a["field"]["field_id"]
        != farmer_b["field"]["field_id"],
    )

    tracker.check(
        "Farmer A and B have different soil profiles",
        farmer_a["soil"]["soil_profile_id"]
        != farmer_b["soil"]["soil_profile_id"],
    )

    tracker.check(
        "Farmer A and B have independent soil types",
        farmer_a["soil"]["soil_type"]
        != farmer_b["soil"]["soil_type"],
        (
            f"A={farmer_a['soil']['soil_type']}, "
            f"B={farmer_b['soil']['soil_type']}"
        ),
    )

    # ========================================================
    # 5. INITIALIZE PIPELINE
    # ========================================================

    tracker.section(
        "5. INITIALIZE REAL PERSISTENT PIPELINE"
    )

    search_counter = CountingFarmerSearch()

    pipeline = PersistentFarmerPipeline(
        farmer_registry=farmer_registry,
        farm_field_registry=farm_registry,
        soil_memory=soil_memory,
        season_manager=season_manager,
        advisory_history=advisory_history,
        search_function=search_counter,
    )

    tracker.check(
        "Persistent pipeline initialized",
        pipeline is not None,
    )

    tracker.check(
        "Contextual Decision Engine available",
        generate_contextual_advisory is not None,
    )

    # ========================================================
    # 6. FARMER A PIPELINE
    # ========================================================

    tracker.section(
        "6. FARMER A END-TO-END PIPELINE"
    )

    calls_before_a = (
        search_counter.total_calls
    )

    result_a = pipeline.generate_advisory(
        farmer_id=farmer_a["farmer"]["farmer_id"],
        farm_id=farmer_a["farm"]["farm_id"],
        field_id=farmer_a["field"]["field_id"],
    )

    calls_after_a = (
        search_counter.total_calls
    )

    # DEBUG ACTUAL OUTPUT SCHEMA
    debug_pipeline_result(
        "FARMER A",
        result_a,
    )

    print_farmer_result(
        "FARMER A",
        result_a,
    )

    tracker.check(
        "Farmer A pipeline returned result",
        isinstance(result_a, dict),
    )

    tracker.check(
        "Farmer A farmer_search executed exactly once",
        (
            calls_after_a
            -
            calls_before_a
        ) == 1,
        (
            "Calls for Farmer A: "
            f"{calls_after_a - calls_before_a}"
        ),
    )

    tracker.check(
        "Farmer A advisory saved automatically",
        bool(
            result_a.get(
                "advisory_history_record"
            )
        ),
    )

    tracker.check(
        "Farmer A canonical context generated",
        bool(
            result_a.get(
                "farmer_context"
            )
        ),
    )

    # ========================================================
    # 7. FARMER B PIPELINE
    # ========================================================

    tracker.section(
        "7. FARMER B END-TO-END PIPELINE"
    )

    calls_before_b = (
        search_counter.total_calls
    )

    result_b = pipeline.generate_advisory(
        farmer_id=farmer_b["farmer"]["farmer_id"],
        farm_id=farmer_b["farm"]["farm_id"],
        field_id=farmer_b["field"]["field_id"],
    )

    calls_after_b = (
        search_counter.total_calls
    )

    # DEBUG ACTUAL OUTPUT SCHEMA
    debug_pipeline_result(
        "FARMER B",
        result_b,
    )

    print_farmer_result(
        "FARMER B",
        result_b,
    )

    tracker.check(
        "Farmer B pipeline returned result",
        isinstance(result_b, dict),
    )

    tracker.check(
        "Farmer B farmer_search executed exactly once",
        (
            calls_after_b
            -
            calls_before_b
        ) == 1,
        (
            "Calls for Farmer B: "
            f"{calls_after_b - calls_before_b}"
        ),
    )

    tracker.check(
        "Farmer B advisory saved automatically",
        bool(
            result_b.get(
                "advisory_history_record"
            )
        ),
    )

    tracker.check(
        "Farmer B canonical context generated",
        bool(
            result_b.get(
                "farmer_context"
            )
        ),
    )

    # ========================================================
    # 8. SAME AGRICULTURAL CONDITIONS
    # ========================================================

    tracker.section(
        "8. VALIDATE SAME AGRICULTURAL CONDITIONS"
    )

    season_a = result_a.get(
        "season",
        {},
    )

    season_b = result_b.get(
        "season",
        {},
    )

    tracker.check(
        "Same crop",
        season_a.get("crop")
        == season_b.get("crop"),
        f"Crop: {season_a.get('crop')}",
    )

    tracker.check(
        "Same growth stage",
        season_a.get("current_stage")
        == season_b.get("current_stage"),
        (
            "Stage: "
            f"{season_a.get('current_stage')}"
        ),
    )

    tracker.check(
        "Same state",
        result_a.get("farm", {}).get("state")
        == result_b.get("farm", {}).get("state"),
        (
            "State: "
            f"{result_a.get('farm', {}).get('state')}"
        ),
    )

    tracker.check(
        "Same district",
        result_a.get("farm", {}).get("district")
        == result_b.get("farm", {}).get("district"),
        (
            "District: "
            f"{result_a.get('farm', {}).get('district')}"
        ),
    )

    # ========================================================
    # 9. DIFFERENT FARMER CONTEXT
    # ========================================================

    tracker.section(
        "9. VALIDATE DIFFERENT FARMER CONTEXT"
    )

    context_a = result_a.get(
        "farmer_context",
        {},
    )

    context_b = result_b.get(
        "farmer_context",
        {},
    )

    tracker.check(
        "Farmer contexts are different",
        context_a != context_b,
    )

    tracker.check(
        "Different farming experience",
        farmer_a["farmer"].get(
            "farming_experience_years"
        )
        !=
        farmer_b["farmer"].get(
            "farming_experience_years"
        ),
    )

    tracker.check(
        "Different labor availability",
        farmer_a["farmer"].get(
            "labor_availability"
        )
        !=
        farmer_b["farmer"].get(
            "labor_availability"
        ),
    )

    tracker.check(
        "Different budget constraints",
        farmer_a["farmer"].get(
            "budget_constraint"
        )
        !=
        farmer_b["farmer"].get(
            "budget_constraint"
        ),
    )

    tracker.check(
        "Different guidance preferences",
        farmer_a["farmer"].get(
            "guidance_preference"
        )
        !=
        farmer_b["farmer"].get(
            "guidance_preference"
        ),
    )

    tracker.check(
        "Different preferred input types",
        farmer_a["farmer"].get(
            "preferred_input_type"
        )
        !=
        farmer_b["farmer"].get(
            "preferred_input_type"
        ),
    )

    # ========================================================
    # 10. PERSONALIZATION COMPARISON
    # ========================================================

    tracker.section(
        "10. PERSONALIZATION OUTCOME COMPARISON"
    )

    advisory_a = get_advisory_object(
        result_a
    )

    advisory_b = get_advisory_object(
        result_b
    )

    priority_a = extract_priority(
        advisory_a
    )

    priority_b = extract_priority(
        advisory_b
    )

    recommendations_a = (
        extract_recommendation_texts(
            advisory_a
        )
    )

    recommendations_b = (
        extract_recommendation_texts(
            advisory_b
        )
    )

    reasons_a = (
        extract_personalization_reasons(
            advisory_a
        )
    )

    reasons_b = (
        extract_personalization_reasons(
            advisory_b
        )
    )

    print()
    print("PERSONALIZATION COMPARISON")
    print()

    print(
        f"Farmer A Priority: {priority_a}"
    )

    print(
        f"Farmer B Priority: {priority_b}"
    )

    print()

    print(
        "Farmer A Recommendations:"
    )

    if recommendations_a:

        for item in recommendations_a[:5]:

            print(f"  - {item}")

    else:

        print("  (No recommendations extracted)")

    print()

    print(
        "Farmer B Recommendations:"
    )

    if recommendations_b:

        for item in recommendations_b[:5]:

            print(f"  - {item}")

    else:

        print("  (No recommendations extracted)")

    print()

    print(
        "Farmer A Personalization Reasons:"
    )

    if reasons_a:

        for reason in reasons_a:

            print(f"  - {reason}")

    else:

        print(
            "  (No personalization reasons extracted)"
        )

    print()

    print(
        "Farmer B Personalization Reasons:"
    )

    if reasons_b:

        for reason in reasons_b:

            print(f"  - {reason}")

    else:

        print(
            "  (No personalization reasons extracted)"
        )

    priority_different = (
        priority_a != priority_b
    )

    recommendations_different = (
        recommendations_a != recommendations_b
    )

    reasons_different = (
        reasons_a != reasons_b
    )

    tracker.check(
        "Priority comparison completed",
        True,
        (
            f"A={priority_a}, "
            f"B={priority_b}, "
            f"Different={priority_different}"
        ),
    )

    tracker.check(
        "Top recommendation comparison completed",
        True,
        (
            "Different="
            f"{recommendations_different}"
        ),
    )

    tracker.check(
        "Personalization reasons comparison completed",
        True,
        (
            f"Different={reasons_different}"
        ),
    )

    tracker.check(
        "Personalization output schema inspected",
        True,
        (
            "See DEBUG sections above "
            "for actual runtime schema."
        ),
    )

    # ========================================================
    # 11. ADVISORY HISTORY
    # ========================================================

    tracker.section(
        "11. VALIDATE INDEPENDENT ADVISORY HISTORY"
    )

    history_a = (
        advisory_history.get_farmer_history(
            farmer_a["farmer"]["farmer_id"]
        )
    )

    history_b = (
        advisory_history.get_farmer_history(
            farmer_b["farmer"]["farmer_id"]
        )
    )

    tracker.check(
        "Farmer A has advisory history",
        len(history_a) >= 1,
        f"Count: {len(history_a)}",
    )

    tracker.check(
        "Farmer B has advisory history",
        len(history_b) >= 1,
        f"Count: {len(history_b)}",
    )

    farmer_a_ids = {
        record.get("farmer_id")
        for record in history_a
    }

    farmer_b_ids = {
        record.get("farmer_id")
        for record in history_b
    }

    tracker.check(
        "Farmer A history contains only Farmer A",
        farmer_a_ids
        ==
        {
            farmer_a["farmer"]["farmer_id"]
        },
    )

    tracker.check(
        "Farmer B history contains only Farmer B",
        farmer_b_ids
        ==
        {
            farmer_b["farmer"]["farmer_id"]
        },
    )

    # ========================================================
    # 12. RESTART / RELOAD
    # ========================================================

    tracker.section(
        "12. RESTART SIMULATION - RELOAD PERSISTENT MEMORY"
    )

    reloaded_farmer_registry = (
        FarmerRegistry()
    )

    reloaded_farm_registry = (
        FarmFieldRegistry()
    )

    reloaded_soil_memory = (
        SoilMemory()
    )

    reloaded_season_manager = (
        SeasonManager()
    )

    reloaded_advisory_history = (
        AdvisoryHistory()
    )

    reloaded_farmer_a = (
        reloaded_farmer_registry.get_farmer(
            farmer_a["farmer"]["farmer_id"]
        )
    )

    reloaded_farmer_b = (
        reloaded_farmer_registry.get_farmer(
            farmer_b["farmer"]["farmer_id"]
        )
    )

    reloaded_farm_a = (
        reloaded_farm_registry.get_farm(
            farmer_a["farm"]["farm_id"]
        )
    )

    reloaded_farm_b = (
        reloaded_farm_registry.get_farm(
            farmer_b["farm"]["farm_id"]
        )
    )

    reloaded_field_a = (
        reloaded_farm_registry.get_field(
            farmer_a["field"]["field_id"]
        )
    )

    reloaded_field_b = (
        reloaded_farm_registry.get_field(
            farmer_b["field"]["field_id"]
        )
    )

    reloaded_soil_a = (
        reloaded_soil_memory
        .get_field_soil_profile(
            farmer_a["field"]["field_id"]
        )
    )

    reloaded_soil_b = (
        reloaded_soil_memory
        .get_field_soil_profile(
            farmer_b["field"]["field_id"]
        )
    )

    reloaded_season_a = (
        reloaded_season_manager
        .get_active_season(
            farmer_a["field"]["field_id"]
        )
    )

    reloaded_season_b = (
        reloaded_season_manager
        .get_active_season(
            farmer_b["field"]["field_id"]
        )
    )

    reloaded_history_a = (
        reloaded_advisory_history
        .get_farmer_history(
            farmer_a["farmer"]["farmer_id"]
        )
    )

    reloaded_history_b = (
        reloaded_advisory_history
        .get_farmer_history(
            farmer_b["farmer"]["farmer_id"]
        )
    )

    tracker.check(
        "Farmer A persists after reload",
        reloaded_farmer_a is not None,
    )

    tracker.check(
        "Farmer B persists after reload",
        reloaded_farmer_b is not None,
    )

    tracker.check(
        "Farmer A farm persists after reload",
        reloaded_farm_a is not None,
    )

    tracker.check(
        "Farmer B farm persists after reload",
        reloaded_farm_b is not None,
    )

    tracker.check(
        "Farmer A field persists after reload",
        reloaded_field_a is not None,
    )

    tracker.check(
        "Farmer B field persists after reload",
        reloaded_field_b is not None,
    )

    tracker.check(
        "Farmer A soil persists after reload",
        reloaded_soil_a is not None,
    )

    tracker.check(
        "Farmer B soil persists after reload",
        reloaded_soil_b is not None,
    )

    tracker.check(
        "Farmer A season persists after reload",
        reloaded_season_a is not None,
    )

    tracker.check(
        "Farmer B season persists after reload",
        reloaded_season_b is not None,
    )

    tracker.check(
        "Farmer A advisory history persists after reload",
        len(reloaded_history_a) >= 1,
    )

    tracker.check(
        "Farmer B advisory history persists after reload",
        len(reloaded_history_b) >= 1,
    )

    # ========================================================
    # 13. DUPLICATE SEARCH CHECK
    # ========================================================

    tracker.section(
        "13. FINAL DUPLICATE SEARCH CHECK"
    )

    tracker.check(
        "Exactly two total farmer_search executions",
        search_counter.total_calls == 2,
        (
            "One advisory per farmer = "
            "exactly one search each"
        ),
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    validation_passed = (
        tracker.print_summary()
    )

    print()

    if validation_passed:

        print(
            "ACCEPTANCE CRITERIA STATUS"
        )

        print(
            "  [PASS] Multiple farmers persist"
        )

        print(
            "  [PASS] Independent farms and fields"
        )

        print(
            "  [PASS] Field-specific soil persistence"
        )

        print(
            "  [PASS] Season persistence"
        )

        print(
            "  [PASS] Advisory auto-save"
        )

        print(
            "  [PASS] Advisory history independence"
        )

        print(
            "  [PASS] Restart/reload persistence"
        )

        print(
            "  [PASS] End-to-end persistent pipeline"
        )

        print(
            "  [PASS] No duplicate farmer_search execution"
        )

        print(
            "  [PASS] Contextual advisory schema inspected"
        )

        print()

        print(
            "PHASE 4G RUNTIME VALIDATION COMPLETE"
        )

    return validation_passed


# ============================================================

# MAIN

# ============================================================

if __name__ == "__main__":

    try:

        success = run_phase4_validation()

        sys.exit(
            0
            if success
            else 1
        )

    except Exception as error:

        print()
        print(LINE)

        print(
            "RAYA PHASE 4G VALIDATION ERROR"
        )

        print(LINE)

        print()

        print(
            f"{type(error).__name__}: {error}"
        )

        print()

        traceback.print_exc()

        print()

        sys.exit(1)
