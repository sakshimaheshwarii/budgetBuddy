# import sqlite3
# from parser import parse_transaction

# DB_NAME = 'budgetbuddy.db'

# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS transactions
#                  (id INTEGER PRIMARY KEY, amount REAL, category TEXT, type TEXT, date TEXT, note TEXT)''')
#     conn.commit()
#     conn.close()

# def add_transaction(parsed):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''INSERT INTO transactions (amount, category, type, date, note) VALUES (?, ?, ?, ?, ?)''',
#               (parsed['amount'], parsed['category'], parsed['type'], parsed['date'], parsed['note']))
#     conn.commit()
#     conn.close()

# def get_transactions(limit=100):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('SELECT amount, category, type, date, note FROM transactions ORDER BY date DESC LIMIT ?', (limit,))
#     rows = c.fetchall()
#     conn.close()
#     return [{'amount': r[0], 'category': r[1], 'type': r[2], 'date': r[3], 'note': r[4]} for r in rows]

# if __name__ == "__main__":
#     init_db()

# ------------------------------------------------------------------
# storage.py (enhanced)
# import sqlite3
# from datetime import datetime, timedelta

# DB_NAME = 'budgetbuddy.db'

# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS transactions
#                  (id INTEGER PRIMARY KEY, amount REAL, category TEXT, type TEXT, 
#                  date TEXT, note TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
#     c.execute('''CREATE TABLE IF NOT EXISTS budgets
#                  (id INTEGER PRIMARY KEY, amount REAL, category TEXT, 
#                  month TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
#     c.execute('''CREATE TABLE IF NOT EXISTS categories
#                  (id INTEGER PRIMARY KEY, name TEXT, type TEXT, 
#                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
#     c.execute('''CREATE TABLE IF NOT EXISTS user_settings
#                  (id INTEGER PRIMARY KEY, key TEXT, value TEXT, 
#                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
#     conn.commit()
#     conn.close()

# def get_monthly_summary():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''
#         SELECT 
#             strftime('%Y-%m', date) as month,
#             SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as income,
#             SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expenses,
#             SUM(CASE WHEN type='income' THEN amount ELSE -amount END) as net
#         FROM transactions
#         GROUP BY strftime('%Y-%m', date)
#         ORDER BY month
#     ''')
#     rows = c.fetchall()
#     conn.close()
    
#     return [{'month': r[0], 'income': r[1], 'expenses': r[2], 'net': r[3]} for r in rows]

# def set_budget(amount, category="general"):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     current_month = datetime.now().strftime('%Y-%m')
#     c.execute('''
#         INSERT OR REPLACE INTO budgets (amount, category, month)
#         VALUES (?, ?, ?)
#     ''', (amount, category, current_month))
#     conn.commit()
#     conn.close()

# def get_budget(category="general"):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     current_month = datetime.now().strftime('%Y-%m')
#     c.execute('''
#         SELECT amount FROM budgets 
#         WHERE category=? AND month=?
#     ''', (category, current_month))
#     result = c.fetchone()
#     conn.close()
#     return result[0] if result else None

# def add_transaction(parsed):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''
#         INSERT INTO transactions (amount, category, type, date, note)
#         VALUES (?, ?, ?, ?, ?)
#     ''', (parsed['amount'], parsed['category'], parsed['type'], parsed['date'], parsed['note']))
#     conn.commit()
#     conn.close()

# def get_transactions(limit=100):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('SELECT amount, category, type, date, note FROM transactions ORDER BY date DESC LIMIT ?', (limit,))
#     rows = c.fetchall()
#     conn.close()
#     return [{'amount': r[0], 'category': r[1], 'type': r[2], 'date': r[3], 'note': r[4]} for r in rows]
# ----------------------------------------------------------------------------------












# storage.py
# import sqlite3
# from datetime import datetime, timedelta

# DB_NAME = 'budgetbuddy.db'

# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS transactions
#                  (id INTEGER PRIMARY KEY, amount REAL, category TEXT, type TEXT, 
#                  date TEXT, note TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
#     c.execute('''CREATE TABLE IF NOT EXISTS budgets
#                  (id INTEGER PRIMARY KEY, amount REAL, month TEXT, 
#                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
#     c.execute('''CREATE TABLE IF NOT EXISTS savings_goals
#                  (id INTEGER PRIMARY KEY, name TEXT, target_amount REAL, 
#                  deadline TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
#     conn.commit()
#     conn.close()

