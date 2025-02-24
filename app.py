from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            is_admin INTEGER DEFAULT 0,
                            is_active INTEGER DEFAULT 1)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT,
                            message TEXT)''')
        conn.commit()

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=? AND is_active=1", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            session['is_admin'] = user[3]
            return redirect(url_for('chat'))
    return "Login failed!"

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('chat.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file uploaded!'
    file = request.files['file']
    if file.filename == '':
        return 'No file selected!'
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return 'File uploaded successfully!'

@app.route('/admin')
def admin():
    if 'username' not in session or not session.get('is_admin'):
        return "Access Denied!"
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, is_active FROM users")
        users = cursor.fetchall()
    return render_template('admin.html', users=users)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
