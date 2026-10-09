#!/usr/bin/env python3
import json
import sys
import fcntl
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

project = Path(__file__).resolve().parent.parent

if len(sys.argv) != 3:
    raise SystemExit(
        'Usage: python3 scripts/incident-note.py INCIDENT_ID "Your note"'
    )

incident_id, note = sys.argv[1:]
if not incident_id.startswith("INC-") or any(
    char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-"
    for char in incident_id
):
    raise SystemExit("Invalid incident ID.")

incident_dir = project / "reports" / "incidents"
known = (incident_dir / f"{incident_id}.json").exists()
active = incident_dir / "active.json"

if active.exists():
    with active.open() as source:
        known = known or json.load(source).get("id") == incident_id

if not known:
    raise SystemExit("Incident not found.")

notes_dir = project / "reports" / "notes"
notes_dir.mkdir(parents=True, exist_ok=True)
output = notes_dir / f"{incident_id}-notes.md"

timestamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime(
    "%d %b %Y, %H:%M:%S IST"
)
note = " ".join(note.split())
if not note:
    raise SystemExit("Note cannot be empty.")

with output.open("a+") as target:
    fcntl.flock(target, fcntl.LOCK_EX)
    target.seek(0, 2)
    if target.tell() == 0:
        target.write(f"# Investigation notes — {incident_id}\n\n")
    target.write(f"- **{timestamp}** — {note}\n")

print(f"Note added: {output}")
