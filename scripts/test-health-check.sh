#!/usr/bin/env bash

# Mark the run unhealthy if either check fails.
result=0

echo "=== Linux Incident Lab: Health Check ==="
date -Is

echo
echo "Checking Nginx..."
if systemctl is-active --quiet nginx; then
    echo "OK: Nginx is active"
else
    echo "ALERT: Nginx is not active"
    result=1
fi

echo
echo "Checking the homepage..."
if http_code=$(curl -sS -o /dev/null -w '%{http_code}' \
    --max-time 5 http://localhost); then
    if [[ "$http_code" == "200" ]]; then
        echo "OK: Homepage returned HTTP 200"
    else
        echo "ALERT: Homepage returned HTTP $http_code"
        result=1
    fi
else
    echo "ALERT: Could not reach the homepage"
    result=1
fi

echo
echo "Checking root filesystem usage..."
disk_used=$(df -P / | awk 'NR==2 {gsub(/%/, "", $5); print $5}')

if [[ "$disk_used" =~ ^[0-9]+$ ]]; then
    if (( disk_used >= 80 )); then
        echo "ALERT: Root filesystem is ${disk_used}% used"
        result=1
    else
        echo "OK: Root filesystem is ${disk_used}% used"
    fi
else
    echo "ALERT: Could not read disk usage"
    result=1
fi

echo
echo "Checking available memory..."
memory_available=131072

if [[ "$memory_available" =~ ^[0-9]+$ ]]; then
    if (( memory_available < 262144 )); then
        echo "ALERT: Available memory is below 256 MiB"
        result=1
    else
        echo "OK: Available memory is $((memory_available / 1024)) MiB"
    fi
else
    echo "ALERT: Could not read available memory"
    result=1
fi

exit "$result"
