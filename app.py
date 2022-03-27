from flask import Flask, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='super secret key',
    SQLALCHEMY_DATABASE_URI='sqlite:///olymp.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/')
def index():
    if 'user' in session:
        return redirect('/tasks')
    else:
        return render_template('index.html')


@app.route('/tasks')
def tasks():
    if 'user' not in session:
        return redirect('/')
    else:
        olymp_tasks = Task.query.order_by(Task.id).all()
        return render_template('tasks.html', user=session.get('user'), tasks=olymp_tasks)


@app.route('/tasks/<task_id>')
def task(task_id):
    if 'user' not in session:
        return redirect('/')
    else:
        olymp_task = Task.query.get(task_id)
        return render_template('task.html', user=session.get('user'), task=olymp_task)


@app.route('/login')
def login():
    if 'user' in session:
        return redirect('/tasks')
    else:
        session['user'] = 'abcdf'
        return redirect('/tasks')


@app.route('/logout', methods=['POST'])
def logout():
    if 'user' not in session:
        return redirect('/login')
    else:
        session.pop('user', None)
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
