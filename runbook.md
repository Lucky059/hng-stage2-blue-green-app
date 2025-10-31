# Runbook  Stage 2 Alerts

## Failover Alert
- Triggered when the active pool fails and traffic switches to backup.
- Action: Check Nginx logs, ensure backup pool is healthy, investigate primary service.

## High Error Rate Alert
- Triggered when more than ERROR_RATE_THRESHOLD errors occur in the monitoring window.
- Action: Inspect logs for root cause, check upstream services, consider scaling or redeploy.

## Notes
- Alerts are rate-limited to avoid spamming Slack.
- All logs are structured with pool, release, upstream status, and latency.

