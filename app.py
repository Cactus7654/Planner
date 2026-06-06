from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date, datetime
import db
app = Flask(__name__)
app.secret_key = 'parol132'



@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    now = datetime.now()
    today_habits = db.get_habits(session['user_id'])
    for habit in today_habits:
        last = db.get_last_completion(session['user_id'], habit['description'])
        urgency = (now-datetime.strptime(last['completed_at'],'%Y-%m-%d %H:%M:%S'))/last['regularity']


    return render_template('index.html',
                           name=session['username'], today_habits=today_habits)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        unam = request.form.get('username')
        passw = request.form.get('password')
        if db.register_user(unam, passw):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='user is already exists')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        check_user_from_db = db.check_user(username, password)
        if check_user_from_db:
            session['user_id'] = check_user_from_db['id']
            session['username'] = check_user_from_db['username']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/add_habit', methods=['POST'])
def add_habit():
    des = request.form.get('description').strip()
    reg = request.form.get('regularity')
    if des:
        db.add_habit(session['user_id'], des, reg)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/add_completion', methods = ["POST"])
def add_completion():
    us = session['user_id']
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    des = request.form.get('description')
    if request.form.get('cancel') == '1':
        db.cancel_completion(us, des, db.get_last_execution_date(us, des))
    db.add_completion(us, des, now)
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)