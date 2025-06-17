import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from monitor import AmulMonitor
from datetime import datetime

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ.setdefault(key, value)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///monitor.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# initialize the app with the extension
db.init_app(app)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# Global monitor instance
monitor = AmulMonitor()

with app.app_context():
    # Import models
    from models import MonitorLog
    db.create_all()

@app.route('/')
def index():
    """Main dashboard page"""
    # Get recent logs
    recent_logs = MonitorLog.query.order_by(MonitorLog.timestamp.desc()).limit(10).all()
    
    # Check if monitoring is active
    is_monitoring = len(scheduler.get_jobs()) > 0
    
    # Get monitor configuration
    config = {
        'telegram_enabled': bool(os.environ.get('TELEGRAM_BOT_TOKEN') and os.environ.get('TELEGRAM_CHAT_ID')),
        'product_url': monitor.product_url,
        'check_interval': '1 hour'
    }
    
    return render_template('index.html', 
                         recent_logs=recent_logs, 
                         is_monitoring=is_monitoring,
                         config=config)

@app.route('/start_monitoring', methods=['POST'])
def start_monitoring():
    """Start the monitoring job"""
    try:
        # Remove existing jobs
        scheduler.remove_all_jobs()
        
        # Add new job to run every hour
        scheduler.add_job(
            func=monitor.check_availability,
            trigger=IntervalTrigger(hours=1),
            id='amul_monitor',
            name='Amul Product Monitor',
            replace_existing=True
        )
        
        # Run an immediate check
        monitor.check_availability()
        
        flash('Monitoring started successfully!', 'success')
        logger.info("Monitoring started - checking every hour")
        
    except Exception as e:
        flash(f'Error starting monitoring: {str(e)}', 'error')
        logger.error(f"Error starting monitoring: {e}")
    
    return redirect(url_for('index'))

@app.route('/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """Stop the monitoring job"""
    try:
        scheduler.remove_all_jobs()
        flash('Monitoring stopped successfully!', 'info')
        logger.info("Monitoring stopped")
        
    except Exception as e:
        flash(f'Error stopping monitoring: {str(e)}', 'error')
        logger.error(f"Error stopping monitoring: {e}")
    
    return redirect(url_for('index'))

@app.route('/check_now', methods=['POST'])
def check_now():
    """Run an immediate check"""
    try:
        result = monitor.check_availability()
        if result:
            flash('Check completed successfully!', 'success')
        else:
            flash('Check completed - product still unavailable', 'info')
            
    except Exception as e:
        flash(f'Error during check: {str(e)}', 'error')
        logger.error(f"Error during manual check: {e}")
    
    return redirect(url_for('index'))

@app.route('/api/logs')
def api_logs():
    """API endpoint to get recent logs"""
    logs = MonitorLog.query.order_by(MonitorLog.timestamp.desc()).limit(20).all()
    
    return jsonify([{
        'id': log.id,
        'timestamp': log.timestamp.isoformat(),
        'status': log.status,
        'message': log.message,
        'is_available': log.is_available
    } for log in logs])

@app.route('/api/status')
def api_status():
    """API endpoint to get monitoring status"""
    return jsonify({
        'is_monitoring': len(scheduler.get_jobs()) > 0,
        'telegram_configured': bool(os.environ.get('TELEGRAM_BOT_TOKEN') and os.environ.get('TELEGRAM_CHAT_ID')),
        'last_check': monitor.last_check_time.isoformat() if monitor.last_check_time else None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
