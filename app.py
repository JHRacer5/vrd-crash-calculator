from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime
import os
import json
import uuid
import requests
import threading

app = Flask(__name__)

# Enable CORS for n8n cloud and other external services
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://zbywxysilprzbqnctpkz.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpieXd4eXNpbHByemJxbmN0cGt6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ2OTI1NTEsImV4cCI6MjA4MDI2ODU1MX0.yhAQ-afJc_oXeT13jI5HrKOPrqSP0rxKh2aRv4g2oZY')

# n8n webhook URL for AI processing (production webhook)
N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL', 'https://slipstreamaiconsulting.app.n8n.cloud/webhook/vrdcrashworkflow')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def trigger_n8n_workflow(report_data):
    """Trigger n8n webhook to process crash report with AI (runs in background)"""
    def send_webhook():
        try:
            print(f"[WEBHOOK] Triggering n8n webhook at: {N8N_WEBHOOK_URL}")
            print(f"[WEBHOOK] Sending data for incident: {report_data.get('incident_id')}")
            response = requests.post(
                N8N_WEBHOOK_URL,
                json=report_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            print(f"[WEBHOOK] Response status: {response.status_code}")
            if response.status_code == 200:
                print(f"[WEBHOOK] SUCCESS - n8n webhook triggered for incident {report_data.get('incident_id')}")
            else:
                print(f"[WEBHOOK] WARNING - n8n returned status {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[WEBHOOK] ERROR - Failed to trigger n8n webhook: {str(e)}")

    # Run in background thread so we don't block the response
    thread = threading.Thread(target=send_webhook)
    thread.daemon = True
    thread.start()


def report_to_dict(report, parts=None):
    """Convert a report record to dictionary format"""
    return {
        'id': report['id'],
        'incident_id': report.get('incident_id'),
        'driver': report.get('driver', ''),
        'date': report.get('date', ''),
        'chassis': report.get('chassis', ''),
        'event': report.get('event', ''),
        'accident_damage': report.get('accident_damage', ''),
        'total': float(report.get('total', 0) or 0),
        'status': report.get('status', 'pending'),
        'created_at': report.get('created_at'),
        'updated_at': report.get('updated_at'),
        'parts': parts if parts is not None else []
    }


def part_to_dict(part):
    """Convert a part record to dictionary format"""
    return {
        'id': part['id'],
        'report_id': part['report_id'],
        'part_number': part.get('part_number', ''),
        'part': part.get('part', ''),
        'likelihood': part.get('likelihood', 'Possible'),
        'price': float(part.get('price', 0) or 0),
        'qty': int(part.get('qty', 1) or 1),
        'total': float(part.get('total', 0) or 0)
    }


def get_report_with_parts(report_id):
    """Get a report with its parts"""
    report_response = supabase.table('reports').select('*').eq('id', report_id).single().execute()
    if not report_response.data:
        return None

    parts_response = supabase.table('parts').select('*').eq('report_id', report_id).execute()
    parts = [part_to_dict(p) for p in (parts_response.data or [])]

    return report_to_dict(report_response.data, parts)


# Web Routes
@app.route('/')
def index():
    """Dashboard home page"""
    return render_template('dashboard.html')


@app.route('/reports')
def reports_list():
    """All reports list page"""
    return render_template('reports_list.html')


@app.route('/reports/new')
def create_report_page():
    """Create new report page"""
    return render_template('create_report.html')


@app.route('/reports/<int:report_id>')
def view_report_page(report_id):
    """View/edit specific report page"""
    return render_template('view_report.html', report_id=report_id)


@app.route('/pending')
def pending_reports():
    """Pending reports that need review"""
    return render_template('pending_reports.html')


@app.route('/n8n-integration')
def n8n_integration_page():
    """n8n integration information and endpoint"""
    return render_template('n8n_integration.html')


# API Routes for n8n Integration

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'VRD Crash Calculator API is running'}), 200


