import json
import sys
from jsonschema import validate, ValidationError


REQUIRED_LAYERS = [
    "crop_identity",
    "growth_lifecycle",
    "climate_interactions",
    "diseases",
    "risk_impact_map",
    "harvest_logic",
    "market_impact",
    "stage_risk_summary"
]


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")


def validate_schema(crop_data, schema):
    try:
        validate(instance=crop_data, schema=schema)
        return True, "Schema validation passed"
    except ValidationError as e:
        return False, f"Schema validation failed: {e.message}"


def validate_required_layers(crop_data):
    missing = [layer for layer in REQUIRED_LAYERS if layer not in crop_data]
    if missing:
        return False, f"Missing required layers: {missing}"
    return True, "All required layers present"


def validate_growth_stages(crop_data):
    stages = crop_data["growth_lifecycle"].get("stages", {})
    if not stages:
        return False, "No growth stages defined"
    return True, "Growth stages validated"


def validate_disease_stage_relevance(crop_data):
    stages = set(crop_data["growth_lifecycle"]["stages"].keys())

    for disease in crop_data["diseases"]:
        for stage in disease["affected_stages"]:
            if stage not in stages:
                return (
                    False,
                    f"Disease '{disease['name']}' references invalid stage '{stage}'"
                )
    return True, "Disease stage relevance validated"


def validate_climate_stage_mapping(crop_data):
    stages = set(crop_data["growth_lifecycle"]["stages"].keys())

    for stage in crop_data["climate_interactions"].keys():
        if stage not in stages:
            return False, f"Climate interaction defined for invalid stage '{stage}'"
    return True, "Climate interactions validated"


def validate_risk_impact_mapping(crop_data):
    stages = set(crop_data["growth_lifecycle"]["stages"].keys())

    for stage in crop_data["risk_impact_map"].keys():
        if stage not in stages:
            return False, f"Risk impact defined for invalid stage '{stage}'"
    return True, "Risk–impact mappings validated"


def run_full_validation(crop_file, schema_file):
    crop_data = load_json(crop_file)
    schema = load_json(schema_file)

    checks = [
        validate_schema(crop_data, schema),
        validate_required_layers(crop_data),
        validate_growth_stages(crop_data),
        validate_disease_stage_relevance(crop_data),
        validate_climate_stage_mapping(crop_data),
        validate_risk_impact_mapping(crop_data)
    ]

    for success, message in checks:
        if not success:
            print("❌ VALIDATION FAILED")
            print("   →", message)
            return

    print("✅ Crop Master validation PASSED — Phase-1 compliant")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python utils/validator.py <crop_file> <schema_file>")
        sys.exit(1)

    crop_file = sys.argv[1]
    schema_file = sys.argv[2]

    run_full_validation(crop_file, schema_file)
