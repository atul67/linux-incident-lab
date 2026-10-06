# Runbook: Nginx Homepage Unavailable

## Scope
Local Ubuntu WSL lab serving http://localhost.

## 1. Confirm the symptoms
```bash
systemctl is-active nginx
curl -I --max-time 5 http://localhost
```

Expected healthy results: active and HTTP 200.

## 2. Gather evidence before recovery
```bash
sudo systemctl status nginx --no-pager -l
sudo journalctl -u nginx --since "10 minutes ago" --no-pager
sudo tail -n 20 /var/log/nginx/error.log
sudo nginx -t
```

- Inspect service and journal output for failures.
- Check the error log for relevant messages.
- nginx -t validates configuration syntax and referenced files.
- Record observations; do not assume the root cause.

## 3. Recover a stopped service
If configuration validation passes and the service
is stopped, start it:

```bash
sudo systemctl start nginx
```

If configuration validation fails, investigate the
reported file and line before attempting recovery.

## 4. Validate recovery
```bash
~/linux-incident-lab/scripts/health-check.sh
echo $?
```

Expected: all checks OK and exit code 0.
Also confirm the project webpage opens in the browser.

## 5. Document the incident
Record impact, detection time, observations, actions,
recovery evidence, and confirmed or unresolved cause.
