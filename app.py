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
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        connection.commit()
        flash('You are now registered and can log in', 'success')
        cur.close()
        connection.close()
        
        return redirect(url_for('index'))

        
    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.secret_key = 'secret12345'
    app.run(debug = True)
    
