# Troubleshooting Guide - n8n Dashboard Integration

## 🔍 Common Issues and Solutions

---

## Issue 1: "Connection Refused" or "ECONNREFUSED"

### Symptoms:
- HTTP Request node fails with connection error
- Error message mentions port 8080
- "Cannot connect to host.docker.internal"

### Solutions:

#### Solution A: Dashboard Not Running
```bash
# Check if dashboard is running
docker ps | grep vrd-crash-calculator

# If not running, start it
cd /Users/joshholland/crash-calculator-dashboard
docker-compose up -d

# Wait 5 seconds and test
curl http://localhost:8080/api/health
```

#### Solution B: Wrong URL
Try different URLs in HTTP Request node:

1. `http://host.docker.internal:8080/api/reports/from-n8n`
2. `http://localhost:8080/api/reports/from-n8n`
3. `http://172.17.0.1:8080/api/reports/from-n8n` (Docker bridge network)

#### Solution C: n8n in Docker (Different Network)
If n8n is also in Docker, you may need to:

1. **Check dashboard container name:**
   ```bash
   docker ps | grep crash-calculator
   # Look for container name (e.g., vrd-crash-calculator)
   ```

2. **Use container name in URL:**
   ```
   http://vrd-crash-calculator:8080/api/reports/from-n8n
   ```

3. **Or connect to same network:**
   ```bash
   docker network connect crash-calculator-dashboard_crash-calc-network <n8n-container-name>
   ```

---

## Issue 2: "JSON Markers Not Found"

### Symptoms:
- Code node shows: "JSON markers not found in AI response"
- Report not sent to dashboard
- AI seems to complete but no JSON output

### Solutions:

#### Solution A: AI Hasn't Generated Final Report Yet
The AI is still in conversation mode, not generating the final report.

**Fix:** Tell the AI explicitly:
```
Please generate the final crash report now with all the parts we discussed.
```

#### Solution B: System Prompt Not Updated
The AI doesn't know to output JSON markers.

**Fix:**
1. Check AI Agent node
2. Verify system message includes:
   - `###JSON_START###` and `###JSON_END###` instructions
   - Final report format section
3. Re-save the node
4. Restart workflow (deactivate and reactivate)

#### Solution C: AI Output Location Changed
n8n may have changed where chat output is stored.

**Fix:** Update Code node to check more locations:
```javascript
// Add more fallback checks in the code
if (item.json.output) {
  fullMessage = item.json.output;
} else if (item.json.message) {
  fullMessage = item.json.message;
} else if (item.json.text) {
  fullMessage = item.json.text;
} else if (item.json.content) {
  fullMessage = item.json.content;
} else if (item.json.response) {
  fullMessage = item.json.response;
}
```

---

## Issue 3: "Invalid JSON" or Parse Error

### Symptoms:
- Code node fails with "Unexpected token" error
- JSON appears in output but won't parse
- "SyntaxError: Unexpected token"

### Solutions:

#### Solution A: AI Generated Bad JSON
Check the AI output for:
- Missing commas
- Trailing commas
- Unescaped quotes in strings
- Comments in JSON (not allowed)

**Fix:** Update AI system prompt to emphasize valid JSON:
```
CRITICAL: The JSON must be perfectly valid. No comments, no trailing commas, all strings properly escaped.
```

#### Solution B: Special Characters in Data
Driver names or descriptions with quotes breaking JSON.

**Fix:** Add sanitization in Code node:
```javascript
// After parsing, sanitize strings
reportData.driver = reportData.driver.replace(/[^\x20-\x7E]/g, '');
reportData.accident_damage = reportData.accident_damage.replace(/[^\x20-\x7E\n\r]/g, '');
```

#### Solution C: Multiple JSON Blocks
AI outputs multiple sets of markers.

**Fix:** Use lastIndexOf for end marker:
```javascript
const startIndex = fullMessage.indexOf(startMarker);
const endIndex = fullMessage.lastIndexOf(endMarker); // Use last occurrence
```

