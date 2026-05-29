from flask import Flask, render_template, request, redirect, url_for
from datetime import date, datetime
app = Flask(__name__)


pseudo_bd = {'admin':'123'}


@app.route('/')
def index():
    today = date.today()
    return render_template('index.html', today = today.strftime('%Y-%m-%d'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if pseudo_bd.get(username) == password:
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
