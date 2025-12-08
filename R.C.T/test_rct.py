# test_rct.py
from rct_core import Anchor, unix_to_rct_ns, rct_ns_to_unix, now_rct_ns, roundtrip_unix
import time
from decimal import Decimal

anchor = Anchor.default_planck2018_anchor()

def test_anchor_roundtrip():
    # the anchor time should roundtrip exactly
    unix_anchor = float(anchor.unix_anchor_ts)
    rct = unix_to_rct_ns(unix_anchor, anchor)
    assert rct == anchor.rct_anchor_ns
    unix_back = float(rct_ns_to_unix(rct, anchor))
    assert abs(unix_back - unix_anchor) < 1e-9

def test_roundtrip_random():
    t = time.time()
    rct = unix_to_rct_ns(t, anchor)
    unix_back = float(rct_ns_to_unix(rct, anchor))
    # roundtrip within 1e-6 seconds (well within ns when using ns-int)
    assert abs(unix_back - t) < 1e-3

def test_now_monotonic():
    a = now_rct_ns(anchor)
    b = now_rct_ns(anchor)
    assert b >= a
