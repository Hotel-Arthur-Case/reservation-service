from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        booking_number TEXT UNIQUE NOT NULL,
        price REAL NOT NULL,
        room_type TEXT NOT NULL,
        country TEXT NOT NULL,
        days_rented INTEGER NOT NULL,
        phone_number TEXT NOT NULL,
        email TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

@app.route('/reservations', methods=['GET'])
def get_reservations():
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in reservations])

@app.route('/reservations', methods=['POST'])
def add_reservation():
    data = request.get_json()
    
    # Check if data is a list (multiple reservations) or a single dict (one reservation)
    if isinstance(data, list):
        reservations = data
    else:
        reservations = [data]  # Wrap single object in a list for consistency
    
    conn = get_db_connection()
    try:
        for reservation in reservations:
            conn.execute(
                '''INSERT INTO reservations (first_name, last_name, booking_number, price, room_type, country, days_rented, phone_number, email)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (reservation['first_name'], reservation['last_name'], reservation['booking_number'], reservation['price'], 
                 reservation['room_type'], reservation['country'], reservation['days_rented'], 
                 reservation['phone_number'], reservation['email'])
            )
        conn.commit()
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

    return jsonify({"message": "Reservations added successfully"}), 201

if __name__ == '__main__':
    initialize_database()  # Ensure the table exists on startup
    app.run(debug=True, host='0.0.0.0', port=5000)