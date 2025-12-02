# n8n Integration Guide for VRD Crash Calculator

This guide explains how to integrate the Crash Calculator Dashboard with your existing n8n workflow.

## Overview

Your current n8n workflow (`Crash Calculator.json`) uses:
- Chat Trigger for user interaction
- AI Agent with OpenAI GPT-5-mini
- Pinecone Vector Stores (Parts Catalog, Pricing, Examples)
- **Google Sheets** (to be replaced)

We will replace the Google Sheets node with HTTP Request nodes that communicate with the Crash Calculator Dashboard API.

## Architecture

```
User → Chat Interface → AI Agent → HTTP Request → Crash Calculator Dashboard
                             ↓
                    Pinecone Vector Stores
                    (Parts & Pricing Data)
```

## Step-by-Step Integration

### 1. Keep Your Existing Workflow Components

Keep these nodes as-is:
- ✅ When chat message received (Chat Trigger)
- ✅ AI Agent
- ✅ OpenAI Chat Model
- ✅ Simple Memory
- ✅ All Pinecone Vector Store nodes
- ✅ All Embeddings nodes

### 2. Add HTTP Request Node

After the AI Agent, add a new **HTTP Request** node to save the crash report.

#### HTTP Request Node Configuration

**Node Name:** `Save Crash Report`

**Request Settings:**
- **Method:** `POST`
- **URL:** `http://host.docker.internal:8080/api/reports`
  - Use `http://vrd-crash-calculator:8080/api/reports` if you add both containers to the same network
- **Authentication:** None
- **Send Body:** Yes
- **Body Content Type:** JSON

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "driver": "{{ $json.driver }}",
  "date": "{{ $json.date }}",
  "venue": "{{ $json.venue }}",
  "event": "{{ $json.event }}",
  "accident_damage": "{{ $json.accident_damage }}",
  "parts": {{ $json.parts }}
}
```

### 3. Update AI Agent System Prompt

Modify the AI Agent's system message to include this at the end:

```
IMPORTANT: When you've completed the crash report assessment, you MUST output the final
data in JSON format for system processing.

Output Format:
{
  "driver": "Driver Name",
  "date": "YYYY-MM-DD",
  "venue": "Venue Name",
  "event": "Event Name",
  "accident_damage": "Detailed description of the accident and damage",
  "parts": [
    {
      "part_number": "Part Number",
      "part": "Part Description",
      "likelihood": "Highly Likely|Likely|Possible|Unlikely",
      "price": 1234.56,
      "qty": 1
    }
  ]
}

After gathering all information from the user and confirming the parts list,
format your final response as this JSON structure. The system will automatically
save this to our crash report database.
```

### 4. Add Response Handler Node (Optional)

Add a **Code** node after the HTTP Request to format the response back to the user:

**Node Name:** `Format Response`

**JavaScript Code:**
```javascript
// Get the API response
const apiResponse = $input.item.json;

if (apiResponse.success) {
  return {
    json: {
      message: `✅ Crash Report #${apiResponse.report.id} created successfully!\n\n` +
               `Driver: ${apiResponse.report.driver}\n` +
               `Total Damage: $${apiResponse.report.total.toFixed(2)}\n\n` +
               `You can view the full report at: http://localhost:8080/\n` +
               `Report ID: ${apiResponse.report.id}`,
      report_id: apiResponse.report.id,
      report_url: `http://localhost:8080/`
    }
  };
} else {
  return {
    json: {
      message: `❌ Error saving crash report: ${apiResponse.error}`,
      error: true
    }
  };
}
```

### 5. Alternative: Code Node to Parse AI Response

If your AI Agent doesn't output structured JSON directly, add a **Code** node between the AI Agent and HTTP Request:

**Node Name:** `Parse AI Output`

**JavaScript Code:**
```javascript
// Extract JSON from AI response
const aiResponse = $input.item.json.output || $input.item.json.text;

// Try to find JSON in the response
const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);

if (jsonMatch) {
  try {
    const reportData = JSON.parse(jsonMatch[0]);
    return { json: reportData };
  } catch (error) {
    throw new Error('Failed to parse JSON from AI response: ' + error.message);
  }
} else {
  throw new Error('No JSON found in AI response');
}
```

## Network Configuration

### Option A: Same Docker Network (Recommended)

1. Create a shared network:
```bash
docker network create vrd-network
```

2. Update your n8n docker-compose.yml:
```yaml
services:
  n8n:
    # ... your existing config
    networks:
      - vrd-network

networks:
  vrd-network:
    external: true
