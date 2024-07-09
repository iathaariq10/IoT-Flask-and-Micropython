from io import StringIO
from flask import Flask, request, render_template, redirect, session, flash, url_for,jsonify,g, Response
import sqlite3
import csv
from datetime import datetime, timedelta
import socket
import json
import threading
import time
import hashlib

app = Flask(__name__)
app.secret_key = 'delibre'

def get_db_connection():
    conn = sqlite3.connect('User.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table(client_id):
    conn = sqlite3.connect(f'client_{client_id}_data.db')
    c = conn.cursor()

    if client_id == 1:
        c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                     (timestamp DATETIME, S1_A REAL, S1_B REAL, status_1 TEXT, status_2 TEXT)''')
    elif client_id == 2:
        c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                     (timestamp DATETIME, S2_A REAL, S2_B REAL, status_1 TEXT, status_2 TEXT)''')
    elif client_id == 3:
        c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                     (timestamp DATETIME, S3_A REAL, S3_B REAL, S3_C REAL, S3_D REAL, status_1 TEXT, status_2 TEXT)''')

    conn.commit()
    conn.close()

def save_sensor_data(client_id, data):
    conn = sqlite3.connect(f'client_{client_id}_data.db')
    c = conn.cursor()
    timestamp = datetime.now()

    last_data_time = get_last_data_time(client_id)
    if last_data_time is None or timestamp - last_data_time >= timedelta(minutes=1):
        formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M')
        if client_id == 1:
            c.execute('''INSERT INTO sensor_data (timestamp, S1_A, S1_B, status_1, status_2) 
                         VALUES (?, ?, ?, ?, ?)''', (formatted_timestamp, float(data['S1_A']), float(data['S1_B']), data['status_1'], data['status_2']))
        elif client_id == 2:
            c.execute('''INSERT INTO sensor_data (timestamp, S2_A, S2_B, status_1, status_2) 
                         VALUES (?, ?, ?, ?, ?)''', (formatted_timestamp, float(data['S2_A']), float(data['S2_B']), data['status_1'], data['status_2']))
        elif client_id == 3:
            c.execute('''INSERT INTO sensor_data (timestamp, S3_A, S3_B, S3_C, S3_D, status_1, status_2) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', (formatted_timestamp, float(data['S3_A']), float(data['S3_B']), float(data['S3_C']), float(data['S3_D']), data['status_1'], data['status_2']))
        conn.commit()
        conn.close()

def get_last_data_time(client_id):
    conn = sqlite3.connect(f'client_{client_id}_data.db')
    c = conn.cursor()
    c.execute('''SELECT timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 1''')
    row = c.fetchone()
    conn.close()
    if row:
        return datetime.fromisoformat(row[0])
    return None

def get_last_5_data(client_id):
    conn = sqlite3.connect(f'client_{client_id}_data.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 5''')
    rows = c.fetchall()
    conn.close()
    return rows

for client_id in range(1, 4):
    create_table(client_id)

def generate_csv(client_id):
    conn = sqlite3.connect(f'client_{client_id}_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sensor_data')
    rows = cursor.fetchall()
    conn.close()

    si = StringIO()
    cw = csv.writer(si)
    if client_id == 1:
        cw.writerow(['timestamp', 'S1_A', 'S1_B', 'status_1', 'status_2'])
    elif client_id == 2:
        cw.writerow(['timestamp', 'S2_A', 'S2_B', 'status_1', 'status_2'])
    elif client_id == 3:
        cw.writerow(['timestamp', 'S3_A', 'S3_B', 'S3_C', 'S3_D', 'status_1', 'status_2'])
    cw.writerows(rows)
    return si.getvalue()


s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s1.bind(('0.0.0.0', 6001))
print('listening on 0.0.0.0:6001')

s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2.bind(('0.0.0.0', 6002))
print('listening on 0.0.0.0:6002')

s3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s3.bind(('0.0.0.0', 6003))
print('listening on 0.0.0.0:6003')


client1_status = "Offline"
last_received_time_1 = time.time()
data_count_1 = 0

client2_status = "Offline"
last_received_time_2 = time.time()
data_count_2 = 0

client3_status = "Offline"
last_received_time_3 = time.time()
data_count_3 = 0

def check_client_status():
    global client1_status, client2_status, client3_status
    while True:
        current_time = time.time()
        if current_time - last_received_time_1 > 2:
            client1_status = "Offline"
        if current_time - last_received_time_2 > 2:
            client2_status = "Offline"
        if current_time - last_received_time_3 > 2:
            client3_status = "Offline"
        time.sleep(2)

threading.Thread(target=check_client_status, daemon=True).start()

