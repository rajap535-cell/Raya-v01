from dataclasses import dataclass

# Planck 2018 age of universe (UTC-based)
AGE_OF_UNIVERSE_YEARS = 13.787e9
SECONDS_PER_YEAR = 365.25 * 24 * 3600
AGE_UNIX_SECONDS = AGE_OF_UNIVERSE_YEARS * SECONDS_PER_YEAR

# Convert to nanoseconds
AGE_UNIX_NS = int(AGE_UNIX_SECONDS * 1e9)


@dataclass
class Anchor:
    rct_anchor_ns: int
    unix_anchor_ts: float
    name: str = "planck2018"


def default_planck2018_anchor():
    return Anchor(
        rct_anchor_ns=AGE_UNIX_NS,
        unix_anchor_ts=0.0,   # unix epoch start
        name="Planck2018"
    )


anchor = default_planck2018_anchor()


def unix_to_rct_ns(unix_ts: float, anchor: Anchor = anchor) -> int:
    return anchor.rct_anchor_ns + int(unix_ts * 1e9)


def rct_ns_to_unix(rct_ns: int, anchor: Anchor = anchor) -> float:
    return (rct_ns - anchor.rct_anchor_ns) / 1e9
