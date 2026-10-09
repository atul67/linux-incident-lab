#!/usr/bin/env python3
import json
from html import escape
from pathlib import Path
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROJECT = Path(__file__).resolve().parent.parent
INCIDENTS = PROJECT / "reports" / "incidents"

def render():
    records = []
    errors = 0

    for path in INCIDENTS.glob("*.json"):
        try:
            records.append(json.loads(path.read_text()))
        except (OSError, ValueError):
            errors += 1

    records.sort(key=lambda item: item["detected_at"], reverse=True)
    opened = [item for item in records if item["status"] == "OPEN"]
    resolved = [item for item in records if item["status"] == "RESOLVED"]
    durations = [
        item["detected_resolution_seconds"] for item in resolved
        if "detected_resolution_seconds" in item
    ]
    average = f"{sum(durations)/len(durations):.1f} seconds" if durations else "N/A"

    state_file = PROJECT / "logs" / "last-health-state"
    health = "UNKNOWN"
    checked = "No completed check"
    if state_file.exists():
        health = state_file.read_text().strip()
        timestamp = state_file.stat().st_mtime
        checked = datetime.fromtimestamp(
            timestamp, timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")
        age = datetime.now(timezone.utc).timestamp() - timestamp
        if age > 120:
            health = f"STALE — last result: {health}"

    rows = ""
    for item in records:
        failures = "; ".join(item.get("initial_failures", []))
        duration = item.get("detected_resolution_seconds")
        elapsed = f"{duration} seconds" if duration is not None else "In progress"
        values = [
            item["id"], item["status"], item["detected_at"],
            failures, elapsed
        ]
        rows += "<tr>" + "".join(
            f"<td>{escape(str(value))}</td>" for value in values
        ) + "</tr>"

    if not rows:
        rows = '<tr><td colspan="5">No incidents recorded yet.</td></tr>'

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="15">
<title>Incident Operations Dashboard</title>
<style>
body {{font-family:Arial,sans-serif;background:#101827;color:#edf2ff;
       margin:0;padding:30px}}
.cards {{display:flex;flex-wrap:wrap;gap:16px;margin:24px 0}}
.card {{background:#1e2b42;border-radius:12px;padding:20px;min-width:170px}}
.value {{font-size:24px;font-weight:bold;margin-top:12px}}
.table-wrap {{overflow:auto}}
table {{width:100%;border-collapse:collapse;background:#1e2b42}}
th,td {{padding:14px;text-align:left;border-bottom:1px solid #35445d}}
th {{color:#8dcaff}}
.note {{color:#b6c4dc;line-height:1.6}}
</style>
</head>
<body>
<h1>Incident Operations Dashboard</h1>
<p class="note">Linux Employee Portal Lab · Refreshes every 15 seconds</p>
<div class="cards">
<div class="card">Last monitored health
<div class="value">{escape(health)}</div></div>
<div class="card">Open incidents<div class="value">{len(opened)}</div></div>
<div class="card">Resolved incidents<div class="value">{len(resolved)}</div></div>
<div class="card">Average detected resolution
<div class="value">{average}</div></div>
</div>
<p class="note">Last health check: {checked}</p>
<div class="table-wrap">
<table>
<thead><tr><th>Incident ID</th><th>Status</th><th>Detected at</th>
<th>Initial symptoms</th><th>Detected resolution time</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</div>
<p class="note">Times are UTC. Resolution time measures detection to detected
recovery. Health becomes stale after two minutes without an update.
Unreadable incident files: {errors}.</p>
</body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        content = render().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

if __name__ == "__main__":
    print("Dashboard: http://localhost:8765", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
