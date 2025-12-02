# VRD Racing - Crash Report Calculator Dashboard

A Flask-based crash report calculator dashboard with SQLite database and REST API for n8n integration.

## Features

- Interactive web dashboard for crash report management
- SQLite database for persistent storage
- REST API endpoints for n8n workflow integration
- Docker support for easy deployment
- CSV export functionality
- Print-friendly report format

## Quick Start

### Using Docker (Recommended)

1. Navigate to the project directory:
```bash
cd ~/crash-calculator-dashboard
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

## API Documentation

### Base URL
```
http://localhost:8080/api
```

### Endpoints

#### Health Check
```http
GET /api/health
```
Returns the API health status.

**Response:**
```json
{
  "status": "healthy",
  "message": "VRD Crash Calculator API is running"
}
```

---

#### Get All Reports
```http
GET /api/reports
```
Retrieves all crash reports.

**Response:**
```json
[
  {
    "id": 1,
    "driver": "John Doe",
    "date": "2025-11-03",
    "venue": "Laguna Seca",
    "event": "Round 5",
    "accident_damage": "Rear impact damage",
    "total": 15250.00,
    "created_at": "2025-11-03T10:30:00",
    "updated_at": "2025-11-03T10:30:00",
    "parts": [...]
  }
]
```

---

#### Get Single Report
```http
GET /api/reports/{report_id}
```
Retrieves a specific crash report.

**Response:**
```json
{
  "id": 1,
  "driver": "John Doe",
  "date": "2025-11-03",
  "venue": "Laguna Seca",
  "event": "Round 5",
  "accident_damage": "Rear impact damage",
  "total": 15250.00,
  "parts": [
    {
      "id": 1,
      "part_number": "122-18-04-036",
      "part": "Crashbox posteriore (Rear impact structure)",
      "likelihood": "Highly Likely",
      "price": 5000.00,
      "qty": 1,
      "total": 5000.00
    }
  ]
}
```

---

#### Create Report (Main n8n Endpoint)
```http
POST /api/reports
Content-Type: application/json
```

**Request Body:**
```json
{
  "driver": "John Doe",
  "date": "2025-11-03",
  "venue": "Laguna Seca",
  "event": "Round 5",
  "accident_damage": "Rear impact damage during qualifying",
  "parts": [
    {
      "part_number": "122-18-04-036",
      "part": "Crashbox posteriore (Rear impact structure)",
      "likelihood": "Highly Likely",
      "price": 5000.00,
      "qty": 1
    },
    {
      "part_number": "121-16-10-002",
      "part": "Rh rear lower wishbone assy",
      "likelihood": "Highly Likely",
      "price": 2500.00,
      "qty": 1
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Report created successfully",
  "report": {
    "id": 1,
    "driver": "John Doe",
    "total": 7500.00,
    ...
  }
}
```

---

#### Update Report
```http
PUT /api/reports/{report_id}
Content-Type: application/json
```

**Request Body:** Same as Create Report

---

#### Delete Report
```http
DELETE /api/reports/{report_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Report deleted successfully"
}
```

---

#### Add Part to Report
```http
POST /api/reports/{report_id}/parts
Content-Type: application/json
```

**Request Body:**
```json
{
  "part_number": "316-14-10-006",
  "part": "Rear upper wishbone",
  "likelihood": "Likely",
  "price": 1200.00,
  "qty": 2
}
```

---

#### Update Part
```http
PUT /api/parts/{part_id}
Content-Type: application/json
```

**Request Body:**
```json
{
  "part_number": "316-14-10-006",
  "part": "Rear upper wishbone",
  "likelihood": "Highly Likely",
  "price": 1300.00,
  "qty": 2
}
```

---

#### Delete Part
```http
DELETE /api/parts/{part_id}
```

## n8n Integration Guide

### Step 1: Replace Google Sheets Node

In your n8n workflow, you'll replace the Google Sheets node with an HTTP Request node.

### Step 2: Add HTTP Request Node

1. Add a new "HTTP Request" node after your AI Agent
2. Configure it as follows:

**Method:** POST
**URL:** `http://host.docker.internal:8080/api/reports`
**Authentication:** None
**Body Content Type:** JSON

**Request Body:**
```json
{
  "driver": "{{ $json.driver }}",
  "date": "{{ $json.date }}",
  "venue": "{{ $json.venue }}",
  "event": "{{ $json.event }}",
  "accident_damage": "{{ $json.accident_damage }}",
  "parts": "{{ $json.parts }}"
}
```

### Step 3: Format AI Agent Output

Your AI Agent should output data in this format:

```json
{
  "driver": "John Doe",
  "date": "2025-11-03",
  "venue": "Laguna Seca",
  "event": "Round 5",
  "accident_damage": "Rear impact during qualifying session",
  "parts": [
    {
      "part_number": "122-18-04-036",
      "part": "Crashbox posteriore (Rear impact structure)",
      "likelihood": "Highly Likely",
      "price": 5000,
      "qty": 1
    }
  ]
}
```

### Step 4: Update AI Agent System Prompt

Add this to your AI Agent's system message:

```
When you've gathered all the necessary information and created the crash report,
output the data in the following JSON format:

{
  "driver": "Driver Name",
  "date": "YYYY-MM-DD",
  "venue": "Venue Name",
  "event": "Event Name",
  "accident_damage": "Description of the accident and damage",
  "parts": [
    {
      "part_number": "Part Number",
      "part": "Part Description",
      "likelihood": "Highly Likely|Likely|Possible|Unlikely",
      "price": 0.00,
      "qty": 1
    }
  ]
}

This data will be automatically saved to our crash report system.
```

### Accessing from n8n Docker Container

If n8n is running in Docker, use one of these URLs:

- **If on same Docker network:** `http://vrd-crash-calculator:8080`
- **If on host network:** `http://host.docker.internal:8080`
- **From outside:** `http://localhost:8080`

## Database

The application uses SQLite for data storage. The database file is located at:
```
instance/crash_reports.db
```

When running in Docker, this is persisted in a volume.

## Stopping the Application

### Docker
```bash
docker-compose down
```

### Manual
Press `Ctrl+C` in the terminal where the app is running.

## Troubleshooting

### Port Already in Use
If port 8080 is already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # Change 8081 to any available port
```

### n8n Can't Connect
1. Ensure both containers are running: `docker ps`
2. Check if they're on the same network
3. Use `http://host.docker.internal:8080` if n8n is in Docker
4. Check firewall settings

### Database Not Persisting
Ensure the `instance` directory exists and has write permissions:
```bash
mkdir -p instance
chmod 755 instance
```

## Development

To run in development mode with auto-reload:

```python
# In app.py, change the last line to:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

## Support

For issues or questions, please check:
- Application logs: `docker-compose logs -f`
- API health: http://localhost:8080/api/health
- Database contents: Use any SQLite browser

## License

© 2025 VRD Racing. All rights reserved.
