#online task keeper

from flask import Flask , render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from data import Tasks
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import os




app = Flask(__name__)

tasks = Tasks()

#config
app.config['mysql_host'] = 'localhost'
app.config['mysql_user'] = os.environ.get('DB_USER')
app.config['mysql_password'] = os.environ.get('DB_PASS')
app.config['mysql_db'] = 'notekeeper'
app.config['mysql_cursorclass'] = 'DictCursor'

#initialize 
mysql = MySQL(app)




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

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
	app.secret_key = 'secret12345'
	app.run(debug = True)
	