```

3. Update crash calculator docker-compose.yml:
```yaml
services:
  crash-calculator:
    # ... existing config
    networks:
      - vrd-network

networks:
  vrd-network:
    external: true
```

4. Restart both containers:
```bash
cd ~/crash-calculator-dashboard
docker-compose down && docker-compose up -d

# Restart n8n (adjust path to your n8n directory)
cd /path/to/n8n
docker-compose down && docker-compose up -d
```

5. Use this URL in n8n: `http://vrd-crash-calculator:8080/api/reports`

### Option B: Host Network Access

If running n8n in Docker and crash calculator on host or different network:

Use: `http://host.docker.internal:8080/api/reports`

### Option C: Direct Host Access

If n8n is running directly on the host (not Docker):

Use: `http://localhost:8080/api/reports`

## Testing the Integration

### 1. Test API Connection

In n8n, add a simple HTTP Request node and test:

```
GET http://host.docker.internal:8080/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "VRD Crash Calculator API is running"
}
```

### 2. Test Report Creation

Create a test HTTP Request:

```
POST http://host.docker.internal:8080/api/reports
Content-Type: application/json

{
  "driver": "Test Driver",
  "date": "2025-11-03",
  "venue": "Test Track",
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
}
```

### 3. Verify in Dashboard

Open http://localhost:8080 and check if the report appears.

## Complete Workflow Example

Here's a complete example of the modified workflow:

```
1. [Chat Trigger] User starts conversation
       ↓
2. [AI Agent] Analyzes damage, queries vector stores
       ↓
3. [Code] Parse AI output to JSON (if needed)
       ↓
4. [HTTP Request] POST to /api/reports
       ↓
5. [Code] Format success message
       ↓
6. [Chat Response] Send confirmation to user
```

## Troubleshooting

### Error: Connection Refused

**Problem:** Cannot connect to API
**Solutions:**
1. Check container is running: `docker ps | grep vrd-crash-calculator`
2. Check API health: `curl http://localhost:8080/api/health`
3. Use `host.docker.internal` instead of `localhost` if n8n is in Docker
4. Check firewall settings

### Error: 400 Bad Request

**Problem:** Invalid data format
**Solutions:**
1. Check JSON structure matches API requirements
2. Ensure `price` is a number, not string
3. Ensure `date` is in `YYYY-MM-DD` format
4. Check all required fields are present

### Error: Cannot Parse JSON from AI

**Problem:** AI doesn't output valid JSON
**Solutions:**
1. Update AI system prompt to emphasize JSON output
2. Add the "Parse AI Output" code node
3. Test AI responses manually to see output format

### Error: Parts Array Empty

**Problem:** No parts in the report
**Solutions:**
1. Ensure AI agent successfully queries Pinecone
2. Check vector store connections
3. Verify parts data is properly formatted

## API Endpoints Reference

### Create Report
```http
POST /api/reports
```

### Update Report
```http
PUT /api/reports/{id}
```

### Get Report
```http
GET /api/reports/{id}
```

### Get All Reports
```http
GET /api/reports
```

### Add Part to Report
```http
POST /api/reports/{id}/parts
```

## Example n8n Workflow Node

Here's a complete HTTP Request node configuration in JSON:

```json
{
  "parameters": {
    "method": "POST",
    "url": "http://host.docker.internal:8080/api/reports",
    "authentication": "none",
    "sendBody": true,
    "contentType": "application/json",
    "bodyParameters": {
      "parameters": [
        {
          "name": "driver",
          "value": "={{ $json.driver }}"
        },
        {
          "name": "date",
          "value": "={{ $json.date }}"
        },
        {
          "name": "venue",
          "value": "={{ $json.venue }}"
        },
        {
          "name": "event",
          "value": "={{ $json.event }}"
        },
        {
          "name": "accident_damage",
          "value": "={{ $json.accident_damage }}"
        },
        {
          "name": "parts",
          "value": "={{ $json.parts }}"
        }
      ]
    }
  },
  "name": "Save Crash Report",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.1,
  "position": [420, 300]
}
```

## Next Steps

1. ✅ Verify dashboard is running: http://localhost:8080
2. ✅ Test API health endpoint
3. 📝 Update AI Agent system prompt
4. 🔧 Add HTTP Request node to workflow
5. 🧪 Test with sample data
6. 🚀 Enable workflow and test with real conversations

## Support

For issues or questions:
- Check container logs: `docker-compose logs -f`
- Test API manually: `curl http://localhost:8080/api/health`
- View all reports: `curl http://localhost:8080/api/reports`
