"""
GI4C API Routes
"""

from flask import request, jsonify
from app import app, db
from models import *
from ai_service import AIAssistant
from payment_service import PaymentProcessor
from data_processor import DataProcessor
from gis_service import GISProcessor
from datetime import datetime
import uuid

# Initialize services
ai_assistant = AIAssistant()
payment_processor = PaymentProcessor()
data_processor = DataProcessor()
gis_processor = GISProcessor()

# ==================== AI Assistant Routes ====================

@app.route('/api/ai-assistant', methods=['POST'])
def ai_chat():
    """AI Assistant chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Get AI response
        response = ai_assistant.generate_response(user_message, session_id)
        
        # Save conversation to database
        conversation = AIConversation(
            session_id=session_id,
            user_message=user_message,
            bot_response=response['message'],
            metadata=response.get('metadata', {})
        )
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify({
            'response': response['message'],
            'session_id': session_id,
            'sources': response.get('sources', [])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-assistant/history/<session_id>', methods=['GET'])
def ai_history(session_id):
    """Get conversation history for a session"""
    try:
        conversations = AIConversation.query.filter_by(
            session_id=session_id
        ).order_by(AIConversation.timestamp.asc()).all()
        
        history = [{
            'user': conv.user_message,
            'bot': conv.bot_response,
            'timestamp': conv.timestamp.isoformat()
        } for conv in conversations]
        
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Payment Routes ====================

@app.route('/api/payment/create', methods=['POST'])
def create_payment():
    """Create a payment intent"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        donor_name = data.get('donor_name', '')
        donor_email = data.get('donor_email', '')
        
        # Create payment with Monetbil/Orange Money
        payment = payment_processor.create_payment(
            amount=amount,
            donor_name=donor_name,
            donor_email=donor_email
        )
        
        # Save to database
        donation = Donation(
            donor_name=donor_name,
            donor_email=donor_email,
            amount=amount,
            currency='XAF',
            payment_method='monetbil',
            transaction_id=payment['transaction_id'],
            status='pending',
            metadata={'payment_url': payment.get('payment_url')}
        )
        db.session.add(donation)
        db.session.commit()
        
        return jsonify(payment)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/payment/notify', methods=['POST'])
def payment_notify():
    """Payment notification webhook"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        
        # Update donation status
        donation = Donation.query.filter_by(
            transaction_id=transaction_id
        ).first()
        
        if donation:
            donation.status = status
            if status == 'completed':
                donation.metadata = {**donation.metadata, **data}
            db.session.commit()
        
        return jsonify({'status': 'received'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/payment/status/<transaction_id>', methods=['GET'])
def payment_status(transaction_id):
    """Check payment status"""
    try:
        donation = Donation.query.filter_by(
            transaction_id=transaction_id
        ).first()
        
        if donation:
            return jsonify({
                'status': donation.status,
                'amount': donation.amount,
                'created_at': donation.created_at.isoformat()
            })
        else:
            return jsonify({'error': 'Payment not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Dashboard Data Routes ====================

@app.route('/api/dashboard/kpi', methods=['GET'])
def dashboard_kpi():
    """Get dashboard KPI data"""
    try:
        kpi_data = data_processor.get_kpi_data()
        return jsonify(kpi_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/programs', methods=['GET'])
def dashboard_programs():
    """Get programs data for dashboard"""
    try:
        programs = Program.query.filter_by(status='active').all()
        program_data = [{
            'id': p.id,
            'name': p.name,
            'category': p.category,
            'beneficiaries': p.beneficiaries,
            'region': p.region,
            'short_solution': p.short_solution or p.map_summary or p.description,
            'start_date': p.start_date.isoformat() if p.start_date else None
        } for p in programs]
        
        return jsonify({'programs': program_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/impact', methods=['GET'])
def dashboard_impact():
    """Get impact data for dashboard"""
    try:
        impact_data = data_processor.get_impact_data()
        return jsonify(impact_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/reports', methods=['GET'])
def dashboard_reports():
    """Get published reports"""
    try:
        reports = Report.query.filter_by(status='published').order_by(
            Report.published_at.desc()
        ).limit(10).all()
        
        report_data = [{
            'id': r.id,
            'title': r.title,
            'report_type': r.report_type,
            'published_at': r.published_at.isoformat() if r.published_at else None
        } for r in reports]
        
        return jsonify({'reports': report_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== GIS Routes ====================

@app.route('/api/gis/locations', methods=['GET'])
def gis_locations():
    """Get all GIS locations"""
    try:
        locations = GISLocation.query.all()
        geojson = gis_processor.locations_to_geojson(locations)
        return jsonify(geojson)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gis/locations', methods=['POST'])
def add_gis_location():
    """Add a new GIS location"""
    try:
        data = request.get_json()
        location = GISLocation(
            program_id=data.get('program_id'),
            name=data.get('name'),
            latitude=data['latitude'],
            longitude=data['longitude'],
            location_type=data.get('location_type', 'project'),
            properties=data.get('properties', {})
        )
        db.session.add(location)
        db.session.commit()
        
        return jsonify({'id': location.id, 'status': 'created'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gis/map', methods=['GET'])
def gis_map():
    """Generate interactive map HTML"""
    try:
        locations = GISLocation.query.all()
        map_html = gis_processor.generate_map(locations)
        return jsonify({'map_html': map_html})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Data Management Routes ====================

@app.route('/api/data/programs', methods=['GET'])
def get_programs():
    """Get all programs"""
    try:
        programs = Program.query.all()
        return jsonify({
            'programs': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'short_solution': p.short_solution or p.map_summary,
                'category': p.category,
                'status': p.status,
                'beneficiaries': p.beneficiaries,
                'region': p.region
            } for p in programs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/programs', methods=['POST'])
def create_program():
    """Create a new program"""
    try:
        data = request.get_json()
        program = Program(
            name=data['name'],
            description=data.get('description'),
            short_solution=data.get('short_solution') or data.get('map_summary'),
            map_summary=data.get('map_summary') or data.get('short_solution'),
            category=data.get('category'),
            region=data.get('region'),
            beneficiaries=data.get('beneficiaries', 0),
            metadata=data.get('metadata', {})
        )
        db.session.add(program)
        db.session.commit()
        
        return jsonify({'id': program.id, 'status': 'created'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/team', methods=['GET'])
def get_team():
    """Get team members"""
    try:
        team = TeamMember.query.filter_by(is_active=True).all()
        return jsonify({
            'team': [{
                'id': t.id,
                'name': t.name,
                'role': t.role,
                'bio': t.bio,
                'expertise': t.expertise
            } for t in team]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Report Routes ====================

@app.route('/api/reports', methods=['POST'])
def create_report():
    """Create a new report"""
    try:
        data = request.get_json()
        report = Report(
            title=data['title'],
            report_type=data.get('report_type', 'situation'),
            content=data.get('content'),
            program_id=data.get('program_id'),
            status='draft'
        )
        db.session.add(report)
        db.session.commit()
        
        return jsonify({'id': report.id, 'status': 'created'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/<int:report_id>/publish', methods=['POST'])
def publish_report(report_id):
    """Publish a report"""
    try:
        report = Report.query.get_or_404(report_id)
        report.status = 'published'
        report.published_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'status': 'published'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
