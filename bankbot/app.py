# app.py
from __future__ import annotations
import os, sqlite3, datetime as dt
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g, flash
from werkzeug.security import generate_password_hash, check_password_hash

from nlu import get_intent, parse_amount, parse_name, load_or_train

BASE_DIR = Path(__file__).resolve().parent
DATASET_CSV = str(BASE_DIR / "dataset.csv")
DB_PATH = str(BASE_DIR / "database.db")

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        number TEXT NOT NULL,
        balance REAL NOT NULL DEFAULT 50000,
        card_blocked INTEGER NOT NULL DEFAULT 0,
        card_limit REAL NOT NULL DEFAULT 50000,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL,
        tdate TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    );
    """)
    db.commit()

    # seed one user if not exists
    cur.execute("SELECT id FROM users WHERE email=?", ("demo@bank.com",))
    if not cur.fetchone():
        cur.execute("INSERT INTO users(email,password,name) VALUES(?,?,?)",
                    ("demo@bank.com", generate_password_hash("demo123"), "Demo User"))
        uid = cur.lastrowid
        cur.execute("INSERT INTO accounts(user_id, number, balance) VALUES(?,?,?)",
                    (uid, "1234 5678 9012", 75000))
        acc_id = cur.lastrowid
        seed_tx = [
            ("Salary Credit", 50000.00),
            ("Amazon Purchase", -2499.00),
            ("Zomato", -650.00),
            ("Electricity Bill", -1900.00),
        ]
        for desc, amt in seed_tx:
            cur.execute("INSERT INTO transactions(account_id,tdate,description,amount) VALUES(?,?,?,?)",
                        (acc_id, dt.date.today().isoformat(), desc, amt))
        db.commit()

# Flask App
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
app.secret_key = "dev-secret-change-me"
app.teardown_appcontext(close_db)

# Ensure model trained on startup
load_or_train(DATASET_CSV)

def login_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE email=?", (email,))
        row = cur.fetchone()
        if row and check_password_hash(row["password"], password):
            session['user_id'] = row['id']
            session['name'] = row['name']
            return redirect(url_for('dashboard'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        if not (name and email and password):
            flash("Fill all fields", "warning")
        else:
            try:
                db = get_db()
                cur = db.execute("INSERT INTO users(email,password,name) VALUES(?,?,?)",
                                 (email, generate_password_hash(password), name))
                uid = cur.lastrowid
                db.execute("INSERT INTO accounts(user_id,number,balance) VALUES(?,?,?)",
                           (uid,"9999 0000 1111",50000))
                db.commit()
                flash("Account created. Please login.", "success")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("Email already exists", "danger")
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    acc = db.execute("SELECT * FROM accounts WHERE user_id=?", (session['user_id'],)).fetchone()
    tx = db.execute("SELECT * FROM transactions WHERE account_id=? ORDER BY id DESC LIMIT 5", (acc['id'],)).fetchall()
    return render_template('dashboard.html', name=session.get('name'), account=acc, tx=tx)

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html', name=session.get('name'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------- Chat API ----------------
@app.post('/api/chat')
@login_required
def api_chat():
    data = request.get_json(force=True) or {}
    msg = (data.get('message') or '').strip()
    if not msg:
        return jsonify(reply="Please type something.", options=default_options())

    db = get_db()
    acc = db.execute("SELECT * FROM accounts WHERE user_id=?", (session['user_id'],)).fetchone()
    intent = get_intent(msg, DATASET_CSV)

    if intent == 'greet':
        return jsonify(reply=f"Hi {session.get('name')}! How can I help you today?", options=default_options())

    if intent == 'help':
        return jsonify(reply="I can show your balance, recent transactions, block/unblock card, transfer money, and show loan info.", options=default_options())

    if intent == 'balance':
        bal = acc['balance']
        return jsonify(reply=f"Your current balance is ₹{bal:,.2f}.", options=default_options())

    if intent == 'transactions':
        tx = db.execute("SELECT tdate, description, amount FROM transactions WHERE account_id=? ORDER BY id DESC LIMIT 5", (acc['id'],)).fetchall()
        lines = [f"{row['tdate']}: {row['description']} ({'+' if row['amount']>=0 else ''}₹{row['amount']:,.2f})" for row in tx]
        return jsonify(reply="Here are your last 5 transactions:\n" + "\n".join(lines), options=default_options())

    if intent == 'transfer':
        amount = parse_amount(msg) or 0.0
        recipient = parse_name(msg) or "Recipient"
        if amount <= 0:
            return jsonify(reply="How much should I transfer and to whom? Example: 'transfer 1500 to Ravi'", options=default_options())
        if acc['balance'] < amount:
            return jsonify(reply=f"Insufficient balance. Available: ₹{acc['balance']:,.2f}", options=default_options())
        # Perform transfer
        new_bal = acc['balance'] - amount
        db.execute("UPDATE accounts SET balance=? WHERE id=?", (new_bal, acc['id']))
        db.execute("INSERT INTO transactions(account_id,tdate,description,amount) VALUES(?,?,?,?)",
                   (acc['id'], dt.date.today().isoformat(), f"Transfer to {recipient}", -amount))
        db.commit()
        return jsonify(reply=f"Transferred ₹{amount:,.2f} to {recipient}. New balance: ₹{new_bal:,.2f}.", options=default_options())

    if intent == 'card_block':
        # toggle block/unblock depending on text
        text = msg.lower()
        block = True
        if "unblock" in text or "un-freeze" in text:
            block = False
        db.execute("UPDATE accounts SET card_blocked=? WHERE id=?", (1 if block else 0, acc['id']))
        db.commit()
        state = "blocked" if block else "unblocked"
        return jsonify(reply=f"Your card is now {state}.", options=default_options())

    if intent == 'card_limit':
        if "increase" in msg.lower():
            new_limit = acc['card_limit'] + 10000
        elif "decrease" in msg.lower():
            new_limit = max(5000, acc['card_limit'] - 10000)
        else:
            return jsonify(reply=f"Your card limit is ₹{acc['card_limit']:,.2f}. Say 'increase' or 'decrease' to change it.", options=default_options())
        db.execute("UPDATE accounts SET card_limit=? WHERE id=?", (new_limit, acc['id']))
        db.commit()
        return jsonify(reply=f"Card limit updated to ₹{new_limit:,.2f}.", options=default_options())

    if intent == 'loan_info':
        # For demo, compute a fake loan
        principal = 200000
        paid = 65000
        outstanding = principal - paid
        return jsonify(reply=f"Home Loan — Principal: ₹{principal:,.0f}, Paid: ₹{paid:,.0f}, Outstanding: ₹{outstanding:,.0f}. EMI: ₹12,500.", options=default_options())

    if intent == 'logout':
        session.clear()
        return jsonify(reply="You have been logged out.", options=[])

    # fallback
    return jsonify(reply="Sorry, I didn't get that. Try: 'balance', 'transactions', 'transfer 1000 to Ravi', 'block my card'.", options=default_options())

def default_options():
    return [
        {"label":"💰 Balance", "text":"check balance"},
        {"label":"📄 Transactions", "text":"show my recent transactions"},
        {"label":"💳 Card Status", "text":"block my card"},
        {"label":"🔁 Transfer", "text":"transfer 1000 to Ravi"},
        {"label":"🏦 Loan", "text":"show my loan details"},
    ]

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
