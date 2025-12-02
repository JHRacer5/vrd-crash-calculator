# Pending Reports & n8n Integration Guide

## 🎉 What's New

Your dashboard now has a complete **Pending Reports System** that integrates seamlessly with n8n workflows!

### New Features

1. **Pending Reports Section** - Reports from n8n await your review
2. **n8n Integration Page** - Complete guide and test interface
3. **Report Status System** - Track reports as pending, active, or reviewed
4. **Dashboard Pending Counter** - See pending reports at a glance

---

## 📋 Report Status Workflow

### Status Types

- **🟠 PENDING** - New reports from n8n workflow awaiting review
- **🔴 ACTIVE** - Reports being worked on or manually created
- **🟢 REVIEWED** - Finalized and approved reports

### Workflow

```
n8n Workflow → Pending → Review → Active → Reviewed
```

---

## 🚀 Quick Start

### 1. Dashboard Overview

Visit: **http://localhost:8080**

The first stat card now shows **Pending Review** count in orange. Click it to go directly to pending reports.

### 2. Pending Reports Page

Visit: **http://localhost:8080/pending**

Features:
- See all reports awaiting review
- Orange alert banner shows pending count
- Review button to view/edit each report
- Quick "✓" button to mark as active without reviewing
- Auto-refreshes every 30 seconds

### 3. n8n Integration Page

Visit: **http://localhost:8080/n8n-integration**

Features:
- Complete API documentation
- Copy-paste endpoint URL
- JSON payload example
- n8n node configuration guide
- Test button to verify integration
- Additional API endpoints reference

---

## 🔗 n8n Workflow Integration

### Update Your n8n Workflow

**Change the endpoint from:**
```
http://localhost:8080/api/reports
```

**To:**
```
http://host.docker.internal:8080/api/reports/from-n8n
```

### What This Does

- Reports created through `/api/reports/from-n8n` are automatically marked as **PENDING**
- They appear in the Pending Reports section
- Users are notified to review and approve them
- After review, they can be marked as Active or Reviewed

### n8n HTTP Request Node Configuration

```
Method: POST
URL: http://host.docker.internal:8080/api/reports/from-n8n
Authentication: None
Body Type: JSON
Headers: Content-Type: application/json
```

### JSON Payload Format

```json
{
  "driver": "John Smith",
  "date": "2025-11-03",
  "venue": "Laguna Seca",
  "event": "Round 5",
  "accident_damage": "Rear impact description",
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

## 📊 New API Endpoints

### 1. Create Pending Report (n8n)
```http
POST http://localhost:8080/api/reports/from-n8n
```
Creates report with **status=pending**

**Response:**
```json
{
  "success": true,
  "message": "Report created successfully and marked as PENDING for review",
  "status": "pending",
  "report": { ... }
}
```

---

### 2. Get Pending Reports
```http
GET http://localhost:8080/api/reports/pending
```
Returns array of all pending reports

---

### 3. Update Report Status
```http
PUT http://localhost:8080/api/reports/{id}/status
Content-Type: application/json

