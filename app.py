from flask import Flask , render_template, flash, redirect, url_for, session, logging, request
from data import Tasks
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import os
import pymysql.cursors

app = Flask(__name__)

tasks = Tasks()



@app.route('/')
def index():
        return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        un = os.environ['DB_USER']
        pw = os.environ['DB_PASS']
        connection = pymysql.connect(host='localhost', 
                                     user=un,
                                     password=pw,
                                     db='notekeeper',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        cur = connection.cursor()

        check = cur.execute("SELECT * FROM users WHERE username = (%s)",(username))
        if int(check) > 0:
            flash('That username is already taken. Please choose another.')
            return render_template('register.html', form=form)

        else:
            cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
            connection.commit()
            flash('You are now registered and can log in', 'success')
            cur.close()
            connection.close()
            return redirect(url_for('index'))
            

        
    return render_template('register.html', form=form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwdCandidate = request.form['password']

        un = os.environ['DB_USER']
        pw = os.environ['DB_PASS']
        connection = pymysql.connect(host='localhost', 
                                     user=un,
                                     password=pw,
                                     db='notekeeper',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        cur = connection.cursor()
        check = cur.execute("SELECT * FROM users WHERE username = (%s)",(username))

        if int(check) > 0:
            data = cur.fetchone()
            pwd = data['password']

            if sha256_crypt.verify(pwdCandidate, pwd):
                session['loggedin'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))


                app.logger.info('PASSWORD MATCHED')
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)

            cur.close()

        else:
            error = 'Username not found'
            return render_template('login.html', error=error)



    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.secret_key = 'secret12345'
    app.run(debug = True)
    
