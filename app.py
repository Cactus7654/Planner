from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date, datetime, timedelta
import db
app = Flask(__name__)
app.secret_key = 'parol132'



@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    now = datetime.now()
    habits_with_urgency = []
    today_habits = db.get_habits_for_dashboard(session['user_id'])
    for habit in today_habits:
        last_completion_time = habit['completed_at']
        regularity = habit['regularity']
        if last_completion_time:
            last_completion_time = datetime.strptime(last_completion_time, '%Y-%m-%d %H:%M:%S')
            difference = (now - last_completion_time).total_seconds()/60
            if regularity == 0:
                urgency = -1
            else:
                urgency = round(difference / regularity, 1)
        else:
            urgency = -1
        habits_with_urgency.append({
            'description': habit['description'],
            'regularity': habit['regularity'],
            'urgency': urgency,
            'formatted_regularity': format_regularity(regularity),
            'id': habit['id']
        })
    habits_with_urgency.sort(key=lambda h: h['urgency'], reverse=True)

    return render_template('index.html',
                           name=session['username'], today_habits=habits_with_urgency)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        unam = request.form.get('username').strip()
        passw = request.form.get('password').strip()
        if not unam:
            return render_template('register.html', error='Введите имя пользователя')
        if len(passw) < 4:
            return render_template('register.html', error='Пароль содержать минимум 4 символа')
        if db.register_user(unam, passw):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Пользователь с таким именем уже существует')
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
    date_req_minutes = (
            float(request.form.get('reg_days') or 0) * 24 * 60 +
            float(request.form.get('reg_hours') or 0) * 60 +
            float(request.form.get('reg_minutes') or 0)
    )
    if date_req_minutes == 0:
        flash('Укажите интервал', 'error')
        return redirect(url_for('index'))
    if des:
        session['play_sound'] = 'hueta'
        db.add_habit(session['user_id'], des, date_req_minutes)
        flash(f'Привычка "{des}" добавлена', 'success')
        return redirect(url_for('index'))
    else:
        flash('Введите название привычки', 'error')
        return redirect(url_for('index'))

@app.route('/add_completion', methods = ["POST"])
def add_completion():
    us = session['user_id']
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    des = request.form.get('description')
    date_req = request.form.get("date_requested")
    if request.form.get('cancel') == '1':
        db.cancel_completion(us, des, db.get_last_execution_date(us, des))
    elif date_req.strip():
        date_req = date_req.replace('T', ' ') + ':00'
        db.add_completion(us, des, date_req)
    else:
        db.add_completion(us, des, now)
    return redirect(url_for('index'))


@app.route('/delete_habit', methods = ["POST"])
def delete_habit():
    if datetime.now().second % 2 == 0:
        session['play_sound'] = 'sad'
    else:
        session['play_sound'] = 'suka'
    db.delete_habit(session['user_id'], request.form.get('delete_habit_id'))
    return redirect("/")


@app.route('/change_habit', methods=["POST"])
def change_habit():
    db.change_habit(float(request.form.get('new_regularity')), request.form.get('new_description'), session['user_id'], request.form.get('id'))
    return redirect("/")



def format_regularity(minutes_total):
    days = int(minutes_total // (24 * 60))
    hours = int(minutes_total % (24 * 60) // 60)
    minutes = int(minutes_total % 60)
    a = b = c = ''
    if days > 0:
        a = f'{days} дн '
    if hours > 0:
        b = f'{hours} ч '
    if minutes > 0:
        c = f'{minutes} мин'
    return a+b+c




if __name__ == '__main__':
    app.run(debug=True)