{
  "status": "active"  // or "pending" or "reviewed"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Report status updated to active",
  "report": { ... }
}
```

---

## 🎯 User Workflow Examples

### Scenario 1: n8n Creates Report

1. n8n workflow processes crash data
2. Sends POST to `/api/reports/from-n8n`
3. Report created with status=pending
4. Dashboard shows "1" in Pending Review card (orange)
5. User clicks Pending Review or navigates to Pending Reports
6. User sees report in orange banner section
7. User clicks "Review" button
8. User reviews and edits details
9. User clicks "Mark as Reviewed"
10. Report moves to reviewed status

### Scenario 2: Quick Approval

1. User sees pending report
2. Clicks "✓" button directly in table
3. Report immediately marked as active
4. User can still edit later if needed

### Scenario 3: Manual Creation

1. User clicks "New Report" in sidebar
2. Fills out form manually
3. Saves report
4. Report created with status=active (not pending)
5. No review needed since user created it

---

## 🎨 UI Updates

### Navigation

New sidebar items:
- **⏳ Pending Reports** - Second item (orange when active)
- **🔗 n8n Integration** - Before API Status

### Dashboard Stats

First card now shows:
- **Label:** Pending Review
- **Value:** Count (in orange)
- **Icon:** ⏳
- **Clickable:** Takes you to /pending

### Report View Page

When viewing a report:
- **Status Badge** shows current status (Pending/Active/Reviewed)
- **Mark as Reviewed Button** appears for pending/active reports
- Badge colors: Orange (pending), Red (active), Green (reviewed)

---

## 🧪 Testing

### Test the n8n Endpoint

**Option 1: Use the UI**
1. Go to http://localhost:8080/n8n-integration
2. Click "Send Test Report" button
3. View test report in Pending Reports

**Option 2: Use cURL**
```bash
curl -X POST http://localhost:8080/api/reports/from-n8n \
  -H "Content-Type: application/json" \
  -d '{
    "driver": "Test Driver",
    "date": "2025-11-03",
    "venue": "Test Track",
    "event": "Test Event",
    "accident_damage": "Test damage",
    "parts": [{
      "part_number": "TEST-001",
      "part": "Test Part",
      "likelihood": "Likely",
      "price": 100.00,
      "qty": 1
    }]
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "status": "pending",
  "report": { "id": 1, "status": "pending", ... }
}
```

### Verify Pending Report

1. Visit: http://localhost:8080/pending
2. Should see your test report
3. Click "Review" to view details
4. Status badge should be orange "Pending"

### Test Status Update

```bash
curl -X PUT http://localhost:8080/api/reports/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}'
```

---

## 📍 Key Pages

| Page | URL | Purpose |
|------|-----|---------|
| Dashboard | http://localhost:8080 | Overview with pending count |
| Pending Reports | http://localhost:8080/pending | Review n8n reports |
| n8n Integration | http://localhost:8080/n8n-integration | API docs and testing |
| All Reports | http://localhost:8080/reports | All reports (any status) |
| Create Report | http://localhost:8080/reports/new | Manual entry (active) |

---

## 🔄 Migration from Old System

If you have existing reports in the database:
- They will have `status=active` by default
- No action needed
- Everything continues working as before
- Only NEW reports from n8n get `status=pending`

---

## 💡 Tips

1. **Dashboard Alert** - Orange pending card is clickable
2. **Auto-Refresh** - Pending page auto-refreshes every 30 seconds
3. **Quick Approve** - Use "✓" button to skip detailed review
4. **Status Changes** - Can change status anytime from report view
5. **Test Endpoint** - Use the test button on integration page to verify n8n connection

---

## ✅ What You Can Do Now

- ✅ See pending reports count on dashboard
- ✅ Review reports from n8n workflow
- ✅ Mark reports as active or reviewed
- ✅ Test n8n integration directly from UI
- ✅ Track report status throughout lifecycle
- ✅ All previous functionality still works
- ✅ Manual reports bypass pending (go straight to active)

---

## 🎉 Summary

Your crash calculator dashboard now has a **complete pending reports system**:

1. **n8n Integration** - Dedicated endpoint at `/api/reports/from-n8n`
2. **Pending Section** - See all reports awaiting review
3. **Status Tracking** - Pending → Active → Reviewed
4. **Dashboard Widget** - Orange card shows pending count
5. **Integration Guide** - Complete docs at `/n8n-integration`
6. **Test Interface** - Built-in testing from the UI

**Update your n8n workflow to use the new endpoint and reports will automatically appear in the pending section for your review!**

---

**Dashboard:** http://localhost:8080
**Pending Reports:** http://localhost:8080/pending
**n8n Integration:** http://localhost:8080/n8n-integration
