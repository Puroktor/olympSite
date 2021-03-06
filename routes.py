import re
import bcrypt
from flask import Blueprint, render_template, session, redirect, request
from sqlalchemy import func, desc
from sqlalchemy.exc import NoResultFound
from db import db
from models import Task, User, Completed

blueprint = Blueprint('controllers', __name__, template_folder='templates')


@blueprint.route('/')
def index():
    return render_template('index.html', user=session.get('user'))


@blueprint.route('/tasks')
def tasks():
    olymp_tasks = db.session.query(Task.id, Task.name).all()
    return render_template('tasks.html', user=session.get('user'), tasks=olymp_tasks)


@blueprint.route('/tasks/<task_id>', methods=['GET', 'POST'])
def task(task_id):
    if 'user' not in session:
        return redirect('/login')
    else:
        try:
            olymp_task = Task.query.filter(Task.id == task_id).one()
        except NoResultFound:
            return "No such task!", 400
        user_id, = db.session.query(User.id).filter(User.name == session.get('user')).one()
        time = db.session.query(Completed.time).filter(Completed.task_id == task_id,
                                                       Completed.user_id == user_id).first()
        if request.method == 'POST':
            if time:
                return 'You have already completed this task', 400
            answer = request.form.get('answer').strip()
            if not answer:
                return render_template('task.html', user=session.get('user'), task=olymp_task,
                                       error='Write down your answer!')

            if olymp_task.answer == answer:
                db.session.add(Completed(user_id=user_id, task_id=task_id))
                db.session.commit()
                return redirect(f'/tasks/{task_id}')
            else:
                return render_template('task.html', user=session.get('user'), task=olymp_task, answer=answer,
                                       error='Wrong answer!')
        else:
            if time:
                return render_template('task.html', time=time[0], user=session.get('user'), task=olymp_task)
            else:
                return render_template('task.html', user=session.get('user'), task=olymp_task)


@blueprint.route('/leaderboard')
def leaderboard():
    all_users = db.session.query(User.id, User.name, func.count(User.name).label('done'),
                                 func.sum(func.strftime('%s', func.now()) - func.strftime('%s', Completed.time)).label(
                                     'duration')) \
        .join(Completed) \
        .filter(User.id == Completed.user_id) \
        .group_by(User.name) \
        .order_by(desc('done'), desc('duration')) \
        .all()
    all_tasks = db.session.query(Task.id, Task.name).all()
    all_completed = Completed.query.all()
    completed_dict = {(comp.user_id, comp.task_id): comp.time for comp in all_completed}
    return render_template('leaderboard.html', tasks=all_tasks, users=all_users, dict=completed_dict,
                           user=session.get('user', None))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return 'You are already registered!', 400
    elif request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()

        if not name or not email or not password:
            return render_template('register.html', name=name, email=email, password=password,
                                   error='Fill in all fields of the form!')

        if len(name) == 0 or len(name) > 30:
            return render_template('register.html', name=name, email=email, password=password,
                                   error='Name length must be between 1-30')

        if len(email) > 30:
            return render_template('register.html', name=name, email=email, password=password,
                                   error='Email length must be <= 30')

        if len(password) == 0:
            return render_template('register.html', name=name, email=email, password=password,
                                   error='Password length must be > 0')

        if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            return render_template('register.html', name=name, email=email, password=password, error='Not valid email!')

        user = db.session.query(User.id).filter(User.name == name).first()
        if user:
            return render_template('register.html', name=name, email=email, password=password,
                                   error='User with such name already exists!')

        user = db.session.query(User.id).filter(User.email == email).first()
        if user:
            return render_template('register.html', name=name, email=email, password=password,
                                   error='User with such email already registered!')

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
            return render_template('login.html', name=name, password=password, error='Fill in all fields of the form!')

        user = db.session.query(User.name, User.psw_hash).filter(User.name == name).first()

        if not user:
            return render_template('login.html', name=name, password=password, error='Wrong username!')

        if bcrypt.checkpw(password.encode('utf-8'), user.psw_hash):
            session['user'] = name
            return redirect('/')
        else:
            return render_template('login.html', name=name, password=password, error='Wrong password!')
    else:
        return render_template('login.html')


@blueprint.route('/logout', methods=['POST'])
def logout():
    if 'user' not in session:
        return 'You are not logged in!', 400
    else:
        session.pop('user', None)
        return redirect('/')