# def add_transaction(parsed):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''INSERT INTO transactions (amount, category, type, date, note) 
#                  VALUES (?, ?, ?, ?, ?)''',
#               (parsed['amount'], parsed['category'], parsed['type'], 
#                parsed['date'], parsed['note']))
#     conn.commit()
#     conn.close()

# def get_transactions(limit=100):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('SELECT id, amount, category, type, date, note FROM transactions ORDER BY date DESC LIMIT ?', (limit,))
#     rows = c.fetchall()
#     conn.close()
#     return [{'id': r[0], 'amount': r[1], 'category': r[2], 'type': r[3], 'date': r[4], 'note': r[5]} for r in rows]

# def get_monthly_summary():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''
#         SELECT 
#             strftime('%Y-%m', date) as month,
#             SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as income,
#             SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as expenses,
#             SUM(CASE WHEN type='income' THEN amount ELSE -amount END) as net
#         FROM transactions
#         GROUP BY strftime('%Y-%m', date)
#         ORDER BY month
#     ''')
#     rows = c.fetchall()
#     conn.close()
    
#     return [{'month': r[0], 'income': r[1], 'expenses': r[2], 'net': r[3]} for r in rows]

# def set_budget(amount):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     current_month = datetime.now().strftime('%Y-%m')
#     c.execute('''
#         INSERT OR REPLACE INTO budgets (amount, month)
#         VALUES (?, ?)
#     ''', (amount, current_month))
#     conn.commit()
#     conn.close()

# def get_budget():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     current_month = datetime.now().strftime('%Y-%m')
#     c.execute('SELECT amount FROM budgets WHERE month=?', (current_month,))
#     result = c.fetchone()
#     conn.close()
#     return result[0] if result else None

# def update_transaction(transaction_id, updated_data):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''
#         UPDATE transactions 
#         SET amount=?, category=?, type=?, date=?, note=?
#         WHERE id=?
#     ''', (updated_data['amount'], updated_data['category'], updated_data['type'], 
#           updated_data['date'], updated_data['note'], transaction_id))
#     conn.commit()
#     conn.close()

# def delete_transaction(transaction_id):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('DELETE FROM transactions WHERE id=?', (transaction_id,))
#     conn.commit()
#     conn.close()

# def set_savings_goal(name, target_amount, deadline):
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('''
#         INSERT INTO savings_goals (name, target_amount, deadline)
#         VALUES (?, ?, ?)
#     ''', (name, target_amount, deadline))
#     conn.commit()
#     conn.close()

# def get_savings_goal():
#     conn = sqlite3.connect(DB_NAME)
#     c = conn.cursor()
#     c.execute('SELECT name, target_amount, deadline FROM savings_goals ORDER BY created_at DESC')
#     rows = c.fetchall()
#     conn.close()
#     return [{'name': r[0], 'target': r[1], 'deadline': r[2]} for r in rows]



# storage.py
import sqlite3
import bcrypt
from datetime import datetime

