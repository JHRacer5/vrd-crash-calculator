# 👤 What YOU Need to Do - Action Items

## 📝 Your Task List

I've created all the configuration files and code. Now you need to implement them in n8n.

---

## ✅ Action Item 1: Update AI Agent (5 minutes)

### What to Do:

1. **Open n8n** in your browser
2. **Open workflow:** "Crash Calculator FLOW"
3. **Click on the "AI Agent" node** (the center node with your current system prompt)
4. **Scroll down** to find "System Message" text box
5. **Open this file:** `/Users/joshholland/crash-calculator-dashboard/n8n-integration/ai-agent-system-prompt.txt`
6. **Select ALL text** in that file (Cmd+A)
7. **Copy it** (Cmd+C)
8. **Back in n8n:** Select ALL text in System Message box
9. **Paste** the new prompt (Cmd+V)
10. **Click "Save"** button (top-right of n8n)

### What This Does:
- Tells the AI to output crash reports in structured JSON format
- JSON is wrapped in special markers (`###JSON_START###` and `###JSON_END###`)
- Ensures all required fields are included

### ✓ Done when:
- [ ] System message is updated with new prompt
- [ ] Workflow is saved

---

## ✅ Action Item 2: Add Code Node (5 minutes)

### What to Do:

1. **In n8n workflow editor**
2. **Click the "+" button** on the line coming out of "AI Agent" node
   - Or drag from the left panel: "All" → "Code"
3. **Select "Code" node**
4. **Name it:** "Parse Report Data"
5. **In the node settings:**
   - Language: JavaScript (should be default)
   - Mode: Run Once for All Items
6. **Open this file:** `/Users/joshholland/crash-calculator-dashboard/n8n-integration/code-node-parser.js`
7. **Select ALL code** in that file
8. **Copy it**
9. **Back in n8n Code node:** Delete any placeholder code
10. **Paste** the JavaScript code
11. **Click "Save"**
12. **Draw a connection** from AI Agent output → Parse Report Data input

### What This Does:
- Extracts the JSON from the AI's text response
- Validates all required fields are present
- Formats data for the dashboard API

### ✓ Done when:
- [ ] Code node added
- [ ] JavaScript pasted
- [ ] Connected to AI Agent
- [ ] Node saved

---

## ✅ Action Item 3: Add IF Node (3 minutes) - Optional but Recommended

### What to Do:

1. **Click the "+" button** after "Parse Report Data" node
2. **Search for "IF"** and select it
3. **Name it:** "Check Parse Success"
4. **Configure:**
   - Click "Add Condition"
   - Condition 1:
     - Value 1: `{{ $json.success }}`
     - Operation: Boolean → "is true"
5. **Click "Save"**
6. **Connect:** Parse Report Data output → IF input

### What This Does:
- Checks if parsing was successful
- Routes to dashboard only if data is valid
- Prevents sending bad data

### ✓ Done when:
- [ ] IF node added
- [ ] Condition set to check success = true
- [ ] Connected to Parse Report Data
- [ ] Node saved

---

## ✅ Action Item 4: Add HTTP Request Node (7 minutes)

### What to Do:

1. **Click the "+" button** on the TRUE branch of IF node (green/upper line)
2. **Search for "HTTP Request"** and select it
3. **Name it:** "Send to Dashboard"
4. **Configure these settings:**

   **Authentication:** None

   **Method:** POST

   **URL:** `http://host.docker.internal:8080/api/reports/from-n8n`

   **Send Body:** Toggle ON (switch should be green)

   **Body Content Type:** JSON

   **Specify Body:** Using Fields Below

   **JSON field:** Click in the field and type: `{{ $json.reportData }}`

5. **Click "Add Option"** and select "Timeout"
   - Set to: 30000

6. **Under Headers section:**
   - Click "Add Header"
   - Name: `Content-Type`
   - Value: `application/json`

7. **Under Options:**
   - Response Format: JSON
   - Continue On Fail: Toggle ON (for testing)

8. **Click "Save"**

9. **Connect:** IF node TRUE branch → HTTP Request input

### What This Does:
- Sends the parsed crash report to your dashboard
- Dashboard receives it and marks as "PENDING"
- Returns success confirmation

### ✓ Done when:
- [ ] HTTP Request node added
- [ ] Method set to POST
- [ ] URL correct
- [ ] Body set to {{ $json.reportData }}
- [ ] Headers added
- [ ] Connected to IF TRUE branch
- [ ] Node saved

---

## ✅ Action Item 5: Add Error Handler (2 minutes) - Optional

### What to Do:

1. **Click the "+" button** on the FALSE branch of IF node (red/lower line)
2. **Search for "Stop and Error"** and select it
3. **Name it:** "Parse Failed"
4. **Configure:**
   - Error Message: `Failed to parse crash report. Check AI output has JSON markers.`
5. **Click "Save"**
6. **Connect:** IF node FALSE branch → Stop and Error input

### What This Does:
- Shows clear error if parsing fails
- Helps with debugging
- Prevents silent failures

