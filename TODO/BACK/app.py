import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = 'tasks.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Create Users Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Create Tasks Table with a user_id link
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

# --- AUTHENTICATION ROUTES ---

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        conn = get_db_connection()
        cursor = conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', 
                             (email, password))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return jsonify({"message": "User Created", "user_id": user_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                        (email, password)).fetchone()
    conn.close()
    
    if user:
        return jsonify({"message": "Success", "user_id": user['id']})
    else:
        return jsonify({"error": "Invalid email or password"}), 401

# --- TASK ROUTES ---

# GET tasks for a specific user
@app.route('/tasks/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    conn = get_db_connection()
    tasks_db = conn.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in tasks_db])

# CREATE a new task linked to a user
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    user_id = data.get('user_id')
    text = data.get('text')
    
    conn = get_db_connection()
    cursor = conn.execute('INSERT INTO tasks (user_id, text, status) VALUES (?, ?, ?)', 
                         (user_id, text, 'todo'))
    conn.commit()
    new_task_id = cursor.lastrowid
    conn.close()
    
    return jsonify({"id": new_task_id, "text": text, "status": "todo"})

# UPDATE task status (Moves between columns)
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    new_status = data.get('status')
    
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    
    if task:
        current_text = task['text']
        # Backend handles the (W) win logic for persistence
        if new_status == 'done' and "(W)" not in current_text:
            current_text += " (W)"
            
        conn.execute('UPDATE tasks SET status = ?, text = ? WHERE id = ?', 
                     (new_status, current_text, task_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Task updated"})
    
    conn.close()
    return jsonify({"error": "Task not found"}), 404

# DELETE task (Shadow Realm)
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Banishment complete"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)