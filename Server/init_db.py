import sqlite3
import hashlib

connection = sqlite3.connect('User.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Enkripsi password dengan SHA-256
password = 'ilham'  # Ganti dengan password yang ingin Anda gunakan
hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

cur.execute("INSERT INTO User (username, password, role) VALUES (?, ?, ?)",
            ('ilham', hashed_password, 'user')
            )

connection.commit()
connection.close()