---

## Issue 4: Report Missing Fields

### Symptoms:
- Report appears in dashboard but missing driver name, date, etc.
- Dashboard shows "N/A" or empty values
- Parts array is empty

### Solutions:

#### Solution A: Required Fields Not in JSON
Check the AI output - does JSON have all fields?

**Fix:** Verify JSON includes:
```json
{
  "driver": "...",       // Required
  "date": "YYYY-MM-DD",  // Required
  "event": "...",        // Required
  "venue": "...",
  "accident_damage": "...",
  "parts": [...]         // Can be empty array
}
```

#### Solution B: Date Format Wrong
Dashboard expects `YYYY-MM-DD`, AI might output `November 3, 2025`.

**Fix:** Add date formatting in Code node:
```javascript
// After parsing
if (reportData.date && !reportData.date.match(/^\d{4}-\d{2}-\d{2}$/)) {
  // Try to parse and reformat
  const parsedDate = new Date(reportData.date);
  if (!isNaN(parsedDate)) {
    reportData.date = parsedDate.toISOString().split('T')[0];
  }
}
```

#### Solution C: Parts Price as String
Price should be number, not "$100.00" string.

**Fix:** Already handled in Code node, but verify:
```javascript
price: typeof part.price === 'number' ? part.price : (parseFloat(part.price) || 0)
```

---

## Issue 5: Report Not Appearing in Pending Section

### Symptoms:
- n8n says success
- HTTP Request returns 200 OK
- But report not visible in http://localhost:8080/pending

### Solutions:

#### Solution A: Wrong Endpoint
Using `/api/reports` instead of `/api/reports/from-n8n`.

**Fix:**
- Reports from `/api/reports` are marked as "active", not "pending"
- Check Pending section vs All Reports section
- Use `/api/reports/from-n8n` to mark as pending

#### Solution B: Report Exists But Dashboard Not Refreshing
Browser cache or auto-refresh not working.

**Fix:**
1. Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
2. Check All Reports section: http://localhost:8080/reports
3. Check database directly:
   ```bash
   docker exec -it vrd-crash-calculator sqlite3 /app/instance/crash_reports.db
   SELECT id, driver, status FROM report ORDER BY id DESC LIMIT 5;
   .quit
   ```

#### Solution C: Multiple Dashboard Instances
You may have started dashboard outside Docker AND inside Docker.

**Fix:**
```bash
# Stop all instances
docker-compose down
killall python3  # If running outside Docker

# Start only Docker version
docker-compose up -d

# Verify only one
curl http://localhost:8080/api/health
```

---

## Issue 6: IF Node Always Goes to False Branch

### Symptoms:
- Parse successful message in Code node
- IF node always routes to FALSE
- Error notification triggers

### Solutions:

#### Solution A: Wrong Expression Syntax
n8n expression syntax changed.

**Fix:** Try different syntax:
```
{{ $json.success }}           // Current
{{ $json["success"] }}        // Alternative
{{ Boolean($json.success) }}  // Explicit conversion
```

#### Solution B: Code Node Output Structure Wrong
Success field might be nested differently.

**Fix:** Check Code node output structure in execution log. Adjust IF condition to match actual path.

---

## Issue 7: Dashboard API Returns 400 or 500 Error

### Symptoms:
- HTTP Request shows error code 400 or 500
- Dashboard logs show error
- n8n execution fails

### Solutions:

#### Solution A: Check Dashboard Logs
```bash
docker logs vrd-crash-calculator --tail 50

# Look for error messages
# Common issues:
# - "Required field missing"
# - "Invalid date format"
# - "JSON decode error"
```

#### Solution B: Validate Request Body
Test the exact data being sent:

1. In n8n, look at HTTP Request node input (before sending)
2. Copy the JSON
3. Test manually:
   ```bash
   curl -X POST http://localhost:8080/api/reports/from-n8n \
     -H "Content-Type: application/json" \
     -d '<paste your JSON here>'
   ```

