import sqlite3

def check_database():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Check users table
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    print("\nUsers in database:")
    if users:
        for user in users:
            print(f"UID: {user[0]}, Name: {user[1]}")
    else:
        print("No users found in database")
    
    # Check attendance table
    c.execute('SELECT * FROM attendance')
    attendance = c.fetchall()
    print("\nAttendance records:")
    if attendance:
        for record in attendance:
            print(f"ID: {record[0]}, UID: {record[1]}, Name: {record[2]}, Date: {record[3]}, Time: {record[4]}")
    else:
        print("No attendance records found")
    
    conn.close()

if __name__ == '__main__':
    check_database() 