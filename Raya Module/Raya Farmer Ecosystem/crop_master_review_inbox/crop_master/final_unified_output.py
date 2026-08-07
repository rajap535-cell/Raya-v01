"""
RAYA — Final Unified Output Pipeline
(PRODUCTION READY — CLEAN VERSION)

Purpose
-------
Unified execution layer connecting:

• Farmer Search Engine
• Weather Intelligence
• Market Intelligence
• Crop Knowledge Engine
• Advisory Layer

Design Principles
-----------------
• Deterministic
• Structured
• Human-readable
• No ML
• No prediction logic
"""

# ---------------------------------------------------
# Imports
# ---------------------------------------------------

import json
from datetime import datetime, timezone

from farmer_search_engine import (
    farmer_search,
    farmer_view
)


# ---------------------------------------------------
# Timestamp Helper
# ---------------------------------------------------

def utc_timestamp():
    """
    Timezone-aware UTC timestamp
    """
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------
# Unified Pipeline Runner
# ---------------------------------------------------

def run_raya_pipeline(
    crop,
    stage,
    state,
    district
):
    """
    Execute complete RAYA pipeline.
    """

    try:

        packet = farmer_search(
            crop=crop,
            stage=stage,
            state=state,
            district=district
        )

        return packet

    except Exception as e:

        return {
            "status": "error",
            "message": str(e),

            "meta": {
                "generated_at": utc_timestamp(),
                "pipeline": "RAYA Unified Output Pipeline"
            }
        }


# ---------------------------------------------------
# Structured Packet Viewer
# ---------------------------------------------------

def show_structured_packet(packet):

    print("\n================================================")
    print("📦 STRUCTURED PIPELINE PACKET")
    print("================================================\n")

    print(
        json.dumps(
            packet,
            indent=2
        )
    )


# ---------------------------------------------------
# Farmer-Friendly Viewer
# ---------------------------------------------------

def show_farmer_output(packet):

    print("\n================================================")
    print("👨‍🌾 FARMER VIEW")
    print("================================================")

    farmer_view(packet)


# ---------------------------------------------------
# Unified Output Controller
# ---------------------------------------------------

def show_raya_output(packet):

    if packet.get("status") != "success":

        print("\n================================================")
        print("❌ PIPELINE ERROR")
        print("================================================\n")

        print("Message:", packet.get("message"))

        return

    # Structured Output
    show_structured_packet(packet)

    # Farmer Output
    show_farmer_output(packet)


# ---------------------------------------------------
# Main Test Harness
# ---------------------------------------------------

if __name__ == "__main__":

    print("\n🚀 Starting RAYA Unified Pipeline...\n")

    packet = run_raya_pipeline(
        crop="rice",
        stage="flowering",
        state="Karnataka",
        district="Mandya"
    )

    show_raya_output(packet)

    print("\n================================================")
    print("✅ PIPELINE EXECUTION COMPLETE")
    print("================================================\n")