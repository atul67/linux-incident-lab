# Linux Application Monitoring & Incident Response Lab

## Overview
A local Ubuntu WSL lab hosting a demo employee portal
using Nginx. A Bash script monitors availability and
resources, records failures and recovery, and runs
every minute through cron.

## Tools
Ubuntu, Nginx, Bash, curl, cron, systemd and logrotate.

## Health Checks
1. Nginx service is active.
2. Homepage returns HTTP 200.
3. Root filesystem usage is below 80%.
4. Available memory is at least 256 MiB.
5. Static health endpoint returns PORTAL_OK.

## Monitoring Behaviour
- Displays and saves timestamped check results.
- Returns 0 when healthy and 1 when a check fails.
- Records an alert when overall health becomes unhealthy.
- Records recovery when all checks pass again.
- Uses a lock to prevent overlapping monitoring runs.
- Rotates non-empty logs daily, retaining seven archives.

## Project Structure
- scripts/health-check.sh: main monitoring script.
- scripts/test-health-check.sh: simulated resource tests.
- www/: webpage and static health endpoint.
- config/logrotate.conf: log rotation configuration.
- logs/: runtime logs, archives and health state.
- reports/: incident documentation.
- runbooks/: troubleshooting instructions.
- SETUP.md: installation and scheduling guide.

## Run Manually
From the project directory:

bash scripts/health-check.sh
echo $?

## Verified Scenarios
- Healthy application and server checks.
- Nginx stopped, failure detected and service restored.
- Disk alert triggered with a lowered test threshold.
- Memory alert triggered with a simulated input.
- Incorrect health endpoint content detected and restored.
- Repeated unhealthy checks produced one transition alert.
- Recovery produced a separate recovery entry.
- Cron generated consecutive automatic checks.
- Log rotation archived logs and monitoring continued.

## Limitations
- This is a local learning lab, not a production service.
- WSL must be running and Windows awake for scheduling.
- Employee services are placeholders.
- The static health endpoint does not check a backend
  or database.
- Alerts are local log entries; external notifications
  and ServiceNow integration are not implemented.
- Alert transitions track overall health; a new failure
  during an existing unhealthy state appears in the
  monitoring log but does not create another alert.
- CPU monitoring and automatic remediation are not
  implemented.

## Documentation
See SETUP.md for deployment instructions and
runbooks/nginx-outage.md for troubleshooting.
