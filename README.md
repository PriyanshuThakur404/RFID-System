# Smart RFID Attendance System

A web-based attendance tracking system that uses RFID technology for automated attendance recording.

## Features

- Real-time RFID card scanning
- User registration and management
- Attendance tracking with timestamps
- Admin dashboard for monitoring
- Data export to CSV
- Live feed of recent scans

## Hardware Requirements

- Arduino Uno
- RC522 RFID Module
- Buzzer
- LEDs (Red and Green)
- I2C LCD Display
- DFPlayer Mini (optional)

## Software Requirements

- Python 3.8 or higher
- Flask web framework
- SQLite database
- Modern web browser

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rfid-attendance-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Register Users**:
   - Go to the Register page
   - Enter the RFID card UID and user's name
   - Click "Register User"

2. **Track Attendance**:
   - Present the RFID card to the scanner
   - The system will automatically log the attendance
   - View attendance records in the Admin dashboard

3. **Admin Dashboard**:
   - View all registered users
   - Monitor attendance records
   - Filter attendance by date
   - Export data to CSV

## Project Structure

```
rfid-attendance-system/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── static/            # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── admin.js
│       ├── register.js
│       └── live.js
├── templates/         # HTML templates
│   ├── index.html
│   ├── about.html
│   ├── admin.html
│   ├── register.html
│   └── live.html
└── attendance.db      # SQLite database
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 