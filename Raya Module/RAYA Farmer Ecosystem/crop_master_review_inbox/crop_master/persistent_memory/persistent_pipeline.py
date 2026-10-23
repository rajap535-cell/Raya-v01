"""
RAYA Phase 4E - Persistent Farmer Intelligence Pipeline

File:
persistent_memory/persistent_pipeline.py

Purpose:
Connect persistent farmer memory with the existing RAYA
agricultural intelligence pipeline.

Pipeline:

```
Farmer Registry
    ->
Farm Registry
    ->
Field Registry
    ->
Soil Memory
    ->
Season Manager
    ->
build_farmer_context()
    ->
farmer_search() [EXECUTE ONCE ONLY]
    ->
Contextual Decision Engine
    ->
Advisory History
```

Important architecture rules:
- Agricultural intelligence is NOT duplicated.
- farmer_search() executes exactly once per advisory request.
- Streamlit does not contain business logic.
- Canonical farmer_context schema is used.
- Persistent modules provide historical context.
- Every generated advisory is automatically saved.

This module does NOT modify:
- Crop Master
- Weather Intelligence
- Water Intelligence
- Disease Intelligence
- Market Intelligence
- Agricultural rule logic
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

# ============================================================

# PERSISTENT MEMORY IMPORTS

# ============================================================

from persistent_memory.farmer_registry import (
    FarmerRegistry,
    get_farmer_registry,
)

from persistent_memory.farm_field_registry import (
    FarmFieldRegistry,
    get_farm_field_registry,
)

from persistent_memory.soil_memory import (
    SoilMemory,
    get_soil_memory,
)

from persistent_memory.season_manager import (
    SeasonManager,
    get_season_manager,
)

from persistent_memory.advisory_history import (
    AdvisoryHistory,
    get_advisory_history,
)
from persistent_memory.field_activity_log import (
    EVENT_ADVISORY_GENERATED,
)
from persistent_memory.timeline_manager import (
    TimelineManager,
    get_timeline_manager,
)

# ============================================================

# OPTIONAL EXISTING RAYA IMPORTS

# ============================================================

try:
    from farmer_context import build_farmer_context
except ImportError:
    build_farmer_context = None

try:
    from farmer_search_engine import farmer_search
except ImportError:
    farmer_search = None

try:
    from contextual_decision_engine import (
        generate_contextual_advisory,
    )
except ImportError:
    generate_contextual_advisory = None

# ============================================================

# PERSISTENT PIPELINE

# ============================================================

class PersistentFarmerPipeline:
    """
    Full RAYA persistent intelligence orchestrator.

    ```

    Main usage:

        pipeline = PersistentFarmerPipeline()

        result = pipeline.generate_advisory(
            farmer_id="...",
            farm_id="...",
            field_id="..."
        )

    farmer_search is executed only once.

    The resulting agricultural packet is passed directly to the
    Contextual Decision Engine.
    """

    def __init__(
        self,
        farmer_registry: Optional[FarmerRegistry] = None,
        farm_field_registry: Optional[
            FarmFieldRegistry
        ] = None,
        soil_memory: Optional[SoilMemory] = None,
        season_manager: Optional[
            SeasonManager
        ] = None,
        advisory_history: Optional[
            AdvisoryHistory
        ] = None,
        timeline_manager: Optional[TimelineManager] = None,
        search_function: Optional[
            Callable[..., Dict[str, Any]]
        ] = None,
        decision_engine: Optional[Any] = None,
    ):
        """
        Initialize persistent pipeline.

        Dependency injection is supported so the pipeline can be
        tested without modifying the production modules.
        """

        self.farmer_registry = (
            farmer_registry
            if farmer_registry is not None
            else get_farmer_registry()
        )

        self.farm_field_registry = (
            farm_field_registry
            if farm_field_registry is not None
            else get_farm_field_registry()
        )

        self.soil_memory = (
            soil_memory
            if soil_memory is not None
            else get_soil_memory()
        )

        self.season_manager = (
            season_manager
            if season_manager is not None
            else get_season_manager()
        )

        self.advisory_history = (
            advisory_history
            if advisory_history is not None
            else get_advisory_history()
        )

        self.timeline_manager = (
            timeline_manager
            if timeline_manager is not None
            else get_timeline_manager()
        )

        self.search_function = (
            search_function
            if search_function is not None
            else farmer_search
        )

        if decision_engine is not None:
            self.decision_engine = decision_engine

        elif generate_contextual_advisory is not None:
            self.decision_engine = generate_contextual_advisory

        else:
            self.decision_engine = None

    # ========================================================
    # MAIN PIPELINE
    # ========================================================

    def generate_advisory(
        self,
        farmer_id: str,
        farm_id: str,
        field_id: str,
    ) -> Dict[str, Any]:
        """
        Generate one complete persistent advisory.

        Pipeline:

            Load Farmer
                ->
            Load Farm
                ->
            Load Field
                ->
            Load Soil
                ->
            Load Active Season
                ->
            Build Canonical Farmer Context
                ->
            Farmer Search [ONCE]
                ->
            Contextual Decision Engine
                ->
            Save Advisory History
                ->
            Return Complete Result
        """

        # ----------------------------------------------------
        # 1. LOAD FARMER
        # ----------------------------------------------------

        farmer = self._load_farmer(
            farmer_id
        )

        # ----------------------------------------------------
        # 2. LOAD FARM
        # ----------------------------------------------------

        farm = self._load_farm(
            farm_id=farm_id,
            farmer_id=farmer_id,
        )

        # ----------------------------------------------------
        # 3. LOAD FIELD
        # ----------------------------------------------------

        field = self._load_field(
            field_id=field_id,
            farm_id=farm_id,
            farmer_id=farmer_id,
        )

        # ----------------------------------------------------
        # 4. LOAD PERSISTENT SOIL
        # ----------------------------------------------------

        soil_profile = (
            self._load_soil_profile(
                field_id
            )
        )

        # ----------------------------------------------------
        # 5. LOAD ACTIVE SEASON
        # ----------------------------------------------------

        active_season = (
            self.season_manager.get_active_season(
                field_id
            )
        )

        if active_season is None:
            raise ValueError(
                "No active season found for field: "
                f"{field_id}. "
                "Create an active season before "
                "generating advisory."
            )

        # ----------------------------------------------------
        # 6. BUILD CANONICAL FARMER CONTEXT
        # ----------------------------------------------------

        farmer_context = (
            self._build_canonical_farmer_context(
                farmer=farmer,
                farm=farm,
                field=field,
                soil_profile=soil_profile,
                active_season=active_season,
            )
        )

        if farmer_context is None:
            raise RuntimeError(
                "Could not build canonical farmer context; "
                "refusing to generate an unpersonalized advisory."
            )

        # ----------------------------------------------------
        # 7. BUILD SEARCH PARAMETERS
        # ----------------------------------------------------

        search_parameters = (
            self._build_search_parameters(
                farmer=farmer,
                farm=farm,
                field=field,
                active_season=active_season,
            )
        )

        # ----------------------------------------------------
        # 8. EXECUTE FARMER SEARCH EXACTLY ONCE
        # ----------------------------------------------------

        agricultural_packet = (
            self._execute_farmer_search_once(
                search_parameters
            )
        )

        timeline_context = (
            self.timeline_manager.build_reasoning_context(
                field_id=field_id,
                season_id=active_season.get("season_id"),
            )
        )

        # ----------------------------------------------------
        # 9. CONTEXTUAL DECISION ENGINE
        # ----------------------------------------------------

        contextual_advisory = (
            self._generate_contextual_advisory(
                agricultural_packet=(
                    agricultural_packet
                ),
                farmer_context=farmer_context,
                timeline_context=timeline_context,
            )
        )

        if contextual_advisory.get("status") != "success":
            raise RuntimeError(
                "Contextual Decision Engine failed to generate "
                "an advisory: "
                f"{contextual_advisory.get('message', 'unknown error')}"
            )

        # ----------------------------------------------------
        # 10. SAVE ADVISORY HISTORY
        # ----------------------------------------------------

        history_record = (
            self.advisory_history.save_advisory(
                farmer_id=farmer_id,
                farm_id=farm_id,
                field_id=field_id,
                season_id=active_season.get(
                    "season_id"
                ),
                agricultural_packet=(
                    agricultural_packet
                ),
                contextual_advisory=(
                    contextual_advisory
                ),
            )
        )

        timeline_event = self.timeline_manager.add_event(
            field_id=field_id,
            event_type=EVENT_ADVISORY_GENERATED,
            title=(
                f"Advisory generated for "
                f"{active_season.get('crop')} "
                f"({active_season.get('current_stage')})"
            ),
            occurred_at=history_record["created_at"],
            season_id=active_season.get("season_id"),
            idempotency_key=(
                f"advisory:{history_record['advisory_id']}"
            ),
            details={
                "advisory_id": history_record["advisory_id"],
                "crop": history_record["crop"],
                "stage": history_record["stage"],
                "priority": history_record["overall_priority"],
            },
        )

        # ----------------------------------------------------
        # 11. COMPLETE RESULT
        # ----------------------------------------------------

        return {
            "farmer": farmer,
            "farm": farm,
            "field": field,
            "soil_profile": soil_profile,
            "season": active_season,
            "farmer_context": farmer_context,
            "agricultural_packet": (
                agricultural_packet
            ),
            "contextual_advisory": (
                contextual_advisory
            ),
            "advisory_history_record": (
                history_record
            ),
            "timeline_context": timeline_context,
            "timeline_event": timeline_event,
        }

    # ========================================================
    # LOAD FARMER
    # ========================================================

    def _load_farmer(
        self,
        farmer_id: str,
    ) -> Dict[str, Any]:

        farmer = (
            self.farmer_registry.get_farmer(
                farmer_id
            )
        )

        if farmer is None:
            raise ValueError(
                f"Farmer not found: {farmer_id}"
            )

        return farmer

    # ========================================================
    # LOAD FARM
    # ========================================================

    def _load_farm(
        self,
        farm_id: str,
        farmer_id: str,
    ) -> Dict[str, Any]:

        farm = (
            self.farm_field_registry.get_farm(
                farm_id=farm_id
            )
        )

        if farm is None:
            raise ValueError(
                f"Farm not found: {farm_id}"
            )

        if (
            farm.get("farmer_id")
            != farmer_id
        ):
            raise ValueError(
                "Farm does not belong to "
                "the requested farmer."
            )

        return farm

    # ========================================================
    # LOAD FIELD
    # ========================================================

    def _load_field(
        self,
        field_id: str,
        farm_id: str,
        farmer_id: str,
    ) -> Dict[str, Any]:

        field = (
            self.farm_field_registry.get_field(
                field_id=field_id
            )
        )

        if field is None:
            raise ValueError(
                f"Field not found: {field_id}"
            )

        if (
            field.get("farm_id")
            != farm_id
        ):
            raise ValueError(
                "Field does not belong to "
                "the requested farm."
            )

        if (
            field.get("farmer_id")
            != farmer_id
        ):
            raise ValueError(
                "Field does not belong to "
                "the requested farmer."
            )

        return field

    # ========================================================
    # LOAD SOIL
    # ========================================================

    def _load_soil_profile(
        self,
        field_id: str,
    ) -> Dict[str, Any]:

        soil_profile = (
            self.soil_memory.get_field_soil_profile(
                field_id
            )
        )

        if soil_profile is None:
            return {}

        return soil_profile

    # ========================================================
    # BUILD CANONICAL FARMER CONTEXT
    # ========================================================

    def _build_canonical_farmer_context(
        self,
        farmer: Dict[str, Any],
        farm: Dict[str, Any],
        field: Dict[str, Any],
        soil_profile: Dict[str, Any],
        active_season: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build the canonical Farmer Context.

        This method intentionally delegates to the existing
        build_farmer_context() implementation.

        Persistent data is supplied as the source.

        No second context schema is created.
        """

        if build_farmer_context is None:
            raise ImportError(
                "Could not import build_farmer_context "
                "from farmer_context.py"
            )

        # ----------------------------------------------------
        # Extract persistent farmer profile
        # ----------------------------------------------------

        farmer_profile = dict(
            farmer.get(
                "profile",
                farmer,
            )
        )

        # ----------------------------------------------------
        # Persistent farm profile
        # ----------------------------------------------------

        farm_profile = dict(farm)

        # ----------------------------------------------------
        # Persistent field profile
        # ----------------------------------------------------

        field_profile = dict(field)

        # ----------------------------------------------------
        # Persistent soil profile
        # ----------------------------------------------------

        soil_data = dict(
            soil_profile
            if soil_profile
            else {}
        )

        # ----------------------------------------------------
        # Season profile
        # ----------------------------------------------------

        season_profile = {
            "season_name": (
                active_season.get(
                    "season_name"
                )
            ),
            "crop": active_season.get(
                "crop"
            ),
            "stage": active_season.get(
                "current_stage"
            ),
        }

        # ----------------------------------------------------
        # Flexible compatibility adapter
        #
        # The existing build_farmer_context signature may differ
        # depending on the Phase 3B implementation.
        # ----------------------------------------------------

        try:

            context = build_farmer_context(
                farmer_profile=farmer_profile,
                farm_profile=farm_profile,
                soil_profile=soil_data,
                field_profile=field_profile,
                season_profile=season_profile,
            )

        except TypeError:

            try:

                context = build_farmer_context(
                    farmer=farmer_profile,
                    farm=farm_profile,
                    soil=soil_data,
                    field=field_profile,
                    season=season_profile,
                )

            except TypeError:

                try:

                    context = build_farmer_context(
                        farmer_profile,
                        farm_profile,
                        soil_data,
                    )

                except TypeError as error:

                    raise RuntimeError(
                        "Unable to call "
                        "build_farmer_context(). "
                        "Update the integration adapter "
                        "to match the exact signature in "
                        "farmer_context.py."
                    ) from error

        if not isinstance(context, dict):
            raise RuntimeError(
                "build_farmer_context() must return "
                "a dictionary."
            )

        # ----------------------------------------------------
        # Attach persistent references
        # ----------------------------------------------------

        context["persistent_context"] = {
            "farmer_id": farmer.get(
                "farmer_id"
            ),
            "farm_id": farm.get(
                "farm_id"
            ),
            "field_id": field.get(
                "field_id"
            ),
            "season_id": active_season.get(
                "season_id"
            ),
        }

        return context

    # ========================================================
    # BUILD SEARCH PARAMETERS
    # ========================================================

    def _build_search_parameters(
        self,
        farmer: Dict[str, Any],
        farm: Dict[str, Any],
        field: Dict[str, Any],
        active_season: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build parameters required by farmer_search().

        Search context comes from persistent records.
        """

        state = self._first_available(
            field.get("state"),
            farm.get("state"),
            farmer.get("state"),
            farmer.get("location", {}).get("state")
            if isinstance(
                farmer.get("location"),
                dict,
            )
            else None,
        )

        district = self._first_available(
            field.get("district"),
            farm.get("district"),
            farmer.get("district"),
            farmer.get("location", {}).get(
                "district"
            )
            if isinstance(
                farmer.get("location"),
                dict,
            )
            else None,
        )

        crop = active_season.get("crop")

        stage = active_season.get(
            "current_stage"
        )

        missing = []

        if not state:
            missing.append("state")

        if not district:
            missing.append("district")

        if not crop:
            missing.append("crop")

        if not stage:
            missing.append("stage")

        if missing:
            raise ValueError(
                "Missing Farmer Search parameters: "
                + ", ".join(missing)
            )

        return {
            "state": state,
            "district": district,
            "crop": crop,
            "stage": stage,
        }

    # ========================================================
    # EXECUTE FARMER SEARCH ONCE
    # ========================================================

    def _execute_farmer_search_once(
        self,
        search_parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute Farmer Search exactly one time.

        The returned packet is reused by the
        Contextual Decision Engine.

        IMPORTANT:
            Do not call farmer_search anywhere else
            inside this pipeline.
        """

        if self.search_function is None:
            raise ImportError(
                "Could not import farmer_search "
                "from farmer_search_engine.py"
            )

        result = self.search_function(
            state=search_parameters["state"],
            district=search_parameters[
                "district"
            ],
            crop=search_parameters["crop"],
            stage=search_parameters["stage"],
        )

        if not isinstance(result, dict):
            raise RuntimeError(
                "farmer_search() must return "
                "a dictionary."
            )

        return result

    # ========================================================
    # GENERATE CONTEXTUAL ADVISORY
    # ========================================================

    def _generate_contextual_advisory(
        self,
        agricultural_packet: Dict[str, Any],
        farmer_context: Dict[str, Any],
        timeline_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send existing Farmer Search result to the
        Contextual Decision Engine.

        No additional Farmer Search execution occurs here.
        """

        if self.decision_engine is None:
            raise ImportError(
                "Could not initialize "
                "generate_contextual_advisory function."
            )

        # Extract required parameters from available context
        crop = (
            agricultural_packet.get("crop")
            or farmer_context.get("crop")
        )
        location = agricultural_packet.get(
            "location"
        )
        if not isinstance(location, dict):
            location = {}

        stage = (
            agricultural_packet.get("stage")
            or agricultural_packet.get("current_stage")
            or farmer_context.get("stage")
        )
        state = (
            agricultural_packet.get("state")
            or location.get("state")
            or farmer_context.get("state")
        )
        district = (
            agricultural_packet.get("district")
            or location.get("district")
            or farmer_context.get("district")
        )

        result = self.decision_engine(
            crop=crop,
            stage=stage,
            state=state,
            district=district,
            farmer_context=farmer_context,
            agricultural_packet=agricultural_packet,
            timeline_context=timeline_context,
        )

        if not isinstance(result, dict):
            raise RuntimeError(
                "Contextual Decision Engine must "
                "return a dictionary."
            )

        return result

    # ========================================================
    # HELPER
    # ========================================================

    @staticmethod
    def _first_available(
        *values: Any,
    ) -> Optional[Any]:
        """
        Return first non-empty value.
        """

        for value in values:

            if value is None:
                continue

            if isinstance(value, str):
                value = value.strip()

                if not value:
                    continue

            return value

        return None


# ============================================================

# SINGLETON ACCESSOR

# ============================================================

_default_persistent_pipeline: Optional[
    PersistentFarmerPipeline
] = None

def get_persistent_pipeline() -> (
    PersistentFarmerPipeline
):
    """
    Return default persistent pipeline instance.
    """

    global _default_persistent_pipeline

    if _default_persistent_pipeline is None:

        _default_persistent_pipeline = (
            PersistentFarmerPipeline()
        )

    return _default_persistent_pipeline


# ============================================================

# PHASE 4E RUNTIME VALIDATION

# ============================================================

def _run_local_test() -> None:
    """
    Basic integration validation.

    This validation checks persistent records and
    verifies pipeline wiring.

    For complete production validation, use actual
    registered farmer/farm/field records with an
    active season.
    """

    print("=" * 70)
    print(
        "RAYA PHASE 4E - PERSISTENT PIPELINE TEST"
    )
    print("=" * 70)

    pipeline = PersistentFarmerPipeline()

    print()
    print("Checking persistent registries...")

    farmers = (
        pipeline.farmer_registry.list_farmers()
    )

    if not farmers:

        print()
        print(
            "No persistent farmers found."
        )

        print(
            "Run farmer_registry.py validation "
            "and create a farmer first."
        )

        return

    farmer = farmers[0]

    farmer_id = farmer.get("farmer_id")

    print(
        f"Farmer found: {farmer_id}"
    )

    farms = (
        pipeline.farm_field_registry
        .get_farmer_farms(
            farmer_id
        )
    )

    if not farms:

        print(
            "No farms found for farmer."
        )

        return

    farm = farms[0]

    farm_id = farm.get("farm_id")

    print(
        f"Farm found: {farm_id}"
    )

    fields = (
        pipeline.farm_field_registry
        .get_farm_fields(
            farm_id
        )
    )

    if not fields:

        print(
            "No fields found for farm."
        )

        return

    field = fields[0]

    field_id = field.get("field_id")

    print(
        f"Field found: {field_id}"
    )

    active_season = (
        pipeline.season_manager
        .get_active_season(
            field_id
        )
    )

    if active_season is None:

        print()
        print(
            "No active season found."
        )

        print(
            "Create an active season before "
            "running full pipeline validation."
        )

        return

    print(
        f"Active Crop: "
        f"{active_season.get('crop')}"
    )

    print(
        f"Current Stage: "
        f"{active_season.get('current_stage')}"
    )

    print()
    print(
        "Generating persistent advisory..."
    )

    try:

        result = pipeline.generate_advisory(
            farmer_id=farmer_id,
            farm_id=farm_id,
            field_id=field_id,
        )

    except Exception as error:

        print()
        print(
            "PIPELINE VALIDATION FAILED"
        )

        print(
            f"{type(error).__name__}: {error}"
        )

        print()
        print(
            "Check the exact signatures of:"
        )

        print(
            "- build_farmer_context()"
        )

        print(
            "- farmer_search()"
        )

        print(
            "- ContextualDecisionEngine"
        )

        return

    print()
    print("=" * 70)
    print(
        "PHASE 4E VALIDATION REPORT"
    )
    print("=" * 70)

    print(
        "[PASS] Persistent farmer loaded"
    )

    print(
        "[PASS] Persistent farm loaded"
    )

    print(
        "[PASS] Persistent field loaded"
    )

    print(
        "[PASS] Persistent soil loaded"
    )

    print(
        "[PASS] Active season loaded"
    )

    print(
        "[PASS] Canonical farmer context built"
    )

    print(
        "[PASS] Farmer Search executed"
    )

    print(
        "[PASS] Contextual advisory generated"
    )

    print(
        "[PASS] Advisory automatically saved"
    )

    print()

    history_record = result.get(
        "advisory_history_record",
        {}
    )

    print(
        "Advisory ID: "
        f"{history_record.get('advisory_id')}"
    )

    print(
        "Overall Priority: "
        f"{history_record.get('overall_priority')}"
    )

    print()

    print(
        "PHASE 4E - PERSISTENT PIPELINE COMPLETE"
    )

    print("=" * 70)


# ============================================================

# MAIN

# ============================================================

if __name__ == "__main__":
    _run_local_test()
