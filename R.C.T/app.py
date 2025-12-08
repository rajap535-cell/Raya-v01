# app.py
from flask import Flask, jsonify, request, abort
from rct_core import Anchor, Anchor as AnchorClass, now_rct_ns, unix_to_rct_ns, rct_ns_to_unix, rct_ns_to_utc_datetime

app = Flask(__name__)

# Single in-memory anchor registry for demo; replace with DB table in prod.
ANCHORS = {
    AnchorClass.default_planck2018_anchor().anchor_id: AnchorClass.default_planck2018_anchor()
}

@app.route("/anchors", methods=["GET"])
def list_anchors():
    return jsonify([
        {
            "anchor_id": a.anchor_id,
            "utc_iso": a.utc_iso,
            "cosmology_version": a.cosmology_version,
            "rct_anchor_ns": str(a.rct_anchor_ns),
            "age_years": a.age_years
        } for a in ANCHORS.values()
    ])

@app.route("/rct/now", methods=["GET"])
def rct_now():
    # default use first anchor
    anchor = next(iter(ANCHORS.values()))
    rct_ns = now_rct_ns(anchor)
    return jsonify({
        "rct_ns": str(rct_ns),
        "rct_compact": f"RCT:{(rct_ns/ (10**9)):.12E}s",
        "anchor_id": anchor.anchor_id,
        "cosmology_version": anchor.cosmology_version,
        "generated_at_unix": float(request.environ.get('REQUEST_TIME', 0))
    })

@app.route("/rct/convert", methods=["POST"])
def rct_convert():
    body = request.get_json(force=True)
    if not body or "from" not in body or "value" not in body:
        abort(400, "body must contain 'from' and 'value'")
    anchor_id = body.get("anchor_id")
    anchor = ANCHORS.get(anchor_id) if anchor_id else next(iter(ANCHORS.values()))
    if body["from"] == "unix":
        unix_val = float(body["value"])
        rct_ns = unix_to_rct_ns(unix_val, anchor)
        return jsonify({"rct_ns": str(rct_ns), "anchor_id": anchor.anchor_id})
    elif body["from"] == "rct":
        rct_ns = int(body["value"])
        unix_ts = float(rct_ns_to_unix(rct_ns, anchor))
        return jsonify({"unix_ts": unix_ts, "utc": rct_ns_to_utc_datetime(rct_ns, anchor).isoformat(), "anchor_id": anchor.anchor_id})
    else:
        abort(400, "from must be 'unix' or 'rct'")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
