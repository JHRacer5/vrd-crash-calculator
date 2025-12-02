# Testing Guide - n8n Dashboard Integration

## 🧪 Testing Strategy

Test each component individually before testing the full workflow.

---

## Test 1: Dashboard API Connectivity

**Purpose:** Verify n8n can reach the dashboard API

### From Terminal:

```bash
# Test health endpoint
curl http://host.docker.internal:8080/api/health

# Expected response:
# {"status": "healthy", "message": "VRD Crash Calculator API is running"}
```

**If this fails:**
- Dashboard not running: `docker-compose ps` to check
- Wrong URL: Try `http://localhost:8080/api/health`
- Port conflict: Check nothing else is on port 8080

---

## Test 2: Dashboard API - Create Report

**Purpose:** Verify the API endpoint accepts crash reports

### From Terminal:

```bash
curl -X POST http://host.docker.internal:8080/api/reports/from-n8n \
  -H "Content-Type: application/json" \
  -d '{
    "driver": "Test Driver API",
    "date": "2025-11-03",
    "venue": "Chassis 02",
    "event": "API Test Event",
    "accident_damage": "Testing API endpoint directly",
    "parts": [
      {
        "part_number": "TEST-001",
        "part": "Test Part",
        "likelihood": "Likely",
        "price": 100.50,
        "qty": 1
      }
    ]
  }'
```

### Expected Response:

```json
{
  "success": true,
  "message": "Report created successfully and marked as PENDING for review",
  "status": "pending",
  "report": {
    "id": 4,
    "driver": "Test Driver API",
    "date": "2025-11-03",
    "status": "pending",
    ...
  }
}
```

**Verify in Dashboard:**
1. Open http://localhost:8080/pending
2. You should see "Test Driver API" report
3. Status should be "PENDING"

**If report appears:** ✅ API is working correctly!

---

## Test 3: AI Agent JSON Output

**Purpose:** Verify AI generates correct JSON format

### In n8n:

1. **Temporarily disconnect** the Parse Report Data node from AI Agent
2. **Run workflow** with test conversation
3. **Look at AI Agent output** in execution log
4. **Check for:**
   - Human-readable report text
   - `###JSON_START###` marker
   - Valid JSON structure
   - `###JSON_END###` marker

### Sample Expected Output:

```
Here's your crash report:

Driver: John Smith
Date: November 3, 2025
...
[human readable content]
...

###JSON_START###
{
  "driver": "John Smith",
  "date": "2025-11-03",
  "venue": "Chassis 02",
  "event": "Round 5",
  "accident_damage": "Speed at Impact: 120 km/h...",
  "parts": [...]
}
###JSON_END###
```

**If JSON markers are missing:**
- AI didn't generate final report yet
- System prompt not updated correctly
- Try asking AI: "Please generate the final crash report now"

---

## Test 4: Code Node Parsing

**Purpose:** Verify the parser extracts JSON correctly

### In n8n:

1. **Reconnect** Parse Report Data node
2. **Run workflow** again
3. **Check Parse Report Data node output:**

### Expected Output:

```json
{
  "success": true,
  "reportData": {
    "driver": "John Smith",
    "date": "2025-11-03",
    "venue": "Chassis 02",
    "event": "Round 5",
    "accident_damage": "...",
    "parts": [...]
  },
  "message": "Crash report parsed successfully"
}
```

**If success is false:**
- Check error message in output
- Verify AI output has correct markers
- Check browser console for parsing errors

---

## Test 5: Full End-to-End Test

**Purpose:** Test complete workflow from chat to dashboard

### Test Scenarios:

#### Scenario A: Simple Rear Impact

**Input to chat:**
```
Driver: Jane Doe
Date: November 3, 2025
Chassis: Chassis 03
Event: Round 6 - Practice
Car Number: 15
Impact Areas: Rear-Left, Rear-Right, Center-Rear
Speed at Impact: 85 mph
Barrier: Tire wall
Description: Lost control in Turn 8, backed into tire barrier. Moderate rear damage.
```

**Expected Parts (examples):**
- Crashbox posteriore
- Rear wishbones
- Rear wing
- Rear rims/wheels

**Verify:**
- [ ] AI suggests appropriate parts
- [ ] Parts have pricing (or marked as N/A)
- [ ] Report has JSON markers
- [ ] Parse successful
- [ ] Dashboard receives report
- [ ] Report in Pending section
- [ ] All fields populated

---

#### Scenario B: Front Impact

**Input to chat:**
```
Driver: Mike Johnson
Date: November 3, 2025
Chassis: Chassis 01
Event: Round 6 - Qualifying
Impact Areas: Front-Left, Front-Right, Center-Front
Speed at Impact: 145 km/h
Barrier: SAFER barrier
Description: Locked up brakes entering Turn 1, straight-on impact with barrier. Heavy front-end damage.
```

**Expected Parts (examples):**
- Front crashbox
- Front wishbones
- Front wing
- Nose cone
- Front wheels