### ✓ Done when:
- [ ] Stop and Error node added
- [ ] Error message set
- [ ] Connected to IF FALSE branch
- [ ] Node saved

---

## ✅ Action Item 6: Save and Activate (1 minute)

### What to Do:

1. **Click the "Save" button** (top-right corner)
2. **Toggle workflow to "Active"** (switch should be green)
3. **Verify the workflow looks like this:**

```
Chat Trigger
     ↓
  AI Agent
     ↓
Parse Report Data
     ↓
Check Success (IF)
     ├── TRUE → Send to Dashboard
     └── FALSE → Parse Failed
```

### ✓ Done when:
- [ ] Workflow saved
- [ ] Workflow active (green toggle)
- [ ] All nodes connected properly

---

## ✅ Action Item 7: Test It! (10 minutes)

### What to Do:

1. **Find your chat URL:**
   - Click on "When chat message received" node
   - Look for the webhook URL or chat interface URL
   - Open it in a browser

2. **Start a test conversation:**
   ```
   Driver: Test Driver
   Date: November 3, 2025
   Chassis: Chassis 02
   Event: Test Event
   Car Number: 99
   Impact Areas: Rear-Left, Rear-Right
   Speed at Impact: 120 km/h
   Barrier Type: SAFER barrier

   The car had heavy rear impact during Turn 3. Significant damage to rear suspension and bodywork.
   ```

3. **Follow the AI's questions**

4. **When AI asks if you want the final report, say YES**

5. **Wait for AI to complete** (may take 30-60 seconds)

6. **Check n8n execution:**
   - Click "Executions" tab in n8n
   - Look at most recent execution
   - All nodes should have green checkmarks ✓

7. **Check your dashboard:**
   - Open: http://localhost:8080/pending
   - You should see your test report!
   - Status should be "PENDING"
   - Click "Review" to see all the details

### ✓ Done when:
- [ ] Test conversation completed
- [ ] n8n execution successful (all green)
- [ ] Report appears in dashboard Pending section
- [ ] All fields populated correctly

---

## ❌ What If Something Goes Wrong?

### If test fails, check in this order:

1. **Dashboard running?**
   ```bash
   docker ps | grep vrd-crash-calculator
   ```
   If not running: `docker-compose up -d`

2. **n8n execution log has errors?**
   - Click on the failed node
   - Read the error message
   - Check `TROUBLESHOOTING.md` for that specific error

3. **AI didn't output JSON?**
   - Check AI Agent output in execution log
   - Look for `###JSON_START###` markers
   - If missing, ask AI: "Please generate the final report now"

4. **Report not in Pending?**
   - Check "All Reports" page instead
   - Verify using `/from-n8n` endpoint (not `/reports`)
   - Check dashboard logs: `docker logs vrd-crash-calculator`

5. **Still stuck?**
   - Open `TROUBLESHOOTING.md`
   - Look for your specific error
   - Follow the debugging steps

---

## 📚 Reference Documents

As you work through this, you may need:

| If you need... | Open this file... |
|----------------|------------------|
| Detailed step-by-step instructions | `IMPLEMENTATION_GUIDE.md` |
| Quick configuration reference | `QUICK_REFERENCE.md` |
| Comprehensive testing | `TESTING.md` |
| Error solutions | `TROUBLESHOOTING.md` |
| AI prompt to copy | `ai-agent-system-prompt.txt` |
| JavaScript code to copy | `code-node-parser.js` |
| HTTP settings details | `http-request-config.md` |

---

## ⏱️ Time Breakdown

| Action Item | Est. Time |
|-------------|-----------|
| 1. Update AI Agent | 5 min |
| 2. Add Code Node | 5 min |
| 3. Add IF Node | 3 min |
| 4. Add HTTP Request | 7 min |
| 5. Add Error Handler | 2 min |
| 6. Save & Activate | 1 min |
| 7. Test | 10 min |
| **TOTAL** | **30-35 min** |

---

## ✅ Final Checklist

Before you start:
- [ ] Dashboard is running
- [ ] n8n is accessible
- [ ] "Crash Calculator FLOW" workflow is open
- [ ] You have this guide open

After you finish:
- [ ] AI Agent prompt updated
- [ ] Code node added and configured
- [ ] IF node added
- [ ] HTTP Request node added and configured
- [ ] Error handler added (optional)
- [ ] Workflow saved and active
- [ ] Test completed successfully
- [ ] Report visible in dashboard

---

## 🎉 You're Done!

Once all items are checked, your integration is complete!

The workflow will now automatically send all crash reports from n8n to your dashboard's Pending section for team review.

**Next Steps:**
- Test with more realistic crash scenarios
- Fine-tune the AI prompts if needed
- Train your team on the workflow
- Monitor the first few reports
- Consider moving to production when ready

---

## 🆘 Need Help?

1. Check `TROUBLESHOOTING.md` for your issue
2. Review `IMPLEMENTATION_GUIDE.md` for details
3. Test individual components using `TESTING.md`
4. Check n8n execution logs for error messages
5. Check dashboard logs: `docker logs vrd-crash-calculator`

**You've got this!** 🚀