@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get all reports"""
    response = supabase.table('reports').select('*').order('created_at', desc=True).execute()
    reports = []
    for report in (response.data or []):
        parts_response = supabase.table('parts').select('*').eq('report_id', report['id']).execute()
        parts = [part_to_dict(p) for p in (parts_response.data or [])]
        reports.append(report_to_dict(report, parts))
    return jsonify(reports), 200


@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """Get a specific report by ID"""
    report = get_report_with_parts(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    return jsonify(report), 200


@app.route('/api/reports', methods=['POST'])
def create_report():
    """Create a new crash report - Creates with PENDING status, generates incident_id for n8n linking"""
    try:
        data = request.json

        # Generate unique incident_id for n8n workflow linking
        now = datetime.utcnow()
        incident_id = f"VRD-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # Create new report with PENDING status (awaiting n8n enrichment)
        report_data = {
            'incident_id': incident_id,
            'driver': data.get('driver', ''),
            'date': data.get('date', ''),
            'chassis': data.get('chassis', ''),
            'event': data.get('event', ''),
            'accident_damage': data.get('accident_damage', ''),
            'status': 'pending',
            'total': 0.0
        }

        report_response = supabase.table('reports').insert(report_data).execute()
        report = report_response.data[0]
        report_id = report['id']

        # Add parts if provided
        total_amount = 0.0
        parts_data = data.get('parts', [])
        created_parts = []

        for part_data in parts_data:
            price = float(part_data.get('price', 0) or 0)
            qty = int(part_data.get('qty', 1) or 1)
            part_total = price * qty
            total_amount += part_total

            part_insert = {
                'report_id': report_id,
                'part_number': part_data.get('part_number', ''),
                'part': part_data.get('part', ''),
                'likelihood': part_data.get('likelihood', 'Possible'),
                'price': price,
                'qty': qty,
                'total': part_total
            }
            part_response = supabase.table('parts').insert(part_insert).execute()
            created_parts.append(part_to_dict(part_response.data[0]))

        # Update report total
        supabase.table('reports').update({'total': total_amount}).eq('id', report_id).execute()
        report['total'] = total_amount

        # Trigger n8n webhook for AI processing (runs in background)
        webhook_data = {
            'incident_id': incident_id,
            'driver': data.get('driver', ''),
            'date': data.get('date', ''),
            'chassis': data.get('chassis', ''),
            'event': data.get('event', ''),
            'accident_damage': data.get('accident_damage', '')
        }
        trigger_n8n_workflow(webhook_data)

        return jsonify({
            'success': True,
            'message': 'Report created successfully. AI processing started.',
            'report': report_to_dict(report, created_parts)
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/from-n8n', methods=['POST'])
def create_report_from_n8n():
    """Create a new crash report from n8n workflow - Sets status as PENDING for review"""
    try:
        data = request.json
        # Handle case where n8n sends double-encoded JSON string
        if isinstance(data, str):
            data = json.loads(data)

        # Create new report with PENDING status (from n8n)
        report_data = {
            'driver': data.get('driver', ''),
            'date': data.get('date', ''),
            'chassis': data.get('chassis', ''),
            'event': data.get('event', ''),
            'accident_damage': data.get('accident_damage', ''),
            'status': 'pending',
            'total': 0.0
        }

        report_response = supabase.table('reports').insert(report_data).execute()
        report = report_response.data[0]
        report_id = report['id']

        # Add parts if provided
        total_amount = 0.0
        parts_data = data.get('parts', [])
        created_parts = []

        for part_data in parts_data:
            price = float(part_data.get('price', 0) or 0)
            qty = int(part_data.get('qty', 1) or 1)
            part_total = price * qty
            total_amount += part_total

            part_insert = {
                'report_id': report_id,
                'part_number': part_data.get('part_number', ''),
                'part': part_data.get('part', ''),
                'likelihood': part_data.get('likelihood', 'Possible'),
                'price': price,
                'qty': qty,
                'total': part_total
            }
            part_response = supabase.table('parts').insert(part_insert).execute()
            created_parts.append(part_to_dict(part_response.data[0]))

        # Update report total
        supabase.table('reports').update({'total': total_amount}).eq('id', report_id).execute()
        report['total'] = total_amount

        return jsonify({
            'success': True,
            'message': 'Report created successfully and marked as PENDING for review',
            'report': report_to_dict(report, created_parts),
            'status': 'pending'
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/pending', methods=['GET'])
def get_pending_reports():
    """Get all pending reports that need review"""
    response = supabase.table('reports').select('*').eq('status', 'pending').order('created_at', desc=True).execute()
    reports = []
    for report in (response.data or []):
        parts_response = supabase.table('parts').select('*').eq('report_id', report['id']).execute()
        parts = [part_to_dict(p) for p in (parts_response.data or [])]
        reports.append(report_to_dict(report, parts))
    return jsonify(reports), 200


@app.route('/api/reports/<int:report_id>/status', methods=['PUT'])
def update_report_status(report_id):
    """Update report status (pending, active, reviewed)"""
    try:
        data = request.json

        new_status = data.get('status', '')
        if new_status not in ['pending', 'active', 'reviewed']:
            return jsonify({
                'success': False,
                'error': 'Invalid status. Must be: pending, active, or reviewed'
            }), 400

        response = supabase.table('reports').update({
            'status': new_status,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', report_id).execute()

        if not response.data:
            return jsonify({'success': False, 'error': 'Report not found'}), 404

        report = get_report_with_parts(report_id)

        return jsonify({
            'success': True,
            'message': f'Report status updated to {new_status}',
            'report': report
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """Update an existing report"""
    try:
        data = request.json

        # Build update data
        update_data = {'updated_at': datetime.utcnow().isoformat()}
        if 'driver' in data:
            update_data['driver'] = data['driver']
        if 'date' in data:
            update_data['date'] = data['date']
        if 'chassis' in data:
            update_data['chassis'] = data['chassis']
        if 'event' in data:
            update_data['event'] = data['event']
        if 'accident_damage' in data:
            update_data['accident_damage'] = data['accident_damage']

        # Update parts if provided
        if 'parts' in data:
            # Delete existing parts
            supabase.table('parts').delete().eq('report_id', report_id).execute()

            # Add new parts
            total_amount = 0.0
            for part_data in data['parts']:
                price = float(part_data.get('price', 0) or 0)
                qty = int(part_data.get('qty', 1) or 1)
                part_total = price * qty
                total_amount += part_total

                part_insert = {
                    'report_id': report_id,
                    'part_number': part_data.get('part_number', ''),
                    'part': part_data.get('part', ''),
                    'likelihood': part_data.get('likelihood', 'Possible'),
                    'price': price,
                    'qty': qty,
                    'total': part_total
                }
                supabase.table('parts').insert(part_insert).execute()

            update_data['total'] = total_amount

        response = supabase.table('reports').update(update_data).eq('id', report_id).execute()

        if not response.data:
            return jsonify({'success': False, 'error': 'Report not found'}), 404

        report = get_report_with_parts(report_id)

        return jsonify({
            'success': True,
            'message': 'Report updated successfully',
            'report': report
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/by-incident/<incident_id>', methods=['PUT'])
def update_report_by_incident_id(incident_id):
    """Update an existing report by incident_id - Used by n8n workflow to add parts"""
    try:
        data = request.json
        # Handle case where n8n sends double-encoded JSON string
        if isinstance(data, str):
            data = json.loads(data)

        # Find report by incident_id
        response = supabase.table('reports').select('*').eq('incident_id', incident_id).execute()
        if not response.data:
            return jsonify({
                'success': False,
                'error': f'Report with incident_id {incident_id} not found'
            }), 404

        report = response.data[0]
        report_id = report['id']

        # Build update data
        update_data = {'updated_at': datetime.utcnow().isoformat()}
        if 'driver' in data:
            update_data['driver'] = data['driver']
        if 'date' in data:
            update_data['date'] = data['date']
        if 'chassis' in data:
            update_data['chassis'] = data['chassis']
        if 'event' in data:
            update_data['event'] = data['event']
        if 'accident_damage' in data:
            update_data['accident_damage'] = data['accident_damage']

        # Update parts if provided
        if 'parts' in data and data['parts']:
            # Delete existing parts
            supabase.table('parts').delete().eq('report_id', report_id).execute()

            # Add new parts
            total_amount = 0.0
            parts_list = data['parts']

            # Handle case where parts might be a string (JSON)
            if isinstance(parts_list, str):
                parts_list = json.loads(parts_list)

            for part_data in parts_list:
                price = float(part_data.get('price', 0) or 0)
                qty = int(part_data.get('qty', 1) or 1)
                part_total = price * qty
                total_amount += part_total

                part_insert = {
                    'report_id': report_id,
                    'part_number': part_data.get('part_number', ''),
                    'part': part_data.get('part', ''),
                    'likelihood': part_data.get('likelihood', 'Possible'),
                    'price': price,
                    'qty': qty,
                    'total': part_total
                }
                supabase.table('parts').insert(part_insert).execute()

            update_data['total'] = total_amount

        # Update status to active (n8n has enriched it)
        update_data['status'] = 'active'

        supabase.table('reports').update(update_data).eq('id', report_id).execute()

        report = get_report_with_parts(report_id)

        return jsonify({
            'success': True,
            'message': 'Report updated successfully by incident_id',
            'report': report
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Delete a report"""
    try:
        # Parts will be deleted automatically due to ON DELETE CASCADE
        response = supabase.table('reports').delete().eq('id', report_id).execute()

        if not response.data:
            return jsonify({'success': False, 'error': 'Report not found'}), 404

        return jsonify({
            'success': True,
            'message': 'Report deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/<int:report_id>/parts', methods=['POST'])
def add_part(report_id):
    """Add a part to a report"""
    try:
        # Verify report exists
        report_response = supabase.table('reports').select('*').eq('id', report_id).single().execute()
        if not report_response.data:
            return jsonify({'success': False, 'error': 'Report not found'}), 404

        report = report_response.data
        data = request.json

        price = float(data.get('price', 0) or 0)
        qty = int(data.get('qty', 1) or 1)
        part_total = price * qty

        part_insert = {
            'report_id': report_id,
            'part_number': data.get('part_number', ''),
            'part': data.get('part', ''),
            'likelihood': data.get('likelihood', 'Possible'),
            'price': price,
            'qty': qty,
            'total': part_total
        }

        part_response = supabase.table('parts').insert(part_insert).execute()
        part = part_response.data[0]

        # Update report total
        new_total = float(report.get('total', 0) or 0) + part_total
        supabase.table('reports').update({
            'total': new_total,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', report_id).execute()

        return jsonify({
            'success': True,
            'message': 'Part added successfully',
            'part': part_to_dict(part)
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/parts/<int:part_id>', methods=['PUT'])
def update_part(part_id):
    """Update a specific part"""
    try:
        # Get existing part
        part_response = supabase.table('parts').select('*').eq('id', part_id).single().execute()
        if not part_response.data:
            return jsonify({'success': False, 'error': 'Part not found'}), 404

        part = part_response.data
        old_total = float(part.get('total', 0) or 0)
        report_id = part['report_id']

        data = request.json

        # Build update data
        update_data = {}
        if 'part_number' in data:
            update_data['part_number'] = data['part_number']
        if 'part' in data:
            update_data['part'] = data['part']
        if 'likelihood' in data:
            update_data['likelihood'] = data['likelihood']

        # Get current values for calculation
        price = float(data.get('price', part.get('price', 0)) or 0)
        qty = int(data.get('qty', part.get('qty', 1)) or 1)

        if 'price' in data:
            update_data['price'] = price
        if 'qty' in data:
            update_data['qty'] = qty

        # Recalculate part total
        new_part_total = price * qty
        update_data['total'] = new_part_total

        supabase.table('parts').update(update_data).eq('id', part_id).execute()

        # Update report total
        report_response = supabase.table('reports').select('total').eq('id', report_id).single().execute()
        report_total = float(report_response.data.get('total', 0) or 0)
        new_report_total = report_total - old_total + new_part_total

        supabase.table('reports').update({
            'total': new_report_total,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', report_id).execute()

        # Get updated part
        updated_part = supabase.table('parts').select('*').eq('id', part_id).single().execute()

        return jsonify({
            'success': True,
            'message': 'Part updated successfully',
            'part': part_to_dict(updated_part.data)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/parts/<int:part_id>', methods=['DELETE'])
def delete_part(part_id):
    """Delete a part"""
    try:
        # Get existing part
        part_response = supabase.table('parts').select('*').eq('id', part_id).single().execute()
        if not part_response.data:
            return jsonify({'success': False, 'error': 'Part not found'}), 404

        part = part_response.data
        part_total = float(part.get('total', 0) or 0)
        report_id = part['report_id']

        # Update report total
        report_response = supabase.table('reports').select('total').eq('id', report_id).single().execute()
        report_total = float(report_response.data.get('total', 0) or 0)
        new_report_total = report_total - part_total

        supabase.table('reports').update({
            'total': new_report_total,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', report_id).execute()

        # Delete part
        supabase.table('parts').delete().eq('id', part_id).execute()

        return jsonify({
            'success': True,
            'message': 'Part deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    # Use debug=False in production, controlled by environment variable
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
