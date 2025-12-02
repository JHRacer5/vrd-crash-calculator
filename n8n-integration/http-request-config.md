# HTTP Request Node Configuration

## Environment Variable Setup (n8n Cloud)

Before configuring the HTTP node, set up an environment variable in your n8n cloud instance:

1. Go to your n8n cloud **Settings** → **Variables**
2. Add a new variable:
   - **Name:** `DASHBOARD_API_URL`
   - **Value:** `https://your-cloudflare-domain.com` (your dashboard URL when deployed)

   For local testing, use: `http://host.docker.internal:8080`

---

## Node Settings

**Node Name:** Send to Dashboard

**Method:** PUT

**URL:**
```
{{ $env.DASHBOARD_API_URL }}/api/reports/by-incident/{{ $json.incidentId }}
```

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

## Two-Step Workflow

This configuration uses the **two-step flow**:

1. **User creates report in Dashboard UI** → Gets an `incident_id` (e.g., `VRD-20251202-915E27`)
2. **User provides incident_id to n8n chat** along with crash details
3. **n8n AI analyzes** and generates parts list
4. **n8n calls PUT** `/api/reports/by-incident/{incident_id}` to update the report with parts

The Code Node extracts the `incident_id` from the conversation and passes it as `$json.incidentId`.

---

## Testing the Endpoint

Test that the dashboard API is reachable:

```bash
# Health check
curl $DASHBOARD_API_URL/api/health

# Test PUT endpoint (replace with actual incident_id)
curl -X PUT $DASHBOARD_API_URL/api/reports/by-incident/VRD-20251202-915E27 \
  -H "Content-Type: application/json" \
  -d '{
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
  "message": "Report updated successfully by incident_id",
  "report": {
    "id": 1,
    "incident_id": "VRD-20251202-915E27",
    "status": "active",
    ...
  }
}
```

---

## IF Node Configuration (Required)

Add an IF node between Code and HTTP Request to check:
1. Parsing was successful
2. An incident_id was found

**Condition 1:**
- Value 1: `{{ $json.success }}`
- Operation: `is equal to`
- Value 2: `true`

**Condition 2:**
- Value 1: `{{ $json.hasIncidentId }}`
- Operation: `is equal to`
- Value 2: `true`

**True Branch:** Connect to HTTP Request node
**False Branch:** Connect to a "Stop and Error" node with message: "No incident_id found. Please include the incident ID from the dashboard in your message."

---

## Cloudflare Deployment Notes

When you deploy the dashboard to Cloudflare:

1. Update the `DASHBOARD_API_URL` environment variable in n8n cloud to your Cloudflare URL
2. Ensure CORS is configured on the Flask app if needed
3. The Supabase connection will work from anywhere since it's cloud-hosted
