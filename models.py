"""
GI4C Database Models
"""

from datetime import datetime
from app import db
from sqlalchemy import JSON

class User(db.Model):
    """User model for authentication and access control"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='viewer')  # admin, editor, viewer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Program(db.Model):
    """Program model for GI4C programs"""
    __tablename__ = 'programs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    short_solution = db.Column(db.Text)
    map_summary = db.Column(db.Text)
    category = db.Column(db.String(50))  # emergency, data, capacity, resilience
    status = db.Column(db.String(50), default='active')
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    region = db.Column(db.String(100))
    beneficiaries = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = db.Column(JSON)  # Flexible JSON for additional data

class ImpactData(db.Model):
    """Impact and KPI data model"""
    __tablename__ = 'impact_data'
    
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float)
    metric_unit = db.Column(db.String(50))
    date_recorded = db.Column(db.Date, default=datetime.utcnow)
    region = db.Column(db.String(100))
    metadata = db.Column(JSON)

class TeamMember(db.Model):
    """Team member model"""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    expertise = db.Column(JSON)  # List of expertise areas
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Donation(db.Model):
    """Donation/payment model"""
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_name = db.Column(db.String(200))
    donor_email = db.Column(db.String(120))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='XAF')
    payment_method = db.Column(db.String(50))  # monetbil, orange_money, etc.
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    metadata = db.Column(JSON)

class GISLocation(db.Model):
    """GIS/Geospatial data model"""
    __tablename__ = 'gis_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))
    name = db.Column(db.String(200))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_type = db.Column(db.String(50))  # project, beneficiary, resource
    properties = db.Column(JSON)  # GeoJSON properties
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIConversation(db.Model):
    """AI Assistant conversation history"""
    __tablename__ = 'ai_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    metadata = db.Column(JSON)

class Report(db.Model):
    """Reports and intelligence products"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50))  # situation, policy, warning
    content = db.Column(db.Text)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(50), default='draft')
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScheduledTask(db.Model):
    """Scheduled tasks for automation"""
    __tablename__ = 'scheduled_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(50))  # data_sync, report_gen, alert
    schedule = db.Column(db.String(100))  # cron expression
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
