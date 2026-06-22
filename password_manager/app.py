from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import secrets
import string
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

DATABASE = 'passwords.db'

def get_db():
    """Получение подключения к базе данных"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализация базы данных"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            login TEXT NOT NULL,
            password TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def generate_password(length=12, use_digits=True, use_special=True):
    """Генерация пароля"""
    characters = string.ascii_letters
    if use_digits:
        characters += string.digits
    if use_special:
        characters += string.punctuation
    
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Генерация пароля"""
    length = int(request.form.get('length', 12))
    use_digits = 'use_digits' in request.form
    use_special = 'use_special' in request.form
    
    password = generate_password(length, use_digits, use_special)
    return render_template('index.html', generated_password=password)

@app.route('/passwords')
def list_passwords():
    """Список сохранённых паролей"""
    conn = get_db()
    passwords = conn.execute('SELECT * FROM passwords ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('passwords_list.html', passwords=passwords)

@app.route('/add', methods=['GET', 'POST'])
def add_password():
    """Добавление нового пароля"""
    if request.method == 'POST':
        site = request.form.get('site')
        login = request.form.get('login')
        password = request.form.get('password')
        notes = request.form.get('notes', '')
        
        # Валидация
        if not site or not login or not password:
            flash('Все поля (кроме заметок) обязательны для заполнения', 'error')
            return render_template('add_password.html')
        
        conn = get_db()
        conn.execute(
            'INSERT INTO passwords (site, login, password, notes) VALUES (?, ?, ?, ?)',
            (site, login, password, notes)
        )
        conn.commit()
        conn.close()
        
        flash('Пароль успешно сохранён!', 'success')
        return redirect(url_for('list_passwords'))
    
    return render_template('add_password.html')

@app.route('/password/<int:password_id>')
def view_password(password_id):
    """Просмотр пароля"""
    conn = get_db()
    password = conn.execute('SELECT * FROM passwords WHERE id = ?', (password_id,)).fetchone()
    conn.close()
    
    if not password:
        flash('Пароль не найден', 'error')
        return redirect(url_for('list_passwords'))
    
    return render_template('password_detail.html', password=password)

@app.route('/delete/<int:password_id>', methods=['POST'])
def delete_password(password_id):
    """Удаление пароля"""
    conn = get_db()
    conn.execute('DELETE FROM passwords WHERE id = ?', (password_id,))
    conn.commit()
    conn.close()
    
    flash('Пароль удалён', 'success')
    return redirect(url_for('list_passwords'))

@app.route('/search')
def search():
    """Поиск паролей"""
    query = request.args.get('q', '')
    conn = get_db()
    passwords = conn.execute(
        'SELECT * FROM passwords WHERE site LIKE ? OR login LIKE ? ORDER BY created_at DESC',
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return render_template('passwords_list.html', passwords=passwords, search_query=query)

@app.route('/toggle_show/<int:password_id>', methods=['POST'])
def toggle_show(password_id):
    """Показать/скрыть пароль"""
    # Просто переадресация на страницу просмотра
    return redirect(url_for('view_password', password_id=password_id))

# Инициализация базы данных
init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)