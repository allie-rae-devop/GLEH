# LOGGING QUICK START GUIDE

**For:** Developers, SRE, Operations
**Date:** 2025-11-14
**Status:** Ready for use

---

## Installation

```bash
# Install required dependency
pip install structlog

# Or install all requirements
pip install -r requirements.txt
```

---

## Quick Validation

```bash
# Test logging configuration
python test_logging_manual.py

# Expected output:
# ✓ ALL TESTS PASSED
# Structured logging is ready for production use.
```

---

## Running the Application

### Development Mode

```bash
export FLASK_ENV=development
python app.py

# Logs will appear in console (pretty-printed, colored)
```

### Production Mode

```bash
export FLASK_ENV=production
waitress-serve --port=8000 app:app

# Logs will be written to: logs/app.log (JSON format)
```

---

## Viewing Logs

### Development (Console)

Logs appear in console with pretty formatting:

```
[info     ] request_received           event=request_received method=GET path=/api/content
[info     ] request_completed          event=request_completed status=200 latency_ms=45.23
```

### Production (File)

Logs written to `logs/app.log` in JSON format:

```json
{"timestamp": "2025-11-14T08:30:45.123Z", "level": "info", "event": "request_received", "method": "GET", "path": "/api/content"}
{"timestamp": "2025-11-14T08:30:45.234Z", "level": "info", "event": "request_completed", "status": 200, "latency_ms": 45.23}
```

---

## Analyzing Logs

### Basic Analysis

```bash
# Full report (last hour)
python log_analyzer.py --since 1h

# Error rate report
python log_analyzer.py --report errors

# Latency analysis
python log_analyzer.py --report latency

# Authentication analysis
python log_analyzer.py --report auth
```

### Anomaly Detection

```bash
# Detect anomalies
python log_analyzer.py --anomalies

# Example output:
# Anomalies detected:
# High Error Rate:
#   - /api/login: 15.5% error rate (31/200)
# High Latency:
#   - p99 latency is 678ms (threshold: 500ms)
```

### AHDM Integration

```bash
# Generate AHDM-compatible JSON
python log_analyzer.py --ahdm --json

# Pipe to AHDM
python log_analyzer.py --ahdm --json | ahdm-ingest
```

---

## Common Event Types

### Request Lifecycle

- `request_received` - Request initiated
- `request_completed` - Request finished (includes latency, status)

### Authentication

- `user_login_attempt` - Login attempted
- `user_login_success` - Login succeeded
- `user_login_failed` - Login failed
- `user_logout` - User logged out
- `user_registered` - New user registered

### Security

- `rate_limit_exceeded` - Rate limit triggered
- `image_upload_rejected` - Upload validation failed
- `image_upload_success` - Upload succeeded
- `error_occurred` - Unhandled exception

---

## Adding Custom Logging

### In Route Handlers

```python
@app.route('/api/custom', methods=['POST'])
def custom_endpoint():
    # Log custom event
    if hasattr(g, 'log'):
        g.log.info(
            "custom_event",
            custom_field="value",
            user_id=current_user.id if current_user.is_authenticated else None
        )

    # Your business logic here
    return jsonify({'status': 'ok'})
```

### Error Logging

```python
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    if hasattr(g, 'log'):
        g.log.error(
            "operation_failed",
            error_type=type(e).__name__,
            error_message=str(e),
            operation="risky_operation"
        )
    raise
```

### Security Events

```python
# Log security violation
if hasattr(g, 'log'):
    g.log.warning(
        "security_violation",
        violation_type="unauthorized_access",
        attempted_resource="/admin",
        user_id=current_user.id if current_user.is_authenticated else None
    )
```

---

## Performance Monitoring

### View Latency Stats

```bash
python log_analyzer.py --report latency

# Output:
# LATENCY ANALYSIS
# p50 (median): 42.5ms
# p95: 78.3ms
# p99: 120.7ms
# Mean: 48.2ms
# Max: 234.5ms
```

### Identify Slow Endpoints

```bash
python log_analyzer.py --report latency --json | jq '.endpoint_stats'

# Shows per-endpoint latency breakdown
```

---

## Troubleshooting

### Issue: "structlog not installed"

**Solution:**
```bash
pip install structlog
```

### Issue: Logs not appearing in file

**Check:**
1. Running in production mode? `export FLASK_ENV=production`
2. Logs directory exists? Should be created automatically
3. File permissions? Check `logs/` directory

**Debug:**
```bash
# Check if logs directory exists
ls -la logs/

# Create manually if needed
mkdir -p logs
```

### Issue: Log analyzer shows "No logs found"

**Check:**
1. Log file path correct? Default: `logs/app.log`
2. Logs actually written? Run app first
3. Time filter too restrictive? Try `--since 24h`

**Debug:**
```bash
# Check log file exists and has content
cat logs/app.log | head -5

# Try without time filter
python log_analyzer.py
```

### Issue: Performance slower than expected

**Check:**
1. Too many log entries per request?
2. Disk I/O bottleneck?
3. Large log files (>1GB)?

**Solution:**
- Reduce log verbosity (change INFO to WARNING)
- Add log sampling
- Rotate logs more frequently

---

## Log Rotation

### Automatic Rotation

Production mode automatically rotates logs:
- **Frequency:** Daily (midnight)
- **Retention:** 30 days
- **Location:** `logs/app.log`, `logs/app.log.YYYY-MM-DD`

### Manual Rotation

```bash
# Rotate logs manually
mv logs/app.log logs/app.log.$(date +%Y-%m-%d)

# Compress old logs
gzip logs/app.log.2025-11-13
```

### Clean Old Logs

```bash
# Remove logs older than 30 days
find logs/ -name "app.log.*" -mtime +30 -delete
```

---

## Security Best Practices

### Never Log Sensitive Data

```python
# BAD - Logs password
g.log.info("user_login", password=data['password'])

# GOOD - No sensitive data
g.log.info("user_login_attempt", username=data['username'])
```

### Use PII Masking

```python
from logging_config import mask_sensitive_data

# Automatically mask sensitive fields
log_data = mask_sensitive_data({
    'username': 'john',
    'password': 'secret123',
    'token': 'abc-def-123'
})

g.log.info("user_data", **log_data)

# Output:
# username: 'john'
# password: '***REDACTED***'
# token: '***REDACTED***'
```

---

## Integration with Monitoring

### Grafana Dashboard

```bash
# Export AHDM data for Grafana
python log_analyzer.py --ahdm --json > /var/lib/grafana/gleh-metrics.json
```

### CloudWatch Logs

```bash
# Stream logs to CloudWatch
tail -f logs/app.log | aws logs put-log-events --log-group-name /gleh/app
```

### Elasticsearch

```bash
# Index logs in Elasticsearch
cat logs/app.log | while read line; do
  curl -XPOST 'localhost:9200/gleh-logs/_doc' -H 'Content-Type: application/json' -d "$line"
done
```

---

## Further Reading

- **Architecture:** `docs/architecture/LOGGING_ARCHITECTURE.md`
- **Implementation:** `docs/operations/LOGGING_IMPLEMENTATION_SUMMARY.md`
- **structlog Docs:** https://www.structlog.org/
- **OWASP Logging:** https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

---

## Support

**Issues?**
1. Check `test_logging_manual.py` output
2. Review `docs/architecture/LOGGING_ARCHITECTURE.md`
3. Contact InfrastructureEngineer or solutions-architect

**Feature Requests?**
- See "Future Enhancements" in LOGGING_ARCHITECTURE.md
- Submit to solutions-architect for Phase 2 planning

---

**END OF QUICK START GUIDE**

*Last updated: 2025-11-14*
