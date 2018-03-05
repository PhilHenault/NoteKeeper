#online task keeper

from flask import Flask , render_template
from data import Tasks

tasks = Tasks()


app = Flask(__name__)

@app.route('/')
def index():
		return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

if __name__ == '__main__':
	app.run(debug = True)
	print(tasks)
