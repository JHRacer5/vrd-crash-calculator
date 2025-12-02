# VRD Racing - Crash Report Calculator Dashboard

A Flask-based crash report calculator dashboard with Supabase cloud database and REST API for n8n AI workflow integration.

## Features

- Interactive web dashboard for crash report management
- Supabase cloud database for persistent storage
- REST API endpoints for n8n workflow integration
- Automatic AI-powered parts estimation via n8n
- Docker support with production-ready gunicorn server
- CORS enabled for cross-origin API access
- Cloudflare container deployment ready

## Architecture

```
User submits crash report → Dashboard saves to Supabase
                                    ↓
                         Triggers n8n webhook
                                    ↓
                    n8n AI analyzes & generates parts list
                                    ↓
                    n8n calls back to update report
                                    ↓
                      Report updated with parts (status: active)
```

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/JHRacer5/vrd-crash-calculator.git
cd vrd-crash-calculator
```

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

3. Access the dashboard at: http://localhost:8080

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the dashboard at: http://localhost:8080

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | (built-in) |
| `SUPABASE_KEY` | Supabase anon key | (built-in) |
| `N8N_WEBHOOK_URL` | n8n webhook for AI processing | (built-in) |
| `PORT` | Server port | `8080` |
| `FLASK_DEBUG` | Enable debug mode | `False` |

## Cloudflare Deployment

This app is production-ready for Cloudflare container deployment.

### Required Environment Variables

Set these in your Cloudflare container settings:

```
SUPABASE_URL=https://zbywxysilprzbqnctpkz.supabase.co
SUPABASE_KEY=your-supabase-anon-key
N8N_WEBHOOK_URL=https://slipstreamaiconsulting.app.n8n.cloud/webhook/vrdcrashworkflow
PORT=8080
```

### After Deployment

Update your n8n workflow's callback HTTP node to:
```
PUT https://YOUR-CLOUDFLARE-DOMAIN/api/reports/by-incident/{{ $json.body.incident_id }}
```

## API Documentation

### Base URL
```
https://your-domain.com/api
```

### Endpoints

#### Health Check
```http
GET /api/health
```
Returns the API health status.

#### Get All Reports
```http
GET /api/reports
```
Retrieves all crash reports with parts.

#### Get Single Report
```http
GET /api/reports/{report_id}
```
Retrieves a specific crash report.

#### Get Pending Reports
```http
GET /api/reports/pending
```
Retrieves reports awaiting AI processing.

#### Create Report
```http
POST /api/reports
Content-Type: application/json
```
Creates a new report and triggers n8n AI workflow.

**Request Body:**
```json
{
  "driver": "John Doe",
  "date": "2025-11-03",
  "chassis": "IP22",
  "event": "Round 5 - Qualifying",
  "accident_damage": "Speed: 80mph, Impact: Front-Left, Barrier: SAFER"
}
```

#### Update Report by Incident ID (n8n callback)
```http
PUT /api/reports/by-incident/{incident_id}
Content-Type: application/json
```
Used by n8n to add AI-generated parts to a report.

**Request Body:**
```json
{
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

#### Update Report Status
```http
PUT /api/reports/{report_id}/status
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "reviewed"
}
```
Valid statuses: `pending`, `active`, `reviewed`

#### Delete Report
```http
DELETE /api/reports/{report_id}
```

#### Add Part to Report
```http
POST /api/reports/{report_id}/parts
Content-Type: application/json
```

#### Update Part
```http
PUT /api/parts/{part_id}
Content-Type: application/json
```

#### Delete Part
```http
DELETE /api/parts/{part_id}
```

## n8n Integration

### Workflow Overview

1. **Dashboard triggers n8n** when a report is created
2. **n8n AI** analyzes crash data and generates parts list
3. **n8n calls back** to update the report with parts

### n8n Webhook Receives

```json
{
  "incident_id": "VRD-20251202-ABC123",
  "driver": "John Doe",
  "date": "2025-12-02",
  "chassis": "IP22",
  "event": "Round 5 - Qualifying",
  "accident_damage": "Speed: 80mph, Impact: Front-Left..."
}
```

### n8n Callback Format

```http
PUT /api/reports/by-incident/{incident_id}
```

```json
{
  "parts": [
    {
      "part_number": "122-18-04-036",
      "part": "Front impact structure",
      "likelihood": "Highly Likely",
      "price": 5000.00,
      "qty": 1
    }
  ]
}
```

See `n8n-integration/` folder for detailed setup guides.

## Database

The application uses **Supabase** (PostgreSQL) for cloud data storage.

### Tables

- `reports` - Crash report metadata
- `parts` - Parts associated with reports (cascade delete)

## Development

To run in development mode with auto-reload:

```bash
FLASK_DEBUG=True python app.py
```

Or with Docker:
```bash
docker-compose up -d
docker logs -f vrd-crash-calculator
```

## Troubleshooting

### API Health Check
```bash
curl http://localhost:8080/api/health
```

### View Logs
```bash
docker logs vrd-crash-calculator
```

### n8n Can't Reach Dashboard
- Ensure dashboard is publicly accessible (Cloudflare deployed)
- Check CORS is enabled (it is by default)
- Verify the callback URL in n8n matches your domain

### Report Stuck in Pending
- Check n8n workflow is active
- Verify webhook URL is correct
- Check n8n execution logs for errors

## Tech Stack

- **Backend:** Flask + Gunicorn
- **Database:** Supabase (PostgreSQL)
- **AI Processing:** n8n Cloud
- **Deployment:** Docker / Cloudflare Containers

## License

© 2025 VRD Racing. All rights reserved.
