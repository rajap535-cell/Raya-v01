# Phase 5 — Field Timeline & Agricultural Memory

## What changed

- `persistent_memory/field_activity_log.py` stores validated, field-scoped events.
- `persistent_memory/timeline_manager.py` returns chronological history, inclusive
  last-30/60-day windows, and deterministic temporal reasoning signals.
- `StorageManager` atomically persists `field_activity.json` alongside existing
  persistent-memory entities.
- Creating a season records one sowing event. Successfully generated advisories
  each record one linked advisory event. Both are idempotent.
- The persistent pipeline reads the current field/season timeline before calling
  the contextual decision engine. The decision engine alone turns history
  signals into prioritized, reasoned recommendations.
- The Streamlit Field Timeline page is a read-only presentation of backend
  history, with all/30-day/60-day views.

## Supported event types

`sowing`, `irrigation`, `fertilizer_application`, `heavy_rainfall`,
`disease_observation`, `harvest`, and `advisory_generated`.

Record user-observed events through `TimelineManager.add_event(...)`. Supply an
`idempotency_key` for events that may be retried; keys are scoped to the field.
Include `season_id` and structured `details` (for example
`{"nutrient": "nitrogen"}`) whenever known.

## Temporal rules

- Heavy rainfall within seven days after a fertilizer application recommends a
  nutrient-loss inspection and reports the elapsed calendar days.
- Two or more irrigation events within seven days recommend checking the recent
  soil-moisture pattern.
- A blast observation in the active season elevates blast scouting.
- Reasoning examines the last 60 days and never predicts or replaces Crop
  Master, Weather, Water, Disease, or Market outputs.

## Validation

Run the isolated storage/rule checks and same-packet advisory comparison:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_phase5_timeline
.\.venv\Scripts\python.exe -m persistent_memory.phase5_validation
```

The validation uses a temporary data directory, does not modify the application's
farmer records, records five historical events with a repeated write, verifies
restart persistence and both windows, and compares baseline vs history-aware
advisories from one identical Farmer Search packet.

## Runtime demonstration

Run the application using `streamlit run raya_farmer_interface.py`, select a
farmer and field, and open **Field Timeline**. Creating/activating a season
records sowing; generating a successful advisory records its advisory ID,
crop, stage, and priority. The timeline page reads and displays these events in
chronological order.
