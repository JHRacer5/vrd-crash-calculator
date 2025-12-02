# VRD Crash Calculator - Quick Start Guide

## ✅ Status: Running

Your dashboard is **LIVE** at: **http://localhost:8080**

## 🚀 What's Deployed

- **Web Dashboard**: http://localhost:8080
- **API Endpoint**: http://localhost:8080/api
- **Container**: `vrd-crash-calculator` running on Docker
- **Port**: 8080 (n8n on 5678 is safe)
- **Database**: SQLite at `instance/crash_reports.db`

## 🔑 Key URLs

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:8080 |
| API Health | http://localhost:8080/api/health |
| All Reports | http://localhost:8080/api/reports |
| n8n Endpoint | http://host.docker.internal:8080/api/reports |

## 🎯 Next Steps for n8n Integration

### 1. Update Your n8n Workflow

In your "Crash Calculator" workflow:

**Add HTTP Request Node:**
- Method: `POST`
- URL: `http://host.docker.internal:8080/api/reports`
- Body: Raw JSON

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

### 2. Update AI Agent Prompt

Add to the end of your AI Agent system message:

```
When you complete the assessment, output data in this JSON format:
{
  "driver": "Driver Name",
  "date": "YYYY-MM-DD",
  "venue": "Venue Name",
  "event": "Event Name",
  "accident_damage": "Description",
  "parts": [
    {
      "part_number": "123-456",
      "part": "Part Name",
      "likelihood": "Highly Likely",
      "price": 1234.56,
      "qty": 1
    }
  ]
}
```

## 📋 Docker Commands

```bash
# View status
docker ps | grep vrd-crash-calculator

# View logs
cd ~/crash-calculator-dashboard
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down

# Start again
docker-compose up -d

# Rebuild and start
docker-compose up -d --build
```

## 🧪 Test the API

### Health Check
```bash
curl http://localhost:8080/api/health
```

### Create Test Report
```bash
curl -X POST http://localhost:8080/api/reports \
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

### Get All Reports
```bash
curl http://localhost:8080/api/reports
```

## 📊 Sample Data Already Loaded

Report ID: 1
- Driver: John Smith
- Venue: Laguna Seca
- Event: Round 5 - Qualifying
- Total: $7,500.00

Visit http://localhost:8080 to see it in the dashboard.

## 🔧 Troubleshooting

### Dashboard won't load
```bash
# Check if container is running
docker ps | grep vrd-crash-calculator

# Check logs for errors
docker-compose -f ~/crash-calculator-dashboard/docker-compose.yml logs
```

### n8n can't connect
- Use `http://host.docker.internal:8080` (not localhost)
- Or add both containers to same network (see N8N_INTEGRATION_GUIDE.md)

### Port conflict
Edit `docker-compose.yml` and change `"8080:8080"` to `"8081:8080"`

## 📚 Documentation

- **Full API Docs**: See `README.md`
- **n8n Integration**: See `N8N_INTEGRATION_GUIDE.md`
- **Project Location**: `~/crash-calculator-dashboard`

## 🎉 Features

✅ Web dashboard with crash report management
✅ REST API for n8n integration
✅ SQLite database for persistent storage
✅ CSV export functionality
✅ Print-friendly reports
✅ Docker deployment
✅ Template parts list
✅ Real-time total calculation

## 💡 Tips

1. **Save reports**: Click "Save Report" button in dashboard
2. **Export**: Use "Export CSV" button for Excel/sheets
3. **Print**: Use "Print" button for PDF reports
4. **API**: Use `/api/reports` endpoint from n8n
5. **Database**: Located at `instance/crash_reports.db`

---

**Dashboard**: http://localhost:8080
**Status**: ✅ Running on port 8080
**n8n**: ✅ Safe on port 5678
