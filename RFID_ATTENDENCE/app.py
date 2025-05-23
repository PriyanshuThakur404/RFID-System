from flask import Flask, render_template, jsonify, request, g
import serial
import serial.tools.list_ports
import threading
import time
import sqlite3
from datetime import datetime, date
import csv
import io
import os
import sys
import logging
from typing import Optional, Dict, List, Tuple
from functools import wraps
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
# from supabase import create_client, Client
# from dotenv import load_dotenv

# Load environment variables
# load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rfid_system.log')
    ]
)

# Initialize Supabase client
# SUPABASE_URL = os.getenv('SUPABASE_URL', 'your-project-url')
# SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your-api-key')
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # Preserve JSON order
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Disable pretty printing for smaller responses
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change in production

# Known users from Arduino
KNOWN_USERS: Dict[str, str] = {
    "5A 5E FA 03": "Naruto Uzumaki",
    "E9 7B A8 94": "Priyanshu Thakur",
    "89 6F 5E 93": "Milan",
    "79 AF A0 94": "Shivam Sharma",
    "F9 03 90 54": "Suparn",
    "69 70 88 54": "Ankush Chandel"
}

# Add JWT configuration
JWT_SECRET = 'your-jwt-secret'
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVhdmZkcnRvcW9ub3dnZHJwbnN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUxNTMxMzcsImV4cCI6MjA2MDcyOTEzN30.z0V2NVjijcRULMVLXOCloaCD11QRXl2WvX_GuNfb3M0"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('attendance.db')
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization token provided'}), 401
            
        try:
            # Verify the token
            token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else auth_header
            jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        except ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated

def init_database():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT NOT NULL,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uid) REFERENCES users(uid)
            )
        ''')
        
        # Add sample students if the table is empty
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            sample_students = [
                ('5A 5E FA 03', 'Naruto Uzumaki'),
                ('E9 7B A8 94', 'Priyanshu Thakur'),
                ('89 6F 5E 93', 'Milan'),
                ('79 AF A0 94', 'Shivam Sharma'),
                ('F9 03 90 54', 'Suparn'),
                ('69 70 88 54', 'Ankush Chandel')
            ]
            
            for uid, name in sample_students:
                try:
                    cursor.execute(
                        'INSERT INTO users (uid, name) VALUES (?, ?)',
                        (uid, name)
                    )
                    logging.info(f"Added student: {name} with UID: {uid}")
                except sqlite3.IntegrityError:
                    logging.warning(f"Student {name} with UID {uid} already exists")
        
        db.commit()
        logging.info("Database initialized successfully")
        return True
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live')
def live():
    return render_template('live.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/students', methods=['GET'])
@require_auth
def get_students():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get all users with their attendance stats
        cursor.execute("""
            SELECT 
                u.uid,
                u.name,
                u.created_at,
                COUNT(a.id) as total_attendance,
                MAX(a.created_at) as last_attendance
            FROM users u
            LEFT JOIN attendance a ON u.uid = a.uid
            GROUP BY u.uid, u.name, u.created_at
            ORDER BY u.name
        """)
        
        students = []
        for row in cursor.fetchall():
            students.append({
                'uid': row[0],
                'name': row[1],
                'created_at': row[2],
                'total_attendance': row[3],
                'last_attendance': row[4]
            })
        
        logging.info(f"Retrieved {len(students)} students from database")
        return jsonify(students)
    except Exception as e:
        logging.error(f"Error getting students: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_stats', methods=['GET'])
@require_auth
def get_stats():
    try:
        # Fetch total registered users
        total_registered = get_db().cursor().execute('SELECT COUNT(*) FROM users').fetchone()[0]

        # Fetch total attendance records
        total_attended = get_db().cursor().execute('SELECT COUNT(DISTINCT uid) FROM attendance').fetchone()[0]

        # Calculate today's attendance
        today_date = datetime.now().strftime('%Y-%m-%d')
        today_attendance = get_db().cursor().execute('SELECT COUNT(DISTINCT uid) FROM attendance WHERE date = ?', (today_date,)).fetchone()[0]

        # Calculate attendance rate
        attendance_rate = (total_attended / total_registered * 100) if total_registered > 0 else 0

        # Fetch the most recent attendance record
        most_recent_attendance = get_db().cursor().execute('SELECT name, date, time FROM attendance ORDER BY created_at DESC LIMIT 1').fetchone()

        # Prepare the most recent attendance data
        most_recent_attendance_data = {
            'name': most_recent_attendance['name'] if most_recent_attendance else 'N/A',
            'date': most_recent_attendance['date'] if most_recent_attendance else 'N/A',
            'time': most_recent_attendance['time'] if most_recent_attendance else 'N/A'
        }

        return jsonify({
            'totalRegistered': total_registered,
            'totalAttended': total_attended,
            'todayAttendance': today_attendance,
            'attendanceRate': attendance_rate,
            'mostRecentAttendance': most_recent_attendance_data
        }), 200
    except Exception as e:
        logging.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@app.route('/api/status', methods=['GET'])
@require_auth
def get_status():
    try:
        # Simulate checking system status
        connected = True  # This should be replaced with actual status check logic
        return jsonify({'connected': connected}), 200
    except Exception as e:
        logging.error(f"Error fetching status: {str(e)}")
        return jsonify({'error': 'Failed to fetch status'}), 500

@app.route('/api/get_recent_scans', methods=['GET'])
@require_auth
def get_recent_scans():
    try:
        db = get_db()
        cursor = db.cursor()

        # Fetch recent scans
        cursor.execute('''
            SELECT name, time, type FROM attendance
            ORDER BY created_at DESC LIMIT 10
        ''')

        scans = []
        for row in cursor.fetchall():
            scans.append({
                'name': row['name'],
                'time': row['time'],
                'access': row['type'] == 'entry'  # Assuming 'entry' means access granted
            })

        return jsonify(scans), 200
    except Exception as e:
        logging.error(f"Error fetching recent scans: {str(e)}")
        return jsonify({'error': 'Failed to fetch recent scans'}), 500

# Initialize database at startup
with app.app_context():
    init_database()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 