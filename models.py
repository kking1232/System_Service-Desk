from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """Reprezentacja użytkownika z określoną rolą np. IT/Consultant"""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    
    # Relacje ułatwiające dostęp do powiązanych danych
    tickets = db.relationship('Ticket', backref='author', lazy=True)
    notifications = db.relationship('Notification', backref='recipient', lazy=True)

class Ticket(db.Model):
    """Reprezentacja całościowa formularza zgłoszonego błędu"""
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    service = db.Column(db.String(100))
    account_status = db.Column(db.String(50))
    cache_status = db.Column(db.String(50))
    email = db.Column(db.String(100))
    client_number = db.Column(db.String(100))
    client_name = db.Column(db.String(100))
    pesel_nip = db.Column(db.String(20))
    invoice_number = db.Column(db.String(50))
    version = db.Column(db.String(50))
    model = db.Column(db.String(100))
    os_info = db.Column(db.String(200))
    status = db.Column(db.String(50), default="Nowe")
    solution = db.Column(db.Text)
    
    # Relacja: wiele zgłoszeń może być przypisanych do jednego twórcy
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    created_at = db.Column(db.String(20)) 
    created_at_dt = db.Column(db.DateTime, default=datetime.now)
    closed_at_dt = db.Column(db.DateTime)
    attachments = db.Column(db.Text, default='[]')
    notes = db.Column(db.Text, default='[]')
    logs = db.Column(db.Text, default='[]')

class Notification(db.Model):
    """Powiadomienia systemowe"""
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    message = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)