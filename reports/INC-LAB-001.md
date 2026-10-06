# INC-LAB-001: Simulated Nginx Outage

## Environment
Local Ubuntu WSL lab running Nginx.
Application: http://localhost

## Impact
The lab homepage was unavailable.
No production users were affected.

## Timeline — UTC, 6 October 2026
- 16:51:47: Health check passed.
- 16:52:52: Health check detected inactive Nginx
  and failed HTTP connectivity.
- 16:53:09: Health check confirmed recovery.

## Confirmed Cause
Nginx was deliberately stopped using:
sudo systemctl stop nginx

## Detection
The Bash health-check script checked:
1. Nginx service state.
2. Homepage HTTP response.

Both checks failed during the outage.

## Resolution
Started Nginx using:
sudo systemctl start nginx

## Recovery Validation
Nginx returned active.
The homepage returned HTTP 200.

## Timing
Failed and recovered checks were 17 seconds apart.
Exact outage duration was not measured.

## Evidence
logs/health-check.log

## Improvement
Schedule health checks to detect outages without
manually running the script.
