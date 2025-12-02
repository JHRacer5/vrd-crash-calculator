# n8n → Dashboard Integration Package

## 📦 What's in This Package

This directory contains everything you need to connect your n8n "Crash Calculator FLOW" workflow to the VRD Crash Calculator Dashboard.

### Files Included:

| File | Purpose |
|------|---------|
| **IMPLEMENTATION_GUIDE.md** | Step-by-step setup instructions (START HERE) |
| **QUICK_REFERENCE.md** | One-page cheat sheet for quick lookup |
| **TESTING.md** | Comprehensive testing procedures |
| **TROUBLESHOOTING.md** | Common issues and solutions |
| **ai-agent-system-prompt.txt** | Updated AI prompt (copy/paste into n8n) |
| **code-node-parser.js** | JavaScript for parsing AI output (copy/paste into n8n) |
| **http-request-config.md** | HTTP Request node configuration details |

---

## 🚀 Quick Start

### For First-Time Setup:

1. **Read:** `IMPLEMENTATION_GUIDE.md` (15 min read)
2. **Follow:** Step-by-step instructions in the guide
3. **Test:** Use procedures in `TESTING.md`
4. **Troubleshoot:** Reference `TROUBLESHOOTING.md` if issues arise

**Total Time:** 30-45 minutes

### For Quick Reference:

Open `QUICK_REFERENCE.md` for URLs, commands, and configuration snippets.

---

## 🎯 What This Integration Does

### Before Integration:
- ✅ n8n AI agent generates crash reports in chat
- ❌ Reports only exist in chat history
- ❌ No centralized tracking
- ❌ No review workflow
- ❌ Reports lost when chat closed

### After Integration:
- ✅ n8n AI agent generates crash reports in chat
- ✅ **Reports automatically sent to dashboard**
- ✅ **Appear in "Pending Reports" section**
- ✅ **Team can review and approve reports**
- ✅ **Track all crashes in one place**
- ✅ **Edit, update, and manage reports**
- ✅ **Calculate total costs across all crashes**

---

## 📊 Workflow Overview

```
User → n8n Chat → AI Agent → Parse JSON → Dashboard API → Pending Reports
```

**Detailed Flow:**

1. **User starts chat** with crash details (driver, chassis, damage)
2. **AI Agent analyzes** crash using Pinecone vector stores
3. **AI suggests parts** based on damage description
4. **User confirms** parts to include
5. **AI generates report** with human-readable text + JSON data
6. **Code node extracts** JSON from AI response
7. **IF node validates** parsing was successful
8. **HTTP Request sends** report to dashboard API
9. **Dashboard receives** report and marks as "PENDING"
10. **Team reviews** report in dashboard Pending section
11. **Approved report** moves to Active/Reviewed status

---

## 🛠️ Technical Architecture

### n8n Nodes Added:

```
AI Agent (existing)
    │
    └─> Parse Report Data (Code)
            │
            └─> Check Success (IF)
                    ├─ TRUE ─> Send to Dashboard (HTTP Request) ─> Dashboard
                    │
                    └─ FALSE ─> Error Handler
```

### Data Flow:

```
AI Output (text):
"Here's your report...
###JSON_START###
{
  "driver": "...",
  "parts": [...]
}
###JSON_END###"
          ↓
Code Node extracts JSON
          ↓
{
  "success": true,
  "reportData": {
    "driver": "...",
    "date": "2025-11-03",
    "parts": [...]
  }
}
          ↓
HTTP POST to Dashboard
          ↓
Dashboard Response:
{
  "success": true,
  "status": "pending",
  "report": { "id": 123, ... }
}
```

### Dashboard API Endpoint:

```
POST http://host.docker.internal:8080/api/reports/from-n8n

Headers:
  Content-Type: application/json

Body:
{
  "driver": "string",
  "date": "YYYY-MM-DD",
  "venue": "string (chassis)",
  "event": "string",
  "accident_damage": "string (detailed description)",
  "parts": [
    {
      "part_number": "string",
      "part": "string",
      "likelihood": "Highly Likely|Likely|Possible",
      "price": number,
      "qty": number
    }
  ]
}

Response:
{
  "success": true,
  "message": "Report created successfully and marked as PENDING for review",
  "status": "pending",
  "report": { ... }
}
```

---

## 📋 Prerequisites

### Required:

- [x] Dashboard running on Docker (port 8080)
- [x] n8n installed and running (local or Docker)
- [x] "Crash Calculator FLOW" workflow accessible
- [x] OpenAI API key configured in n8n
- [x] Pinecone vector stores set up in n8n

### Verify:

```bash
# Dashboard is running
docker ps | grep vrd-crash-calculator

# Dashboard is healthy
curl http://localhost:8080/api/health

# n8n workflow is accessible
# Open n8n UI and see "Crash Calculator FLOW"
```

---

## 🎓 Implementation Steps (Summary)

Full details in `IMPLEMENTATION_GUIDE.md`, but here's the overview:

### Step 1: Update AI Agent System Prompt
- Open AI Agent node in n8n
- Copy contents of `ai-agent-system-prompt.txt`
- Paste into System Message field
- Save

### Step 2: Add Code Node
- Add new Code node after AI Agent
- Copy contents of `code-node-parser.js`
- Paste into code editor
- Connect AI Agent → Code node
- Save

### Step 3: Add IF Node (optional but recommended)
- Add IF node after Code node
- Condition: `{{ $json.success }}` = true
- Connect Code → IF
- Save

