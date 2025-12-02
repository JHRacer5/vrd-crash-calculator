# HTTP Request Node Configuration

## Node Settings

**Node Name:** Send to Dashboard

**Method:** POST

**URL:** `http://host.docker.internal:8080/api/reports/from-n8n`

**Authentication:** None

**Send Body:** Yes

**Body Content Type:** JSON

---

## Request Body

In the "Body" section, select "JSON" and use this expression:

```
{{ $json.reportData }}
```

This will send the parsed report data from the Code node.

---

## Headers

Add these headers:

| Header Name | Value |
|------------|-------|
| Content-Type | application/json |

---

## Options

**Response Format:** JSON

**Timeout:** 30000 (30 seconds)

**Redirect:** Follow All Redirects

---

## Error Handling

Enable "Continue On Fail" so the workflow doesn't crash if the dashboard is unreachable.

---

## Testing the Endpoint

Before configuring this node, test that the dashboard is reachable from n8n:

```bash
curl -X POST http://host.docker.internal:8080/api/reports/from-n8n \
  -H "Content-Type: application/json" \
  -d '{
    "driver": "Test Driver",
    "date": "2025-11-03",
    "venue": "Chassis 02",
    "event": "Test Event",
    "accident_damage": "Test damage description",
    "parts": [
      {
        "part_number": "TEST-001",
        "part": "Test Part",
        "likelihood": "Likely",
        "price": 100.00,
        "qty": 1
      }
    ]
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Report created successfully and marked as PENDING for review",
  "status": "pending",
  "report": {
    "id": 1,
    "driver": "Test Driver",
    "status": "pending",
    ...
  }
}
```

---

## IF Node Configuration (Optional - Recommended)

Add an IF node between Code and HTTP Request to check if parsing was successful:

**Condition:**
- Value 1: `{{ $json.success }}`
- Operation: `is equal to`
- Value 2: `true`

**True Branch:** Connect to HTTP Request node
**False Branch:** Connect to a "Stop and Error" node or notification

This prevents sending bad data to the dashboard.
