# rct_core.py
"""
RCT core library: anchors, conversions, formatting.
Uses Decimal for safe arithmetic, stores RCT as integer nanoseconds.
"""

from decimal import Decimal, getcontext
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import time
import uuid

# Precision enough for ns-level arithmetic
getcontext().prec = 50

NS_PER_S = Decimal('1e9')
DAYS_PER_YEAR = Decimal('365.2425')

@dataclass(frozen=True)
class Anchor:
    anchor_id: str
    rct_anchor_ns: int               # integer nanoseconds since Big Bang
    unix_anchor_ts: Decimal          # seconds since 1970-01-01T00:00:00Z
    utc_iso: str
    cosmology_version: str
    age_years: str
    notes: str = ''

    @staticmethod
    def default_planck2018_anchor():
        # Pre-computed anchor values (Planck2018 example)
        return Anchor(
            anchor_id=str(uuid.UUID('11111111-2222-3333-4444-555555555555')),
            rct_anchor_ns=int("435391266744000000000000000"),
            unix_anchor_ts=Decimal('1762819200.0'),  # 2025-11-11T00:00:00Z
            utc_iso="2025-11-11T00:00:00Z",
            cosmology_version="Planck2018-v1",
            age_years="13.797e9",
            notes="Seed Planck2018-v1 anchor computed from age_years*365.2425*86400*1e9"
        )

def now_unix_decimal() -> Decimal:
    """Return current Unix time as Decimal seconds (high precision)."""
    return Decimal(str(time.time()))

def now_rct_ns(anchor: Anchor) -> int:
    """Compute current RCT in integer nanoseconds."""
    now_unix = now_unix_decimal()
    delta_s = now_unix - anchor.unix_anchor_ts
    delta_ns = (delta_s * NS_PER_S).to_integral_value()  # quantize to integer
    return anchor.rct_anchor_ns + int(delta_ns)

def unix_to_rct_ns(unix_ts: float, anchor: Anchor) -> int:
    """Convert unix seconds (float or Decimal-able) to rct ns."""
    delta_s = Decimal(str(unix_ts)) - anchor.unix_anchor_ts
    delta_ns = (delta_s * NS_PER_S).to_integral_value()
    return anchor.rct_anchor_ns + int(delta_ns)

def rct_ns_to_unix(rct_ns: int, anchor: Anchor) -> Decimal:
    """Convert rct ns integer to unix seconds (Decimal)."""
    delta_ns = Decimal(str(rct_ns - anchor.rct_anchor_ns))
    delta_s = (delta_ns / NS_PER_S)
    return anchor.unix_anchor_ts + delta_s

def rct_ns_to_utc_datetime(rct_ns: int, anchor: Anchor) -> datetime:
    """Return a datetime (UTC) from rct_ns using anchor."""
    unix_ts = float(rct_ns_to_unix(rct_ns, anchor))
    return datetime.fromtimestamp(unix_ts, tz=timezone.utc)

def utc_datetime_to_rct_ns(dt: datetime, anchor: Anchor) -> int:
    """Convert timezone-aware UTC datetime to rct ns."""
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware (UTC).")
    unix_ts = dt.timestamp()
    return unix_to_rct_ns(unix_ts, anchor)

# Formatting helpers
def format_rct_compact(rct_ns: int) -> str:
    """Human-friendly compact format: 'RCT:4.35391266744e17s' (seconds display)."""
    rct_s = Decimal(rct_ns) / NS_PER_S
    return f"RCT:{rct_s:.12E}s"

def format_cosmic_years(rct_ns: int) -> str:
    """Return cosmic years (approx, Decimal) with 3 decimal Gyr."""
    rct_s = Decimal(rct_ns) / NS_PER_S
    years = rct_s / (DAYS_PER_YEAR * Decimal('86400'))
    return f"{years:.6E} years"

# Simple roundtrip test helper
def roundtrip_unix(unix_ts: float, anchor: Anchor) -> float:
    rct = unix_to_rct_ns(unix_ts, anchor)
    return float(rct_ns_to_unix(rct, anchor))

# Example CLI usage
if __name__ == "__main__":
    anchor = Anchor.default_planck2018_anchor()
    print("Anchor:", anchor)
    now_rct = now_rct_ns(anchor)
    print("Now RCT (ns):", now_rct)
    print("Now RCT compact:", format_rct_compact(now_rct))
    print("Now UTC from RCT:", rct_ns_to_utc_datetime(now_rct, anchor).isoformat())
