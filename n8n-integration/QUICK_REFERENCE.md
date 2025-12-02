# Quick Reference - n8n Dashboard Integration

## 🚀 Quick Start (TL;DR)

1. **Update AI Agent** → Paste new system prompt
2. **Add Code node** → Paste parser code
3. **Add IF node** → Check `{{ $json.success }}` = true
4. **Add HTTP Request** → POST to `http://host.docker.internal:8080/api/reports/from-n8n`
5. **Test** → Chat → Generate report → Check /pending page

---

## 📍 Node Configuration Summary

### AI Agent Node
- **System Message:** Copy from `ai-agent-system-prompt.txt`
- **Key addition:** Outputs JSON between `###JSON_START###` and `###JSON_END###`

### Code Node (Parse Report Data)
- **Language:** JavaScript
- **Mode:** Run Once for All Items
- **Code:** Copy from `code-node-parser.js`
- **Input:** Connected to AI Agent output
- **Output:** `{ success: true/false, reportData: {...} }`

### IF Node (Check Parse Success)
- **Condition:** `{{ $json.success }}` = `true`
- **TRUE branch:** Goes to HTTP Request
- **FALSE branch:** Goes to error handler

### HTTP Request Node (Send to Dashboard)
- **Method:** POST
- **URL:** `http://host.docker.internal:8080/api/reports/from-n8n`
- **Body:** JSON → `{{ $json.reportData }}`
- **Headers:** `Content-Type: application/json`
- **Timeout:** 30000ms
- **Continue on Fail:** ON (for testing)

---

## 🔗 Workflow Flow Diagram

```
┌─────────────────────┐
│  Chat Trigger       │
│  (User starts chat) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AI Agent           │
│  - Analyzes crash   │
│  - Suggests parts   │
│  - Generates JSON   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Parse Report Data  │
│  (Code Node)        │
│  - Extracts JSON    │
│  - Validates fields │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Check Success      │
│  (IF Node)          │
└─────┬──────────┬────┘
      │          │
   TRUE│      FALSE│
      │          ▼
      │     ┌──────────┐
      │     │  Error   │
      │     │  Handler │
      │     └──────────┘
      │
      ▼
┌─────────────────────┐
│  Send to Dashboard  │
│  (HTTP Request)     │
└──────────┬──────────┘
           │
           ▼
      Dashboard
    (Pending Reports)
```

---

## 🎯 Critical URLs

| Purpose | URL |
|---------|-----|
| Dashboard Home | http://localhost:8080 |
| Pending Reports | http://localhost:8080/pending |
| All Reports | http://localhost:8080/reports |
| n8n Integration Page | http://localhost:8080/n8n-integration |
| API Health Check | http://localhost:8080/api/health |
| n8n Endpoint | http://host.docker.internal:8080/api/reports/from-n8n |

---

## ✅ Pre-Flight Checklist

Before testing:
- [ ] Dashboard is running (`docker ps`)
- [ ] Dashboard is healthy (`curl http://localhost:8080/api/health`)
- [ ] n8n workflow is saved
- [ ] n8n workflow is activated (green toggle)
- [ ] All nodes are connected properly
- [ ] System prompt updated in AI Agent
- [ ] Code pasted in Code node
- [ ] HTTP Request URL is correct

---

## 🧪 Test Commands

### Test Dashboard API:
```bash
curl http://localhost:8080/api/health
```

### Test Create Report:
```bash
curl -X POST http://localhost:8080/api/reports/from-n8n \
  -H "Content-Type: application/json" \
  -d '{"driver":"Test","date":"2025-11-03","venue":"Chassis 02","event":"Test","accident_damage":"Test","parts":[]}'
```

### View Dashboard Logs:
```bash
docker logs vrd-crash-calculator --tail 50 -f
```

### Check Database:
```bash
docker exec -it vrd-crash-calculator sqlite3 /app/instance/crash_reports.db "SELECT id, driver, status FROM report ORDER BY id DESC LIMIT 5;"
```

---

## 🔍 Troubleshooting Quick Checks

| Symptom | Check | Fix |
|---------|-------|-----|
| Connection refused | Dashboard running? | `docker-compose up -d` |
| No JSON markers | AI generated report? | Ask: "Generate final report" |
| Parse fails | Valid JSON? | Check AI output for syntax |
| Not in Pending | Using correct endpoint? | Use `/from-n8n` not `/reports` |
| IF goes to FALSE | success field present? | Check Code node output |
| 400/500 error | What's the error? | `docker logs vrd-crash-calculator` |

---

## 📝 Sample Test Conversation

**Start with:**
```
Driver: John Smith
Date: November 3, 2025
Chassis: Chassis 02
Event: Round 5 - Qualifying
Car Number: 42
Impact areas: Rear-Left and Rear-Right
Speed: 120 km/h
Barrier: SAFER barrier
Description: Rear impact in Turn 3. Heavy rear suspension damage.
```

**AI will:**
1. Ask clarifying questions
2. Suggest parts from catalog
3. Wait for your confirmation
4. Generate final report with JSON

**You say:**
```
Yes, generate the final report with all suggested parts.
```

**Expected result:**
- n8n execution completes (green)
- Report in http://localhost:8080/pending
- Status: PENDING

---

## 🎨 Expected JSON Format

```json
{
  "driver": "John Smith",
  "date": "2025-11-03",
  "venue": "Chassis 02",
  "event": "Round 5 - Qualifying",
  "accident_damage": "Speed at Impact: 120 km/h\nCar Number: 42\nChassis: Chassis 02\nBarrier Type: SAFER barrier\nImpact Areas: Rear-Left (RL), Rear-Right (RR)\nDescription: Rear impact in Turn 3...",
  "parts": [
    {
      "part_number": "122-18-04-036",
      "part": "Crashbox posteriore",
      "likelihood": "Highly Likely",
      "price": 5000.00,
      "qty": 1
    }
  ]
}
```

---

## 🆘 Emergency Reset

If everything is broken:

```bash
# Stop everything
docker-compose down
cd ~/.n8n  # or wherever n8n stores data
# Back up your n8n data first!

# Restart dashboard fresh
cd /Users/joshholland/crash-calculator-dashboard
docker-compose up -d

# Test basic connectivity
curl http://localhost:8080/api/health

# Reload n8n workflow from backup
# Re-apply all node configurations
```

---

## 📚 Full Documentation

- **Implementation:** `IMPLEMENTATION_GUIDE.md`
- **Testing:** `TESTING.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`

---

## ⏱️ Time Estimates

| Task | Duration |
|------|----------|
| Update AI prompt | 2 minutes |
| Add Code node | 3 minutes |
| Add IF node | 2 minutes |
| Add HTTP node | 5 minutes |
| First test | 5 minutes |
| Troubleshooting | 5-15 minutes |
| **Total** | **20-30 minutes** |

---

## ✨ Success Indicators

You're done when:
- ✅ Chat generates crash report
- ✅ n8n execution completes (all green)
- ✅ Report appears at http://localhost:8080/pending
- ✅ Status badge shows "PENDING"
- ✅ All fields populated correctly
- ✅ Can review and edit in dashboard
- ✅ Can mark as Active or Reviewed
