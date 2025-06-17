from app import db
from datetime import datetime

class MonitorLog(db.Model):
    """Model to store monitoring logs"""
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'success', 'error', 'available', 'unavailable'
    message = db.Column(db.Text, nullable=False)
    is_available = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<MonitorLog {self.timestamp}: {self.status}>'
