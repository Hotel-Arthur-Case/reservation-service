from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/reservations', methods=['GET'])
def get_reservations():
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()
    return jsonify([dict(reservation) for reservation in reservations])

@app.route('/reservations', methods=['POST'])
def add_reservation():
    data = request.get_json()
    
    # Tjek om data er en liste (flere reservationer) eller en enkelt dict (én reservation)
    if isinstance(data, list):
        reservations = data
    else:
        reservations = [data]  # Pak enkelt objekt i en liste for konsistens

    conn = get_db_connection()
    try:
        for reservation in reservations:
            conn.execute(
                '''
                INSERT INTO reservations (first_name, last_name, booking_number, price, room_type, country, days_rented, phone_number, email)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    reservation['first_name'],
                    reservation['last_name'],
                    reservation['booking_number'],
                    reservation['price'],
                    reservation['room_type'],
                    reservation['country'],
                    reservation['days_rented'],
                    reservation['phone_number'],
                    reservation['email']
                )
            )
        conn.commit()
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

    return jsonify({"message": "Reservationer tilføjet succesfuldt"}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)