#### Solution C: Dashboard Database Issue
Database might be corrupted or locked.

**Fix:**
```bash
# Restart dashboard
docker-compose restart

# If that doesn't work, check database
docker exec -it vrd-crash-calculator sqlite3 /app/instance/crash_reports.db
.tables
.quit

# Last resort: reset database (DELETES ALL DATA!)
docker-compose down
rm -f instance/crash_reports.db
docker-compose up -d
```

---

## Issue 8: AI Not Using Pinecone Tools

### Symptoms:
- AI suggests generic parts not from catalog
- Prices are all "N/A"
- AI doesn't seem to query vector stores

### Solutions:

#### Solution A: Pinecone Credentials Issue
Check API keys are valid.

**Fix:**
1. In n8n, click on AI Agent node
2. Check credentials for Pinecone nodes
3. Test connection
4. Verify namespace names are exact matches

#### Solution B: Embedding Model Issue
OpenAI embeddings not working.

**Fix:**
1. Verify OpenAI API key is valid
2. Check OpenAI account has credits
3. Test with a simple query

---

## Issue 9: Workflow Execution Hangs

### Symptoms:
- Workflow starts but never completes
- Loading spinner forever
- No error message

### Solutions:

#### Solution A: AI Taking Too Long
GPT-5-mini can be slow with complex queries.

**Fix:**
1. Wait up to 2 minutes
2. Check OpenAI usage dashboard
3. Consider timeout settings

#### Solution B: Memory Issue
Buffer memory might be too large.

**Fix:**
1. Clear chat history
2. Start fresh conversation
3. Reduce context window in Memory node

---

## 🔍 Debugging Checklist

When something goes wrong, check in this order:

1. **Dashboard Running?**
   ```bash
   docker ps | grep vrd-crash-calculator
   curl http://localhost:8080/api/health
   ```

2. **n8n Execution Log**
   - Check each node's output
   - Look for red error badges
   - Read error messages

3. **AI Output Has Markers?**
   - Click on AI Agent node in execution
   - Scroll through output
   - Find `###JSON_START###` and `###JSON_END###`

4. **Code Node Parsed Successfully?**
   - Check output: `success: true`?
   - reportData object present?

5. **HTTP Request Sent?**
   - Check status code (200 = good)
   - Check response body
   - Look for success message

6. **Dashboard Received It?**
   ```bash
   docker logs vrd-crash-calculator --tail 20
   # Look for "POST /api/reports/from-n8n"
   ```

7. **Report in Database?**
   - Check /pending page
   - Check /reports page
   - Query database directly if needed

---

## 🆘 Still Stuck?

### Gather Information:

1. **n8n execution log** (screenshot or copy/paste)
2. **Dashboard logs:** `docker logs vrd-crash-calculator --tail 100`
3. **Test API directly:** Use curl to rule out n8n issues
4. **n8n version:** Check for compatibility
5. **Error messages:** Exact text of any errors

### Share This Info:

Provide the gathered information for faster troubleshooting.

---

## 📝 Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Connection refused | Check dashboard running: `docker-compose up -d` |
| No JSON markers | Ask AI: "Generate final report now" |
| Parse error | Check AI output has valid JSON between markers |
| Missing fields | Verify JSON has driver, date, event |
| Not in Pending | Check using `/from-n8n` endpoint, not `/reports` |
| IF always false | Change condition to: `{{ Boolean($json.success) }}` |
| 400/500 error | Check dashboard logs: `docker logs vrd-crash-calculator` |
| Workflow hangs | Wait 2 min, or reduce context window |

---

## ✅ Prevention Tips

1. **Test API first** before adding n8n nodes
2. **Save workflow often** before making changes
3. **Keep system prompt updated** when you change API format
4. **Monitor dashboard logs** during first few tests
5. **Start simple** - test with minimal data first
6. **Document changes** to custom configurations
