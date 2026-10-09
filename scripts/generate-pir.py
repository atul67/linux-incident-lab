#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

project = Path(__file__).resolve().parent.parent
incident_dir = project / "reports" / "incidents"
output_dir = project / "reports" / "pir"
output_dir.mkdir(parents=True, exist_ok=True)

resolved = []
for path in incident_dir.glob("*.json"):
    incident = json.loads(path.read_text())
    if incident.get("status") == "RESOLVED":
        resolved.append(incident)

if not resolved:
    raise SystemExit("No resolved incidents found.")

incident = max(resolved, key=lambda item: item["detected_at"])

def india_time(value):
    return datetime.fromisoformat(value).astimezone(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%d %b %Y, %H:%M:%S IST")

symptoms = "\n".join(
    f"- {value}" for value in incident.get("initial_failures", [])
)
detected = india_time(incident["detected_at"])
recovered = india_time(incident["recovery_detected_at"])

report = f"""# Post-Incident Review — {incident['id']}

Personal lab simulation | Draft requiring human review

## Summary
- Service: {incident['service']}
- Monitoring status: {incident['status']}
- Priority: {incident.get('priority', 'Pending assessment')}
- Detected resolution time: {incident['detected_resolution_seconds']} seconds

## Recorded symptoms
{symptoms}

## Business impact
Not recorded. Document the simulated user impact and affected functionality.
Do not claim an actual customer or financial impact.

## Recorded timeline
| Time | Event |
|---|---|
| {detected} | Monitoring detected failed health checks; incident opened |
| {recovered} | All configured health checks passed; incident resolved |

Investigation and recovery-action timestamps were not recorded by the tracker.

## Root cause
{incident.get('root_cause', 'Not determined')}.
Add the verified cause and supporting evidence after investigation.

## Recovery action
Not recorded by the tracker. Add the actual command or action performed.

## Recovery validation
The tracker recorded HEALTHY after the configured checks passed:
Nginx active, homepage HTTP 200, disk below threshold,
available memory above threshold, and health endpoint PORTAL_OK.

## Corrective actions
| Action | Owner | Due date | Status |
|---|---|---|---|
| Document verified cause and recovery action | Atul | TBD | Open |
| Review the recovery runbook | Atul | TBD | Open |
| Capture investigation timestamps in the next test | Atul | TBD | Open |

## Stakeholder recovery update — draft
Monitoring detected an issue with the lab employee portal at {detected}.
All configured health checks passed at {recovered}.
Root cause and business impact remain pending review.

## Measurement note
Duration measures detection to detected recovery, rather than exact outage time.
"""

notes_file = project / "reports" / "notes" / f"{incident['id']}-notes.md"
if notes_file.exists():
    report += (
        "\n## Investigator notes\n"
        "Note timestamps show when entries were written. "
        "Retrospective entries do not establish action times.\n\n"
        + notes_file.read_text()
    )

output = output_dir / f"{incident['id']}-PIR-with-notes.md"
if output.exists():
    raise SystemExit(f"Report already exists; preserved: {output}")

output.write_text(report)
print(f"Created: {output}")
print(report)
