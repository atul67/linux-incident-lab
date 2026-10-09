#!/usr/bin/env python3
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

project = Path(__file__).resolve().parent.parent
incident_dir = project / "reports" / "incidents"
incident_dir.mkdir(parents=True, exist_ok=True)
active_file = incident_dir / "active.json"

state = sys.argv[1]
failures = sys.argv[2:]
now = datetime.now(timezone.utc)

def save(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    os.replace(temporary, path)

if state == "UNHEALTHY":
    if active_file.exists():
        incident = json.loads(active_file.read_text())
        incident["last_observed_at"] = now.isoformat()
        incident["current_failures"] = failures
        save(active_file, incident)
        print(f"Incident remains OPEN: {incident['id']}")
    else:
        incident = {
            "id": f"INC-{now:%Y%m%d-%H%M%S}-{uuid4().hex[:6]}",
            "service": "Linux Employee Portal Lab",
            "status": "OPEN",
            "detected_at": now.isoformat(),
            "last_observed_at": now.isoformat(),
            "initial_failures": failures,
            "current_failures": failures,
            "root_cause": "Not determined",
            "priority": "Pending impact assessment"
        }
        save(active_file, incident)
        print(f"Incident OPENED: {incident['id']}")

elif state == "HEALTHY":
    if active_file.exists():
        incident = json.loads(active_file.read_text())
        detected = datetime.fromisoformat(incident["detected_at"])
        incident["status"] = "RESOLVED"
        incident["recovery_detected_at"] = now.isoformat()
        incident["detected_resolution_seconds"] = round(
            (now - detected).total_seconds()
        )
        incident["current_failures"] = []
        save(incident_dir / f"{incident['id']}.json", incident)
        active_file.unlink()
        print(f"Incident RESOLVED: {incident['id']}")
    else:
        print("No open incident; service is healthy.")
else:
    raise SystemExit("Expected HEALTHY or UNHEALTHY")
