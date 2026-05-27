from flask import Flask, render_template, request
from datetime import date, datetime
app = Flask(__name__)


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
        print(username, password)
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
