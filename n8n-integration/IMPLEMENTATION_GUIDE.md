# n8n → Dashboard Integration - Step-by-Step Guide

## 📋 Overview

This guide will walk you through connecting your n8n "Crash Calculator FLOW" workflow to the VRD Crash Calculator Dashboard so that completed crash reports are automatically sent to the dashboard's Pending Reports section.

**Time Required:** 15-20 minutes

---

## ✅ Prerequisites

Before starting, ensure:
- [ ] Dashboard is running on http://localhost:8080
- [ ] n8n is running and you can access the workflow editor
- [ ] "Crash Calculator FLOW" workflow is open in n8n

Test dashboard is accessible:
```bash
curl http://localhost:8080/api/health
```
Expected: `{"status": "healthy", "message": "VRD Crash Calculator API is running"}`

---

## 🔧 Step 1: Update AI Agent System Prompt

**What this does:** Instructs the AI to output crash reports in a structured JSON format that the dashboard can understand.

### Instructions:

1. **Open your n8n workflow** "Crash Calculator FLOW"

2. **Click on the "AI Agent" node** (the one in the middle of the canvas)

3. **Scroll down to find "System Message"** field

4. **Copy the ENTIRE contents** of this file:
   ```
   /Users/joshholland/crash-calculator-dashboard/n8n-integration/ai-agent-system-prompt.txt
   ```

5. **Replace the existing system message** with the new one

6. **Important changes in the new prompt:**
   - AI now outputs both human-readable report AND JSON
   - JSON is wrapped in `###JSON_START###` and `###JSON_END###` markers
   - Ensures all required fields are included

7. **Click "Save"** button in top-right of n8n

---

## 🔧 Step 2: Add Code Node (Parse Report)

**What this does:** Extracts the JSON data from the AI's response and validates it.

### Instructions:

1. **Click the "+" button** on the connection line after "AI Agent" node
   - Or drag a new node from the left panel

2. **Search for "Code"** and select the "Code" node

3. **Name it:** "Parse Report Data"

4. **In the Code node settings:**
   - Language: JavaScript
   - Mode: Run Once for All Items

5. **Copy the ENTIRE contents** of this file:
   ```
   /Users/joshholland/crash-calculator-dashboard/n8n-integration/code-node-parser.js
   ```

6. **Paste into the code editor** (delete any placeholder code first)

7. **Click "Save"**

8. **Connect the nodes:**
   - Draw a line from "AI Agent" output to "Parse Report Data" input

---

## 🔧 Step 3: Add IF Node (Optional but Recommended)

**What this does:** Checks if the report was parsed successfully before sending to dashboard.

### Instructions:

1. **Click the "+" button** after "Parse Report Data" node

2. **Search for "IF"** and select the "IF" node

3. **Name it:** "Check Parse Success"

4. **Configure the condition:**
   - **Condition 1:**
     - Value 1: `{{ $json.success }}`
     - Operation: `Boolean` → `is true`

5. **Click "Save"**

6. **Connect:** Parse Report Data → Check Parse Success

---

## 🔧 Step 4: Add HTTP Request Node (Send to Dashboard)

**What this does:** Sends the parsed crash report to your dashboard API.

### Instructions:

1. **Click the "+" button** on the **TRUE branch** of the IF node
   - This is the green/upper output

2. **Search for "HTTP Request"** and select it

3. **Name it:** "Send to Dashboard"

4. **Configure the HTTP Request:**

   **Authentication:** None

   **Method:** POST

   **URL:** `http://host.docker.internal:8080/api/reports/from-n8n`

   **Send Body:** Toggle ON

   **Body Content Type:** JSON

   **Specify Body:** Using Fields Below

   **JSON:**
   ```
   {{ $json.reportData }}
   ```

5. **Click on "Add Option"** and add:
   - **Timeout:** 30000

6. **Headers section - Add Header:**
   - Name: `Content-Type`
   - Value: `application/json`

7. **Options:**
   - Response Format: JSON
   - Continue On Fail: Toggle ON (recommended for testing)

8. **Click "Save"**

---

## 🔧 Step 5: Add Error Notification (Optional)

**What this does:** Notifies you if report parsing fails.

### Instructions:

1. **Click the "+" button** on the **FALSE branch** of the IF node
   - This is the red/lower output

2. **Search for "Stop and Error"** and select it

3. **Name it:** "Parse Failed"

4. **Configure:**
   - Error Message: `Failed to parse crash report from AI. Check that the AI generated a complete report with JSON markers.`

5. **Click "Save"**

---

## 🔧 Step 6: Activate and Save Workflow

### Instructions:

1. **Review your workflow** - it should look like:
   ```
   Chat Trigger → AI Agent → Parse Report Data → IF Node
                                                    ├─ TRUE → Send to Dashboard
                                                    └─ FALSE → Parse Failed
   ```

2. **Click "Save" button** (top-right)

3. **Toggle the workflow "Active"** (top-right switch should be green)

---

## 🧪 Step 7: Test the Integration

### Test Procedure:

1. **Open your chat interface**
   - Go to the n8n chat URL (usually shown in the "When chat message received" node)

2. **Start a test conversation:**
   ```
   Driver: John Smith
   Date: Today
   Chassis: Chassis 02
   Event: Round 5 - Qualifying
   Car Number: 42
   Impact areas: Rear-Left and Rear-Right
   Speed at impact: 120 km/h
   Barrier type: SAFER barrier

   The car hit the barrier in turn 3. Significant rear damage visible.
   ```

3. **Follow the AI's prompts** to build the crash report

4. **When AI asks if you want to generate the final report, say YES**

5. **Watch for:**
   - AI outputs human-readable report
   - AI outputs JSON block with markers
   - n8n execution completes successfully

6. **Check n8n execution log:**
   - Click on "Executions" tab
   - Look at the most recent execution
   - Verify all nodes executed successfully (green checkmarks)
   - Check "Send to Dashboard" node output for success response

7. **Check your dashboard:**
   - Navigate to: http://localhost:8080/pending
   - You should see your test report with status "PENDING"
   - Click "Review" to verify all data was captured

---

## ✅ Success Criteria

Your integration is working correctly if:

- [ ] AI generates crash report with JSON markers
- [ ] Parse Report Data node shows `success: true`
- [ ] IF node routes to TRUE branch
- [ ] Send to Dashboard node returns `{ "success": true, "status": "pending" }`
- [ ] Report appears in dashboard Pending section
- [ ] All fields (driver, date, chassis, parts, etc.) are populated correctly
- [ ] You can review and edit the report in the dashboard

---

## 🆘 What If Something Goes Wrong?

See `TROUBLESHOOTING.md` for common issues and solutions.

---

## 📝 Notes

- Reports sent via n8n are marked as "PENDING" status
- Manual reports created in dashboard are marked as "ACTIVE" status
- You can change status at any time from the report view
- The AI may take 30-60 seconds to generate a complete report with parts pricing
- The dashboard can handle reports with 0 parts (AI can add "Unable to determine parts" message)

---

## 🔄 Next Steps After Successful Integration

Once you've verified the integration works:

1. **Test with real crash scenarios** from your team
2. **Fine-tune the AI prompts** if needed for better part identification
3. **Add more chassis options** to the form if needed
4. **Train your team** on the workflow
5. **Monitor the pending reports** dashboard for incoming submissions

---

## 📞 Need Help?

If you get stuck:
1. Check the n8n execution log for error messages
2. Check the dashboard API logs: `docker logs vrd-crash-calculator`
3. Refer to TROUBLESHOOTING.md
4. Test each component individually (see TESTING.md)