### Step 4: Add HTTP Request Node
- Add HTTP Request node after IF (TRUE branch)
- Method: POST
- URL: `http://host.docker.internal:8080/api/reports/from-n8n`
- Body: `{{ $json.reportData }}`
- Headers: Content-Type: application/json
- Connect IF (TRUE) → HTTP Request
- Save

### Step 5: Activate Workflow
- Click Save
- Toggle workflow Active
- Ready to test!

---

## 🧪 Testing

See `TESTING.md` for comprehensive testing procedures.

### Quick Test:

1. **Open n8n chat** (get URL from "When chat message received" node)

2. **Start conversation:**
   ```
   Driver: Test Driver
   Date: November 3, 2025
   Chassis: Chassis 02
   Event: Test Event
   Impact: Rear damage
   Speed: 100 km/h
   ```

3. **Follow AI prompts**, confirm parts

4. **Ask AI to generate final report**

5. **Check dashboard:** http://localhost:8080/pending

6. **Verify report appears** with status "PENDING"

**Success = Report visible in Pending section!**

---

## 🔍 Troubleshooting

See `TROUBLESHOOTING.md` for detailed solutions.

### Top 3 Issues:

#### 1. Connection Refused
- **Cause:** Dashboard not running
- **Fix:** `docker-compose up -d`

#### 2. JSON Markers Not Found
- **Cause:** AI hasn't generated final report yet
- **Fix:** Tell AI: "Generate the final report now"

#### 3. Report Not in Pending
- **Cause:** Wrong endpoint or status
- **Fix:** Verify using `/api/reports/from-n8n` endpoint

---

## 📚 Documentation Index

### For Setup:
- **New to integration?** → Start with `IMPLEMENTATION_GUIDE.md`
- **Quick lookup?** → Use `QUICK_REFERENCE.md`
- **Something broken?** → Check `TROUBLESHOOTING.md`
- **Want to test thoroughly?** → Follow `TESTING.md`

### For Reference:
- **AI prompt template** → `ai-agent-system-prompt.txt`
- **Parser code** → `code-node-parser.js`
- **HTTP config** → `http-request-config.md`

---

## ⏱️ Time Estimates

| Phase | Duration |
|-------|----------|
| **Read documentation** | 15 minutes |
| **Update AI prompt** | 2 minutes |
| **Add Code node** | 3 minutes |
| **Add IF node** | 2 minutes |
| **Add HTTP node** | 5 minutes |
| **Save and activate** | 1 minute |
| **First test** | 5 minutes |
| **Troubleshooting (if needed)** | 10-20 minutes |
| **Comprehensive testing** | 15 minutes |
| **Total (smooth run)** | **30 minutes** |
| **Total (with issues)** | **45-60 minutes** |

---

## ✅ Success Checklist

You're done when:

- [ ] AI Agent system prompt updated
- [ ] Code node added and configured
- [ ] IF node added (optional)
- [ ] HTTP Request node added and configured
- [ ] Workflow saved and activated
- [ ] Test conversation completed
- [ ] Report appeared in http://localhost:8080/pending
- [ ] Report shows status "PENDING"
- [ ] All fields populated correctly (driver, date, event, parts)
- [ ] Can click "Review" and see full report
- [ ] Can edit report in dashboard
- [ ] Can mark as Active or Reviewed
- [ ] Dashboard stats update correctly

---

## 🎉 After Successful Integration

### Immediate Next Steps:

1. **Test with real crash scenarios** from your team
2. **Fine-tune AI prompts** if part suggestions need improvement
3. **Train team members** on the workflow
4. **Document any custom configurations** you made
5. **Set up monitoring** to catch failed submissions

### Future Enhancements:

- Add email notifications when new reports arrive
- Create automated reports summary (daily/weekly)
- Add more chassis types if fleet expands
- Implement approval workflow with multiple reviewers
- Export reports to PDF for insurance/documentation
- **Move to production** (see main dashboard README for production checklist)

---

## 🆘 Need Help?

### Debugging Steps:

1. Check `TROUBLESHOOTING.md` for your specific issue
2. Look at n8n execution log for errors
3. Check dashboard logs: `docker logs vrd-crash-calculator`
4. Test API directly with curl (examples in `TESTING.md`)
5. Verify each node output in n8n execution view

### Information to Gather:

If you need further assistance, gather:
- n8n execution log (screenshot or text)
- Dashboard logs (last 50 lines)
- Error messages (exact text)
- What you expected vs what happened
- Steps to reproduce the issue

---

## 📄 Version Information

- **Integration Version:** 1.0
- **Dashboard Version:** Latest (from /Users/joshholland/crash-calculator-dashboard)
- **Compatible with:** n8n 1.x (tested with latest)
- **Last Updated:** November 3, 2025

---

## 🔗 Related Documentation

- **Dashboard Main README:** `/Users/joshholland/crash-calculator-dashboard/README.md`
- **Pending Reports Guide:** `/Users/joshholland/crash-calculator-dashboard/PENDING_REPORTS_GUIDE.md`
- **API Documentation:** Dashboard http://localhost:8080/n8n-integration

---

## 📞 Quick Links

| Resource | URL/Path |
|----------|----------|
| Dashboard | http://localhost:8080 |
| Pending Reports | http://localhost:8080/pending |
| Integration Guide | http://localhost:8080/n8n-integration |
| Implementation Steps | `IMPLEMENTATION_GUIDE.md` |
| Quick Reference | `QUICK_REFERENCE.md` |
| Testing Guide | `TESTING.md` |
| Troubleshooting | `TROUBLESHOOTING.md` |

---

**Ready to get started?** Open `IMPLEMENTATION_GUIDE.md` and let's connect your n8n workflow to the dashboard! 🚀
