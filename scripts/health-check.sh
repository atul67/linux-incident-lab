#!/usr/bin/env bash

# Configuration
portal_url="http://localhost"
disk_threshold=80
memory_threshold_kib=262144

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)" || exit 1
log_dir="$project_dir/logs"
mkdir -p "$log_dir" || exit 1

# Prevent manual and scheduled runs from overlapping.
exec 9>"$log_dir/health-check.lock"
flock -n 9 || exit 0

# Display results and also append them to the monitoring log.
exec > >(tee -a "$log_dir/health-check.log") 2>&1

result=0
failures=()

ok() {
    echo "OK: $1"
}

alert() {
    echo "ALERT: $1"
    failures+=("$1")
    result=1
}

echo "=== Linux Incident Lab: Health Check ==="
date -Is

echo
echo "Checking Nginx..."
if systemctl is-active --quiet nginx; then
    ok "Nginx is active"
else
    alert "Nginx is not active"
fi

echo
echo "Checking the homepage..."
if http_code=$(curl -sS -o /dev/null -w '%{http_code}' \
    --max-time 5 "$portal_url/"); then
    if [[ "$http_code" == "200" ]]; then
        ok "Homepage returned HTTP 200"
    else
        alert "Homepage returned HTTP $http_code"
    fi
else
    alert "Could not reach the homepage"
fi

echo
echo "Checking root filesystem usage..."
disk_used=$(df -P / | awk 'NR==2 {gsub(/%/, "", $5); print $5}')

if [[ "$disk_used" =~ ^[0-9]+$ ]]; then
    if (( disk_used >= disk_threshold )); then
        alert "Root filesystem is ${disk_used}% used"
    else
        ok "Root filesystem is ${disk_used}% used"
    fi
else
    alert "Could not read disk usage"
fi

echo
echo "Checking available memory..."
memory_available=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)

if [[ "$memory_available" =~ ^[0-9]+$ ]]; then
    if (( memory_available < memory_threshold_kib )); then
        alert "Available memory is below 256 MiB"
    else
        ok "Available memory is $((memory_available / 1024)) MiB"
    fi
else
    alert "Could not read available memory"
fi

echo
echo "Checking portal health endpoint..."
if health_body=$(curl -fsS --max-time 5 "$portal_url/health.txt"); then
    if [[ "$health_body" == "PORTAL_OK" ]]; then
        ok "Portal health endpoint returned PORTAL_OK"
    else
        alert "Portal health endpoint returned unexpected content"
    fi
else
    alert "Portal health endpoint request failed"
fi

# Record overall health transitions.
state_file="$log_dir/last-health-state"
previous_state="UNKNOWN"
if [[ -f "$state_file" ]]; then
    previous_state=$(cat "$state_file")
fi

current_state="HEALTHY"
if (( result != 0 )); then
    current_state="UNHEALTHY"
fi

if [[ "$current_state" != "$previous_state" ]]; then
    if [[ "$current_state" == "UNHEALTHY" ]]; then
        printf '%s | ALERT | %s\n' \
            "$(date -Is)" "${failures[*]}" >> "$log_dir/alerts.log"
    elif [[ "$previous_state" == "UNHEALTHY" ]]; then
        printf '%s | RECOVERY | All health checks passed\n' \
            "$(date -Is)" >> "$log_dir/alerts.log"
    fi
fi

printf '%s\n' "$current_state" > "$state_file"
echo
echo "Overall health: $current_state"

exit "$result"