**Verify same checklist as Scenario A**

---

#### Scenario C: Minimal Damage (Edge Case)

**Input to chat:**
```
Driver: Sarah Williams
Date: November 3, 2025
Chassis: Chassis 02
Event: Round 6 - Race
Impact Areas: Mid-Left
Speed at Impact: 45 km/h
Description: Side contact with another car. Minor bodywork damage, likely just cosmetic.
```

**Expected:**
- AI might suggest few or no parts
- AI might mark parts as "Unlikely" or "Possible"
- Report should still be created

**Verify:**
- [ ] Report created even with minimal parts
- [ ] Dashboard accepts empty or minimal parts array
- [ ] Report still reviewable

---

## Test 6: Error Handling

**Purpose:** Verify system handles errors gracefully

### Test: Dashboard Offline

1. **Stop dashboard:** `docker-compose down`
2. **Run n8n workflow** to completion
3. **Expected:**
   - HTTP Request node shows error
   - Workflow continues (doesn't crash)
   - Error is logged

4. **Restart dashboard:** `docker-compose up -d`
5. **Re-run workflow:** Report should go through

---

### Test: Malformed Data

**In n8n Code node, temporarily modify output:**

```javascript
return [{
  json: {
    success: true,
    reportData: {
      driver: "Test",
      // Missing required fields
    }
  }
}];
```

**Expected:**
- Dashboard API returns error
- HTTP Request node shows failure
- Error message helpful for debugging

**Remember to revert changes after testing!**

---

## Test 7: Dashboard Review Workflow

**Purpose:** Verify complete workflow including review

1. **Generate report via n8n** (use any test scenario)
2. **Check dashboard pending section:** http://localhost:8080/pending
3. **Click "Review" button** on the report
4. **Verify:**
   - [ ] All fields display correctly
   - [ ] Status badge shows "Pending"
   - [ ] Parts table populated
   - [ ] Total cost calculated
   - [ ] Can edit fields
   - [ ] Can add/remove parts

5. **Click "Mark as Reviewed"**
6. **Verify:**
   - [ ] Status changes to "Reviewed"
   - [ ] Badge turns green
   - [ ] Report removed from Pending section
   - [ ] Report shows in All Reports

---

## Test 8: Multiple Reports

**Purpose:** Test concurrent report handling

1. **Generate 3 reports** back-to-back via n8n
2. **Check dashboard:**
   - [ ] All 3 appear in Pending
   - [ ] Counter shows "3"
   - [ ] Each has unique ID
   - [ ] Can review each independently

3. **Mark one as active**
4. **Check:**
   - [ ] Counter now shows "2"
   - [ ] Only 2 remain in Pending

---

## 🎯 Quick Test Checklist

Before calling it done, verify:

- [ ] AI outputs JSON with markers
- [ ] Parser extracts JSON successfully
- [ ] Dashboard receives POST request
- [ ] Report appears in Pending section
- [ ] Report has all fields populated
- [ ] Can review and edit report
- [ ] Can mark as Active or Reviewed
- [ ] Dashboard stats update correctly
- [ ] Multiple reports work fine
- [ ] Error handling works (IF node catches failures)

---

## 📊 Test Results Template

Use this to track your testing:

```
Date: ___________
Tester: ___________

✅ Test 1: API Connectivity - PASS / FAIL
   Notes:

✅ Test 2: API Create Report - PASS / FAIL
   Notes:

✅ Test 3: AI JSON Output - PASS / FAIL
   Notes:

✅ Test 4: Code Parsing - PASS / FAIL
   Notes:

✅ Test 5: End-to-End - PASS / FAIL
   Scenario A: PASS / FAIL
   Scenario B: PASS / FAIL
   Scenario C: PASS / FAIL
   Notes:

✅ Test 6: Error Handling - PASS / FAIL
   Notes:

✅ Test 7: Dashboard Review - PASS / FAIL
   Notes:

✅ Test 8: Multiple Reports - PASS / FAIL
   Notes:

Overall Status: READY / NEEDS WORK
```

---

## 🔍 Debugging Tips

**If report not appearing in dashboard:**
1. Check n8n execution log - was HTTP request successful?
2. Check dashboard logs: `docker logs vrd-crash-calculator`
3. Verify URL is correct (host.docker.internal vs localhost)
4. Test API directly with curl

**If JSON parsing fails:**
1. Check AI output in execution log
2. Look for JSON markers
3. Verify JSON is valid (use jsonlint.com)
4. Check for special characters breaking JSON

**If parts missing or wrong:**
1. Review AI system prompt
2. Check Pinecone queries are working
3. Verify part names match catalog
4. Test with simpler scenarios first

---

## ✅ When All Tests Pass

Congratulations! Your integration is working. Next steps:

1. Document any custom configurations
2. Train users on the workflow
3. Monitor first few real reports
4. Collect feedback and iterate
5. Consider moving to production (see PRODUCTION_CHECKLIST.md)
