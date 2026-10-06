# Setup Guide

## Prerequisites
- Ubuntu with systemd running.
- A regular user with sudo access.
- Project files copied into ~/linux-incident-lab.
- Port 80 available.

## 1. Install packages
```bash
sudo apt update
sudo apt install nginx curl cron -y
```

## 2. Prepare folders and script permissions
```bash
mkdir -p ~/linux-incident-lab/{logs,reports,runbooks}
chmod u+x ~/linux-incident-lab/scripts/health-check.sh
```

## 3. Deploy the webpage
On a fresh lab installation:
```bash
sudo cp ~/linux-incident-lab/www/index.html /var/www/html/index.html
sudo nginx -t
```

Continue only if configuration validation succeeds.

## 4. Start services
```bash
sudo systemctl enable --now nginx cron
```

## 5. Validate
```bash
~/linux-incident-lab/scripts/health-check.sh
echo $?
```

Expected: all checks OK and exit code 0.

## 6. Schedule monitoring
Run:
```bash
crontab -e
```

Add the following once, replacing /home/atul with
your actual home directory if using another account:

```cron
* * * * * /home/atul/linux-incident-lab/scripts/health-check.sh > /dev/null 2>&1
```

Verify with crontab -l and inspect the log after two minutes.

## WSL Limitation
Monitoring runs while WSL is running and Windows is awake.

## Configure Log Rotation

This configuration assumes username and group atul,
with the project in /home/atul/linux-incident-lab.
For another account, update the paths, su and create
settings in config/logrotate.conf before installation.

Install and validate:
```bash
sudo apt install logrotate -y
sudo cp ~/linux-incident-lab/config/logrotate.conf /etc/logrotate.d/linux-incident-lab
sudo logrotate --debug /etc/logrotate.d/linux-incident-lab
```

If validation passes, enable the daily schedule:
```bash
sudo systemctl enable --now logrotate.timer
```

Non-empty logs are rotated daily, with up to seven
archives retained per log. Older archives are compressed.
