from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crash_reports.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.String(50), unique=True, nullable=True)  # Unique ID for n8n linking
    driver = db.Column(db.String(200))
    date = db.Column(db.String(50))
    chassis = db.Column(db.String(200))
    event = db.Column(db.String(200))
    accident_damage = db.Column(db.Text)
    total = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, active, reviewed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parts = db.relationship('Part', backref='report', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'driver': self.driver,
            'date': self.date,
            'chassis': self.chassis,
            'event': self.event,
            'accident_damage': self.accident_damage,
            'total': self.total,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'parts': [part.to_dict() for part in self.parts]
        }


class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    part_number = db.Column(db.String(100))
    part = db.Column(db.String(500))
    likelihood = db.Column(db.String(50))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer, default=1)
    total = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'part_number': self.part_number,
            'part': self.part,
            'likelihood': self.likelihood,
            'price': self.price,
            'qty': self.qty,
            'total': self.total
        }


# Initialize database
with app.app_context():
    db.create_all()


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
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return jsonify([report.to_dict() for report in reports]), 200


@app.route('/api/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    """Get a specific report by ID"""
    report = Report.query.get_or_404(report_id)
    return jsonify(report.to_dict()), 200


@app.route('/api/reports', methods=['POST'])
def create_report():
    """Create a new crash report - Creates with PENDING status, generates incident_id for n8n linking"""
    try:
        data = request.json

        # Generate unique incident_id for n8n workflow linking
        now = datetime.utcnow()
        incident_id = f"VRD-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # Create new report with PENDING status (awaiting n8n enrichment)
        report = Report(
            incident_id=incident_id,
            driver=data.get('driver', ''),
            date=data.get('date', ''),
            chassis=data.get('chassis', ''),
            event=data.get('event', ''),
            accident_damage=data.get('accident_damage', ''),
            status='pending',
            total=0.0
        )
        db.session.add(report)
        db.session.flush()  # Get the report ID

        # Add parts if provided
        total_amount = 0.0
        parts_data = data.get('parts', [])

        for part_data in parts_data:
            price = float(part_data.get('price', 0) or 0)
            qty = int(part_data.get('qty', 1) or 1)
            part_total = price * qty
            total_amount += part_total

            part = Part(
                report_id=report.id,
                part_number=part_data.get('part_number', ''),
                part=part_data.get('part', ''),
                likelihood=part_data.get('likelihood', 'Possible'),
                price=price,
                qty=qty,
                total=part_total
            )
            db.session.add(part)

        # Update report total
        report.total = total_amount
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Report created successfully',
            'report': report.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
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
        report = Report(
            driver=data.get('driver', ''),
            date=data.get('date', ''),
            chassis=data.get('chassis', ''),
            event=data.get('event', ''),
            accident_damage=data.get('accident_damage', ''),
            status='pending',  # Mark as pending for review
            total=0.0
        )
        db.session.add(report)
        db.session.flush()  # Get the report ID

        # Add parts if provided
        total_amount = 0.0
        parts_data = data.get('parts', [])

        for part_data in parts_data:
            price = float(part_data.get('price', 0) or 0)
            qty = int(part_data.get('qty', 1) or 1)
            part_total = price * qty
            total_amount += part_total

            part = Part(
                report_id=report.id,
                part_number=part_data.get('part_number', ''),
                part=part_data.get('part', ''),
                likelihood=part_data.get('likelihood', 'Possible'),
                price=price,
                qty=qty,
                total=part_total
            )
            db.session.add(part)

        # Update report total
        report.total = total_amount
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Report created successfully and marked as PENDING for review',
            'report': report.to_dict(),
            'status': 'pending'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/pending', methods=['GET'])
def get_pending_reports():
    """Get all pending reports that need review"""
    reports = Report.query.filter_by(status='pending').order_by(Report.created_at.desc()).all()
    return jsonify([report.to_dict() for report in reports]), 200


@app.route('/api/reports/<int:report_id>/status', methods=['PUT'])
def update_report_status(report_id):
    """Update report status (pending, active, reviewed)"""
    try:
        report = Report.query.get_or_404(report_id)
        data = request.json

        new_status = data.get('status', '')
        if new_status not in ['pending', 'active', 'reviewed']:
            return jsonify({
                'success': False,
                'error': 'Invalid status. Must be: pending, active, or reviewed'
            }), 400

        report.status = new_status
        report.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Report status updated to {new_status}',
            'report': report.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    """Update an existing report"""
    try:
        report = Report.query.get_or_404(report_id)
        data = request.json

        # Update report fields
        if 'driver' in data:
            report.driver = data['driver']
        if 'date' in data:
            report.date = data['date']
        if 'chassis' in data:
            report.chassis = data['chassis']
        if 'event' in data:
            report.event = data['event']
        if 'accident_damage' in data:
            report.accident_damage = data['accident_damage']

        # Update parts if provided
        if 'parts' in data:
            # Delete existing parts
            Part.query.filter_by(report_id=report_id).delete()

            # Add new parts
            total_amount = 0.0
            for part_data in data['parts']:
                price = float(part_data.get('price', 0) or 0)
                qty = int(part_data.get('qty', 1) or 1)
                part_total = price * qty
                total_amount += part_total

                part = Part(
                    report_id=report.id,
                    part_number=part_data.get('part_number', ''),
                    part=part_data.get('part', ''),
                    likelihood=part_data.get('likelihood', 'Possible'),
                    price=price,
                    qty=qty,
                    total=part_total
                )
                db.session.add(part)

            report.total = total_amount

        report.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Report updated successfully',
            'report': report.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
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
        report = Report.query.filter_by(incident_id=incident_id).first()
        if not report:
            return jsonify({
                'success': False,
                'error': f'Report with incident_id {incident_id} not found'
            }), 404

        # Update report fields if provided
        if 'driver' in data:
            report.driver = data['driver']
        if 'date' in data:
            report.date = data['date']
        if 'chassis' in data:
            report.chassis = data['chassis']
        if 'event' in data:
            report.event = data['event']
        if 'accident_damage' in data:
            report.accident_damage = data['accident_damage']

        # Update parts if provided
        if 'parts' in data and data['parts']:
            # Delete existing parts
            Part.query.filter_by(report_id=report.id).delete()

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

                part = Part(
                    report_id=report.id,
                    part_number=part_data.get('part_number', ''),
                    part=part_data.get('part', ''),
                    likelihood=part_data.get('likelihood', 'Possible'),
                    price=price,
                    qty=qty,
                    total=part_total
                )
                db.session.add(part)

            report.total = total_amount

        # Update status to active (n8n has enriched it)
        report.status = 'active'
        report.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Report updated successfully by incident_id',
            'report': report.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Delete a report"""
    try:
        report = Report.query.get_or_404(report_id)
        db.session.delete(report)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Report deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/<int:report_id>/parts', methods=['POST'])
def add_part(report_id):
    """Add a part to a report"""
    try:
        report = Report.query.get_or_404(report_id)
        data = request.json

        price = float(data.get('price', 0) or 0)
        qty = int(data.get('qty', 1) or 1)
        part_total = price * qty

        part = Part(
            report_id=report_id,
            part_number=data.get('part_number', ''),
            part=data.get('part', ''),
            likelihood=data.get('likelihood', 'Possible'),
            price=price,
            qty=qty,
            total=part_total
        )
        db.session.add(part)

        # Update report total
        report.total = (report.total or 0) + part_total
        report.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Part added successfully',
            'part': part.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/parts/<int:part_id>', methods=['PUT'])
def update_part(part_id):
    """Update a specific part"""
    try:
        part = Part.query.get_or_404(part_id)
        data = request.json

        old_total = part.total or 0

        if 'part_number' in data:
            part.part_number = data['part_number']
        if 'part' in data:
            part.part = data['part']
        if 'likelihood' in data:
            part.likelihood = data['likelihood']
        if 'price' in data:
            part.price = float(data['price'] or 0)
        if 'qty' in data:
            part.qty = int(data['qty'] or 1)

        # Recalculate part total
        part.total = (part.price or 0) * (part.qty or 1)

        # Update report total
        report = Report.query.get(part.report_id)
        report.total = (report.total or 0) - old_total + part.total
        report.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Part updated successfully',
            'part': part.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/parts/<int:part_id>', methods=['DELETE'])
def delete_part(part_id):
    """Delete a part"""
    try:
        part = Part.query.get_or_404(part_id)
        report = Report.query.get(part.report_id)

        # Update report total
        report.total = (report.total or 0) - (part.total or 0)
        report.updated_at = datetime.utcnow()

        db.session.delete(part)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Part deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
