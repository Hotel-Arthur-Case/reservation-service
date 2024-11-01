from flask import Flask, jsonify, request, make_response
import sqlite3
from io import StringIO
import csv

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
    
    # Check if data is a list (multiple reservations) or a single dict (one reservation)
    if isinstance(data, list):
        reservations = data
    else:
        reservations = [data]  # Wrap single object in a list for consistency

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

    return jsonify({"message": "Reservations added successfully"}), 201

# Export reservations to CSV
@app.route('/reservations/csv', methods=['GET'])
def export_reservations_csv():
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()
    conn.close()
    
    si = StringIO()
    writer = csv.writer(si)
    
    # Write CSV header
    writer.writerow([
        'Reservation ID',
        'First Name',
        'Last Name',
        'Booking Number',
        'Price',
        'Room Type',
        'Country',
        'Days Rented',
        'Phone Number',
        'Email'
    ])
    
    # Write reservation data
    for reservation in reservations:
        writer.writerow([
            reservation['id'],  # Assuming there's an 'id' column in your table
            reservation['first_name'],
            reservation['last_name'],
            reservation['booking_number'],
            reservation['price'],
            reservation['room_type'],
            reservation['country'],
            reservation['days_rented'],
            reservation['phone_number'],
            reservation['email']
        ])
    
    # Create a response with the CSV data
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=reservations.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)