def is_user_logged_in():
    return 'username' in session

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/client')
def client():
    if is_user_logged_in():
        return render_template('client.html')
    else:
        flash("Anda harus login untuk mengakses halaman ini.", "error")
        return redirect(url_for('login'))

# History Data
@app.route('/history')
def history():
    if is_user_logged_in():
        data_client1 = get_last_5_data(1)
        data_client2 = get_last_5_data(2)
        data_client3 = get_last_5_data(3)
        return render_template('history.html', data_client1=data_client1, data_client2=data_client2, data_client3=data_client3)
    else:
        flash("Anda harus login untuk mengakses halaman ini.", "error")
        return redirect(url_for('login'))

@app.route('/get_sensor_data/<int:client_id>')
def get_sensor_data(client_id):
    conn = sqlite3.connect(f'client_{client_id}_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sensor_data')
    sensor_data = cursor.fetchall()
    conn.close()
    return json.dumps(sensor_data)

# Login / Sign Up / Logout Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM User WHERE username = ?"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        conn.close()

        if user:
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if hashed_password == user['password']:
                session['username'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('monitoring'))
            else:
                flash("Username atau password salah! Silakan ulangi atau daftar.", "error")
                return render_template('login.html')
        else:
            flash("Username atau password salah! Silakan ulangi atau daftar.", "error")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM User WHERE username = ?"
        cursor.execute(query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Username sudah ada, tampilkan popup untuk update password
            return render_template('update_password.html', username=username)

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        query = "INSERT INTO User (username, password, role) VALUES (?, ?, ?)"
        cursor.execute(query, (username, hashed_password, 'user'))
        conn.commit()
        conn.close()

        flash("Daftar berhasil! Silakan gunakan akun baru Anda.", "success")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/update_password', methods=['POST'])
def update_password():
    if request.method == 'POST':
        username = request.form.get('username')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM User WHERE username = ?"
        cursor.execute(query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Verifikasi password lama sebelum update
            hashed_old_password = hashlib.sha256(old_password.encode('utf-8')).hexdigest()
            if hashed_old_password == existing_user['password']:
                # Update password baru
                hashed_new_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
                query = "UPDATE User SET password = ? WHERE username = ?"
                cursor.execute(query, (hashed_new_password, username))
                conn.commit()
                conn.close()

                flash("Password berhasil diupdate.", "success")
            else:
                flash("Password lama salah. Silakan coba lagi.", "error")

    return redirect(url_for('login'))


# Monitoring Page
@app.route('/monitoring')
def monitoring():
    if is_user_logged_in():
        return render_template('monitoring.html')
    else:
        flash("Anda harus login untuk mengakses halaman ini.", "error")
        return redirect(url_for('login'))

# Logout Page
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


# CLIENT 1
@app.route('/updateClient1')
def get_sensor_data_1():
    global client1_status, last_received_time_1, data_count_1
    print("Menerima permintaan data dari Client 1!")

    data, addr1 = s1.recvfrom(2048)
    print('Server menerima data dari client 1', addr1)
    S1_A, S1_B, status_1, status_2 = map(str, data.decode().split(','))

    received_data_1 = {
        'ip_address_1': addr1[0],
        'S1_A': S1_A,
        'S1_B': S1_B,
        'status_1': status_1,
        'status_2': status_2,
    }

    save_sensor_data(1, received_data_1)

    response = {
        "reading_S1_A": float(S1_A),
        "reading_S1_B": float(S1_B),
        "ipAddress_1": received_data_1['ip_address_1'],
        "status_1": status_1,
        "status_2": status_2,
    }

    client1_status = "Online"
    last_received_time_1 = time.time()
    data_count_1 += 1

    return json.dumps(response)

@app.route('/statusClient1')
def status_client_1():
    global client1_status, data_count_1
    return jsonify({"status": client1_status, "data_count": data_count_1})

@app.route('/controlClient1', methods=['POST'])
def control_client_1():
    addr1 = s1.recvfrom(2048)
    ip_client_1 = addr1[1]
    command = request.form['command']
    s1.sendto(command.encode(), (ip_client_1))
    return jsonify({'status': 'success', 'command': command})

@app.route('/get_chart_data/1')
def get_chart_data_1():
    conn = sqlite3.connect('client_1_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, S1_A, S1_B, status_1, status_2 FROM sensor_data ORDER BY timestamp DESC LIMIT 30')
    rows = cursor.fetchall()
    conn.close()

    data = [
        {
            'timestamp': row[0],
            'S1_A': row[1],
            'S1_B': row[2],
            'Status_1': row[3],
            'Status_2': row[4],
        }
        for row in rows
    ]

    return jsonify(data)

# CLIENT 2
@app.route('/updateClient2')
def get_sensor_data_2():
    global client2_status, last_received_time_2, data_count_2
    print("Menerima permintaan data dari Client 2!")

    data, addr2 = s2.recvfrom(2048)
    print('Server menerima data dari client 2', addr2)
    S2_A, S2_B, status_1, status_2 = map(str, data.decode().split(','))

    received_data_2 = {
        'ip_address_2': addr2[0],
        'S2_A': S2_A,
        'S2_B': S2_B,
        'status_1': status_1,
        'status_2': status_2,
    }

    save_sensor_data(2, received_data_2)

    response = {
        "reading_S2_A": float(S2_A),
        "reading_S2_B": float(S2_B),
        "ipAddress_2": received_data_2['ip_address_2'],
        "status_1": status_1,
        "status_2": status_2,
    }

    client2_status = "Online"
    last_received_time_2 = time.time()
    data_count_2 += 1

    return json.dumps(response)

@app.route('/statusClient2')
def status_client_2():
    global client2_status, data_count_2
    return jsonify({"status": client2_status, "data_count": data_count_2})

@app.route('/controlClient2', methods=['POST'])
def control_client_2():
    addr2 = s2.recvfrom(2048)
    ip_client_2 = addr2[1]
    command = request.form['command']
    s1.sendto(command.encode(),(ip_client_2))
    return jsonify({'status': 'success', 'command': command})

@app.route('/get_chart_data/2')
def get_chart_data_2():
    conn = sqlite3.connect('client_2_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, S2_A, S2_B, status_1, status_2 FROM sensor_data ORDER BY timestamp DESC LIMIT 30')
    rows = cursor.fetchall()
    conn.close()

    data = [
        {
            'timestamp': row[0],
            'S2_A': row[1],
            'S2_B': row[2],
            'Status_1': row[3],
            'Status_2': row[4],
        }
        for row in rows
    ]

    return jsonify(data)

# CLIENT 3
@app.route('/updateClient3')
def get_sensor_data_3():
    global client3_status, last_received_time_3, data_count_3
    print("Menerima permintaan data dari Client 3!")

    data, addr3 = s3.recvfrom(2048)
    print('Server menerima data dari client 3', addr3)
    S3_A, S3_B, S3_C, S3_D, status_1, status_2 = map(str, data.decode().split(','))

    received_data_3 = {
        'ip_address_3': addr3[0],
        'S3_A': float(S3_A),
        'S3_B': float(S3_B),
        'S3_C': float(S3_C),
        'S3_D': float(S3_D),
        'status_1': status_1,
        'status_2': status_2,
    }

    save_sensor_data(3, received_data_3)

    response = {
        "reading_S3_A": received_data_3['S3_A'],
        "reading_S3_B": received_data_3['S3_B'],
        "reading_S3_C": received_data_3['S3_C'],
        "reading_S3_D": received_data_3['S3_D'],
        "ipAddress_3": received_data_3['ip_address_3'],
        "status_1": status_1,
        "status_2": status_2,
    }

    client3_status = "Online"
    last_received_time_3 = time.time()
    data_count_3 += 1

    return json.dumps(response)

@app.route('/statusClient3')
def status_client_3():
    global client3_status, data_count_3
    return jsonify({"status": client3_status, "data_count": data_count_3})

@app.route('/controlClient3', methods=['POST'])
def control_client_3():
    addr3 = s3.recvfrom(2048)
    ip_client_3 = addr3[1]
    command = request.form['command']
    s1.sendto(command.encode(),(ip_client_3))
    return jsonify({'status': 'success', 'command': command})

@app.route('/get_chart_data/3')
def get_chart_data_3():
    conn = sqlite3.connect('client_3_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, S3_A, S3_B, S3_C, S3_D, status_1, status_2 FROM sensor_data ORDER BY timestamp DESC LIMIT 30')
    rows = cursor.fetchall()
    conn.close()

    data = [
        {
            'timestamp': row[0],
            'S3_A': row[1],
            'S3_B': row[2],
            'S3_C': row[3],
            'S3_D': row[4],
            'Status_1': row[5],
            'Status_2': row[6],
        }
        for row in rows
    ]

    return jsonify(data)

# Ambil Data CSV
@app.route('/download_csv/<int:client_id>')
def download_csv(client_id):
    if is_user_logged_in():
        csv_data = generate_csv(client_id)
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=client_{client_id}_data.csv'}
        )
    else:
        flash("Anda harus login untuk mengakses halaman ini.", "error")
        return redirect(url_for('login'))





if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        s1.close()
        s2.close()
        s3.close()