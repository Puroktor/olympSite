import re
import bcrypt
from flask import Blueprint, render_template, session, redirect, request
from db import db
from models import Task, User, Completed

blueprint = Blueprint('controllers', __name__, template_folder='templates')


@blueprint.route('/')
def index():
    return render_template('index.html', user=session.get('user', None))


@blueprint.route('/tasks')
def tasks():
    olymp_tasks = Task.query.order_by(Task.id).all()
    return render_template('tasks.html', user=session.get('user'), tasks=olymp_tasks)


@blueprint.route('/tasks/<task_id>', methods=['GET', 'POST'])
def task(task_id):
    if 'user' not in session:
        return redirect('/login')
    else:
        olymp_task = Task.query.filter(Task.id == task_id).first()
        user = User.query.filter(User.name == session.get('user')).first()
        completed = Completed.query.filter(Completed.task_id == task_id,
                                           Completed.user_id == user.id).first()
        if request.method == 'POST':
            if completed:
                return 'You have already completed this task', 400
            answer = request.form.get('answer')
            if not answer:
                return render_template('task.html', user=user.id, task=olymp_task,
                                       error='Write down your answer!')

            if olymp_task.answer == answer.strip():
                db.session.add(Completed(user_id=user.id, task_id=task_id))
                db.session.commit()
                return redirect(f'/tasks/{task_id}')
            else:
                return render_template('task.html', user=user.id, task=olymp_task,
                                       error='Wrong answer!')
        else:
            if completed:
                return render_template('task.html', time=completed.time, user=user.id, task=olymp_task)
            else:
                return render_template('task.html', user=user.id, task=olymp_task)


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return 'You are already registered!', 400
    elif request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not password:
            return render_template('register.html', error='Fill in all fields of the form!')

        if len(name) > 100:
            return render_template('register.html', error='Name length must be <= 100')

        if len(email) > 30:
            return render_template('register.html', error='Email length must be <= 30')

        if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            return render_template('register.html', error='Not valid email!')

        user = User.query.filter(User.name == name).first()

        if user:
            return render_template('register.html', error='User with such name already exists!')

        db.session.add(User(name=name, email=email, psw_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())))
        db.session.commit()
        session['user'] = name
        return redirect('/')
    else:
        return render_template('register.html')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return 'You are already logged in!', 400
    elif request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        if not name or not password:
            return render_template('login.html', error='Fill in all fields of the form!')

        user = User.query.filter(User.name == name).first()

        if not user:
            return render_template('login.html', error='Wrong username!')

        if bcrypt.checkpw(password.encode('utf-8'), user.psw_hash):
            session['user'] = name
            return redirect('/')
        else:
            return render_template('login.html', error='Wrong password!')
    else:
        return render_template('login.html')


@blueprint.route('/logout', methods=['POST'])
def logout():
    if 'user' not in session:
        return 'You are not logged in!', 400
    else:
        session.pop('user', None)
        return redirect('/')