DB_NAME = 'budgetbuddy.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Users table — full_name added
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  username TEXT UNIQUE,
                  full_name TEXT,
                  user_id TEXT,
                  password_hash TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Migrate existing DB: add full_name column if it doesn't exist yet
    try:
        c.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    except sqlite3.OperationalError:
        pass  # column already exists, ignore

    # Transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, category TEXT,
                  type TEXT, date TEXT, note TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')

    # Budgets table
    c.execute('''CREATE TABLE IF NOT EXISTS budgets
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, month TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')

    # Savings goals table
    c.execute('''CREATE TABLE IF NOT EXISTS savings_goals
                 (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT,
                  target_amount REAL, deadline TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')

    # User settings table
    c.execute('''CREATE TABLE IF NOT EXISTS user_settings
                 (id INTEGER PRIMARY KEY, user_id INTEGER, key TEXT, value TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')

    conn.commit()
    conn.close()


def create_user(username, password, full_name=""):
    """Returns user_id on success, None if username already taken."""
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute('INSERT INTO users (username, full_name, password_hash) VALUES (?, ?, ?)',
                  (username, full_name.strip(), password_hash))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def verify_user(username, password):
    """Returns (user_id, full_name) on success, None on failure."""
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('SELECT id, password_hash, full_name FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    if result:
        user_id, password_hash, full_name = result
        if bcrypt.checkpw(password.encode('utf-8'), password_hash):
            return user_id, (full_name or username)
    return None


def add_transaction(user_id, parsed):
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('''INSERT INTO transactions (user_id, amount, category, type, date, note)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (user_id, parsed['amount'], parsed['category'], parsed['type'],
               parsed['date'], parsed['note']))
    conn.commit()
    conn.close()


def get_transactions(user_id, limit=100):
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('''SELECT id, amount, category, type, date, note
                 FROM transactions
                 WHERE user_id=?
                 ORDER BY date DESC
                 LIMIT ?''', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [{'id':r[0],'amount':r[1],'category':r[2],'type':r[3],'date':r[4],'note':r[5]} for r in rows]


def get_monthly_summary(user_id):
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('''
        SELECT
            strftime('%Y-%m', date) as month,
            SUM(CASE WHEN type='income'  THEN amount ELSE 0   END) as income,
            SUM(CASE WHEN type='expense' THEN amount ELSE 0   END) as expenses,
            SUM(CASE WHEN type='income'  THEN amount ELSE -amount END) as net
        FROM transactions
        WHERE user_id = ?
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{'month':r[0],'income':r[1],'expenses':r[2],'net':r[3]} for r in rows]


def set_budget(user_id, amount):
    conn         = sqlite3.connect(DB_NAME)
    c            = conn.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    c.execute('''INSERT OR REPLACE INTO budgets (user_id, amount, month) VALUES (?, ?, ?)''',
              (user_id, amount, current_month))
    conn.commit()
    conn.close()


def get_budget(user_id):
    conn          = sqlite3.connect(DB_NAME)
    c             = conn.cursor()
    current_month = datetime.now().strftime('%Y-%m')
    c.execute('SELECT amount FROM budgets WHERE user_id = ? AND month = ?', (user_id, current_month))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def update_transaction(user_id, transaction_id, updated_data):
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('''UPDATE transactions
                 SET amount=?, category=?, type=?, date=?, note=?
                 WHERE id=? AND user_id=?''',
              (updated_data['amount'], updated_data['category'], updated_data['type'],
               updated_data['date'], updated_data['note'], transaction_id, user_id))
    conn.commit()
    conn.close()


def delete_transaction(user_id, transaction_id):
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id=? AND user_id=?', (transaction_id, user_id))
    conn.commit()
    conn.close()


def set_savings_goal(user_id, name, target_amount, deadline):
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('''INSERT INTO savings_goals (user_id, name, target_amount, deadline)
                 VALUES (?, ?, ?, ?)''', (user_id, name, target_amount, deadline))
    conn.commit()
    conn.close()


def get_savings_goal(user_id):
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('SELECT name, target_amount, deadline FROM savings_goals WHERE user_id=? ORDER BY created_at DESC',
              (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{'name':r[0],'target':r[1],'deadline':r[2]} for r in rows]


def set_user_setting(user_id, key, value):
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_settings (user_id, key, value) VALUES (?, ?, ?)''',
              (user_id, key, value))
    conn.commit()
    conn.close()


def get_user_setting(user_id, key):
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('SELECT value FROM user_settings WHERE user_id=? AND key=?', (user_id, key))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def update_username(user_id, new_username):
    """Returns True on success, False if username already taken."""
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    try:
        c.execute('UPDATE users SET username=? WHERE id=?', (new_username, user_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def update_password(user_id, new_password):
    """Hash and store new password."""
    conn          = sqlite3.connect(DB_NAME)
    c             = conn.cursor()
    new_hash      = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    c.execute('UPDATE users SET password_hash=? WHERE id=?', (new_hash, user_id))
    conn.commit()
    conn.close()


def get_user_settings(user_id):
    conn = sqlite3.connect(DB_NAME)
    c    = conn.cursor()
    c.execute('SELECT key, value FROM user_settings WHERE user_id=?', (user_id,))
    rows = c.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}