import sqlite3

def add_users():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # List of users with their UIDs and names
    users = [
        ("5A5EFA03", "Naruto Uzumaki"),
        ("E97BA894", "Priyanshu Thakur"),
        ("896F5E93", "Sasuke Uchiha"),
        ("79AFA094", "Shivam Sharma"),
        ("F9039054", "Kakashi Hatake"),
        ("69708854", "Itachi Uchiha")
    ]
    
    added_count = 0
    for uid, name in users:
        try:
            c.execute('INSERT INTO users (uid, name) VALUES (?, ?)', (uid, name))
            print(f"Successfully added user: {name} with UID: {uid}")
            added_count += 1
        except sqlite3.IntegrityError:
            print(f"User {name} already exists in database")
    
    conn.commit()
    print(f"\nTotal users added: {added_count}")
    conn.close()

if __name__ == '__main__':
    add_users() 