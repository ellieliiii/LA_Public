from flask import Flask, render_template, request, redirect, session, flash, make_response, json, url_for, jsonify, g
from markupsafe import Markup
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from sqlalchemy import text
from sqlalchemy.sql import text
import random
import string
import os
from markupsafe import Markup  
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.sql import text

app = Flask(__name__)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# @app.before_request
# def before_request_func():
#     if not getattr(g, '_first_request', False):
#         g._first_request = True
#         init_notes()
#         init_admin_todo_account()
#         session.pop('unlocked_note_viewed', None)


bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_FILE_PATH']
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.secret_key = "b'\xd9\x04U\xf8v\x0e4\xb42f\xa9\x97\x97}S\x92'"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return TodoUser.query.get(int(user_id))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    current_task = db.Column(db.Integer, default=1)
    time1 = db.Column(db.DateTime)
    time2 = db.Column(db.DateTime)
    time3 = db.Column(db.DateTime)
class Todo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(100), nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('todo_user.id'), nullable=False)  # Reference to TodoUser
    owner = db.relationship('TodoUser', backref='todos')


class TodoUser(db.Model, UserMixin):
    __tablename__ = 'todo_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    # Flask-Login integration
    def get_id(self):
        return str(self.id)


class Note(db.Model):
    __tablename__ = 'notes'  # this sets the table name to "notes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=True)
    locked = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(120))

# class Event(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'), nullable=False)
#     event_type = db.Column(db.String(50), nullable=False)
#     event_data = db.Column(db.JSON, nullable=False)
#     url = db.Column(db.String(200), nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=True)
    event_data = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    url = db.Column(db.String)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.user_id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    correct = db.Column(db.Boolean)
    ip_address = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user = TodoUser.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError('That username already exists. Please choose a different one.')
class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

def record_survey_data(user_id, question, response, correct=False):
    ip_address = request.remote_addr  # Get the client's IP address
    timestamp = datetime.now()  # Get the current timestamp
    # No need to open a connection, as SQLAlchemy handles this

    # If question is one of the tasks, include a correct value
    new_response = Response(
        user_id=user_id,
        question=question,
        response=response,
        correct=correct,
        ip_address=ip_address,
        timestamp=timestamp
    )

    db.session.add(new_response)
    db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        # Using SQLAlchemy ORM to find the user
        user = User.query.filter_by(user_id=user_id, password=password).first()
        print("get the user input!!")
        if user:
            session['user_id'] = user.user_id
            task_url = f'/{prefix}/task{user.current_task}'
            return redirect(task_url)

        else:
            flash('Invalid User ID or password.')

        
    return render_template('index.html', prefix = prefix)

@app.route('/home')
def home():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    return render_template('home.html', prefix = prefix)


@app.route('/login', methods=['GET', 'POST'])
def login():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Intentionally vulnerable SQL query
        query = f"SELECT id FROM todo_user WHERE username = '{username}' AND password = '{password}'"
        result = db.session.execute(text(query)).first()

        if result:
            # Fetch the user object from the database
            user_id = result[0]  # Get the user ID from the result
            user = TodoUser.query.get(user_id)
            login_user(user)  # Use Flask-Login to handle user session
            flash('Login successful!', 'success')
            dashboard_url = f'/{prefix}' + url_for('dashboard')
            return redirect(dashboard_url)
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form, prefix=prefix)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    todos = Todo.query.filter_by(owner=current_user).all()
    return render_template('dashboard.html', todos=todos, prefix=prefix)

@app.route('/dashboard/add', methods=['POST'])
@login_required
def add():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    todo = request.form['todo']
    new_todo = Todo(task=todo, done=False, user_id=current_user.id)  # Use user_id, not owner
    db.session.add(new_todo)
    db.session.commit()
    dashboard_url = f'/{prefix}' + url_for('dashboard')
    return redirect(dashboard_url)

@app.route('/dashboard/check/<int:todo_id>', methods=['POST'])
@login_required
def check(todo_id):
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    todo = Todo.query.get_or_404(todo_id)
    if todo.owner != current_user:
        abort(403)
    todo.done = not todo.done
    db.session.commit()
    dashboard_url = f'/{prefix}' + url_for('dashboard')
    return redirect(dashboard_url)

@app.route('/dashboard/delete/<int:todo_id>')
@login_required
def delete(todo_id):
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    todo = Todo.query.get_or_404(todo_id)
    if todo.owner != current_user:
        abort(403)
    db.session.delete(todo)
    db.session.commit()
    dashboard_url = f'/{prefix}' + url_for('dashboard')
    return redirect(dashboard_url)

@app.route('/dashboard/edit/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def edit(todo_id):
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    todo = Todo.query.get_or_404(todo_id)
    if todo.owner != current_user:
        abort(403)
    if request.method == 'POST':
        todo.task = request.form['todo']
        db.session.commit()
        dashboard_url = f'/{prefix}' + url_for('dashboard')
        return redirect(dashboard_url)
    else:
        return render_template('edit.html', todo=todo, prefix=prefix)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    login_url = f'/{prefix}/login' 
    return redirect(login_url)


@app.route('/register', methods=['GET', 'POST'])
def register():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    form = RegisterForm()
    if form.validate_on_submit():
        new_todo_user = TodoUser(username=form.username.data, password=form.password.data)
        db.session.add(new_todo_user)
        db.session.commit()
        flash('Registration successful. You can now log in.', 'success')
        login_url = f'/{prefix}/login' 
        return redirect(login_url)
    return render_template('register.html', form=form, prefix=prefix)

@app.route('/background-image.jpg')
def hint():
    return render_template('hint.html')

def get_current_task(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        return user.current_task
    else:
        flash('Invalid User ID or password.')
        return None


@app.route('/task1', methods=['GET', 'POST'])
def task1():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    user_id = session.get('user_id')
    if user_id is None:
        flash('You must be logged in to access this page.')
        index_url = '/' + prefix
        return redirect(index_url)


    if get_current_task(user_id) != 1 and get_current_task(user_id)<4:
        return redirect(f'/{prefix}/task{get_current_task(user_id)}')
    elif get_current_task(user_id)>=4:
        return redirect(f'/{prefix}/thankyou')

    record_entry_time(user_id, 1)
    if request.method == 'POST':
        password = request.form.get('password')
        correct = (password == 'Flag{S3cr3t_P@ssw0rd_2023}')
        record_survey_data(user_id, 1, password, correct)  # record every attempt
        current_task = get_current_task(user_id)
        if correct:
            if current_task is not None:
                update_current_task(user_id, current_task + 1)
                response = make_response(redirect('/'+ prefix +'continue'))
                response.set_cookie('task1StartTime', '', expires=0)
                return response
        else:
            flash('Wrong password. Please try again.')
            return render_template('task1.html', user_id=user_id, prefix = prefix)

    else:
        response = make_response(render_template('task1.html', user_id=user_id, prefix = prefix))
        if not request.cookies.get('task1StartTime'):
            response.set_cookie('task1StartTime', datetime.now().isoformat(), max_age=40*60)
        return response


@app.route('/task2', methods=['GET', 'POST'])
def task2():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    user_id = session.get('user_id')
    if user_id is None:
        flash('You must be logged in to access this page.')
        index_url = '/' + prefix
        return redirect(index_url)
    if get_current_task(user_id) != 2 and get_current_task(user_id)<4:
        return redirect(f'/{prefix}/task{get_current_task(user_id)}')
    elif get_current_task(user_id)>=4:
        return redirect(f'/{prefix}/thankyou')

    record_entry_time(user_id, 2)
    if request.method == 'POST':
        password = request.form.get('password')
        correct = (password == 'Flag{Un1corn_R@inbow_2023}')
        record_survey_data(user_id, 2, password, correct)  # record every attempt
        current_task = get_current_task(user_id)
        if correct:
            if current_task is not None:
                update_current_task(user_id, current_task + 1)
                continue1_url = f'/{prefix}/continue1'
                response = make_response(redirect(continue1_url))
                response.set_cookie('task2StartTime', '', expires=0)
                return response
        else:
            flash('Wrong password. Please try again.')
            return render_template('task2.html', user_id=user_id, prefix=prefix)
    else:
        response = make_response(render_template('task2.html', user_id=user_id, prefix=prefix))
        if not request.cookies.get('task2StartTime'):
            response.set_cookie('task2StartTime', datetime.now().isoformat(), max_age=40*60)
        return response

@app.route('/task3', methods=['GET', 'POST'])
def task3():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    user_id = session.get('user_id')
    if user_id is None:
        flash('You must be logged in to access this page.')
        return redirect('/')
    if get_current_task(user_id) != 3 and get_current_task(user_id)<4:
        return redirect(f'/{prefix}/task{get_current_task(user_id)}')
    elif get_current_task(user_id)>=4:
        return redirect(f'/{prefix}/thankyou')

    record_entry_time(user_id, 3)
    if request.method == 'POST':
        password = request.form.get('password')
        correct = (password == 'Flag{ChocoL@te_C@ke_2023}')
        record_survey_data(user_id, 3, password, correct)  # record every attempt
        current_task = get_current_task(user_id)
        if correct:
            if current_task is not None:
                update_current_task(user_id, current_task + 1)
                thankyou_url = f'/{prefix}'+url_for('thankyou')
                response = make_response(redirect(thankyou_url))
                response.set_cookie('task3StartTime', '', expires=0)
                return response
        else:
            flash('Wrong password. Please try again.')
            return render_template('task3.html', user_id=user_id, prefix=prefix)
    else:
        response = make_response(render_template('task3.html', user_id=user_id, prefix=prefix))
        if not request.cookies.get('task3StartTime'):
            response.set_cookie('task3StartTime', datetime.now().isoformat(), max_age=40*60)
        return response
        
@app.route('/continue')
def continue_task():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    user_id = session.get('user_id')
    return render_template('continue.html', user_id=user_id, prefix=prefix)

@app.route('/continue1')
def continue_task1():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    user_id = session.get('user_id')
    return render_template('continue1.html', user_id=user_id, prefix=prefix)

@app.route('/thankyou')
def thankyou():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    user_id = session.get('user_id')
    return render_template('thankyou.html', user_id=user_id, prefix=prefix)

@app.route('/survey_continue', methods=['GET', 'POST'])
def survey_continue():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    if request.method == 'POST':
        amount = request.form.get('amount')
        user_id = session.get('user_id')
        if user_id is not None:
            record_survey_data(user_id, 'survey_continue', amount)
            task2_url = f'/{prefix}'+url_for('task2')
            return redirect(task2_url)
    return render_template('survey_continue.html', prefix=prefix)

@app.route('/survey_continue1', methods=['GET', 'POST'])
def survey_continue1():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    if request.method == 'POST':
        amount = request.form.get('amount')
        user_id = session.get('user_id')
        if user_id is not None:
            record_survey_data(user_id, 'survey_continue1', amount)
            task3_url = f'/{prefix}'+url_for('task3')
            return redirect(task3_url)
    return render_template('survey_continue1.html', prefix=prefix)

@app.route('/survey_quit', methods=['GET', 'POST'])
def survey_quit():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    if request.method == 'POST':
        amount = request.form.get('amount')
        user_id = session.get('user_id')
        if user_id is not None:
            record_survey_data(user_id, 'survey_quit', amount)
            thankyou_url = f'/{prefix}'+url_for('thankyou')
            return redirect(thankyou_url)
    return render_template('survey_quit.html', prefix=prefix)


def record_event_data(user_id, event_data):
    timestamp = datetime.utcnow()
    event = Event(user_id=user_id, event_type=event_data['type'], event_data=json.dumps(event_data), timestamp=timestamp)
    db.session.add(event)
    db.session.commit()

@app.route('/log_event', methods=['POST'])
def log_event():
    app.logger.info('log_event endpoint hit')
    # Continue with POST request handling
    event_data = request.get_json(force=True)  # Get the event data from the request body
    if event_data:
        # Convert event_data to a string
        event_data_str = json.dumps(event_data)
        # Extract event type from event_data
        event_type = event_data.get('type')
        event_url = event_data.get('url')
        # Create a new Event object, without web_user_id.
        new_event = Event(event_type=event_type, event_data=event_data_str, url=event_url)
        # Add the new event to the database session
        db.session.add(new_event)

        # Commit the session to save the new event
        db.session.commit()

    return jsonify({'message': 'Event logged successfully'}), 200

# from here is app2
@app.route('/home2')
def home2():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    notes = Note.query.all() # fetch all notes from the database
    return render_template('home2.html', notes=notes, prefix=prefix)

@app.route('/note/<int:note_id>', methods=['GET', 'POST'])
def note_page(note_id):
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    home2_url = f'/{prefix}/home2' 
    note = Note.query.get(note_id)  # fetch a note from the database using its ID
    if note is None:
        return "Note not found", 404

    if request.method == 'POST':
        if not note.locked:
            note.content = request.form.get('content')
            db.session.commit()   
        return redirect(home2_url)

    # Determine if the user accessed this page directly
    referer = request.headers.get('Referer')
    if referer:
        parsed_url = urlparse(referer)
        direct_access = parsed_url.path != home2_url
    else:
        direct_access = True

    # Check if the note is locked and if it has been unlocked in this session
    if note.locked and not session.get(f'/{prefix}/note_{note.id}_unlocked'):
        if direct_access:
            # Bypass the password check if accessed directly
            return render_template('note.html', note_id=note_id, content=note.content, title=note.title, prefix=prefix)
        else:
            # Render the unlock page if accessed from /home2
            print("I AM ACCESSED WOOHOOOOO")
            return render_template('unlock_note.html', note_id=note_id, prefix=prefix)

    # If the note is not locked, or if it has been unlocked in this session, render the note content page
    return render_template('note.html', note_id=note_id, content=note.content, title=note.title, prefix=prefix)


@app.route('/password/<int:note_id>', methods=['POST'])
def password(note_id):
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    password_input = request.form.get('password')
    note = Note.query.get(note_id)  # fetch a note from the database using its ID
    if note is None or note.password != password_input:
        return "Incorrect password. Back up to try again.", 403
    session[f'/{prefix}/note_{note_id}_unlocked'] = True
    return redirect(url_for('note_page', note_id=note_id, prefix=prefix))



@app.route('/new_note', methods=['GET', 'POST'])
def new_note():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        new_note = Note(title=title, content=content)
        db.session.add(new_note)
        db.session.commit()
        home2_url = f'/{prefix}/home2' 
        return redirect(home2_url)
    return render_template('new_note.html', prefix=prefix)

#comment out if running docker init funcs
# def init_notes():
#     # Check if notes are already added
#     if Note.query.count() == 0:
#         notes = [
#             {'title': 'Passwords', 'id': 1, 'content': 'Password to online banking: Flag{S3cr3t_N0t3_2023}.\nPassword to email: fsjoif3243\nPassword to iPad: 234jsdifoj', 'locked': True, 'password': ('P@ssw0rd')},
#             {'title': 'Secret Girlfriends List','id': 2, 'content': 'Fletcher\nMonica Geller\nRachel Green\nLily Aldrin'},
#             {'title': 'Grocery List', 'id': 3,'content': 'Eggplant\nTomatoes\nCarrots\nGarlic Bread'},
#             {'title': 'Secret Boyfriends List', 'id': 4,'content': 'Christian Bale\nBrad Pitt\nRyan Gosling\nRyan Reynolds\nXu Song\nEugene Fitzherbert\nMatt LeBlanc Young'},
#         ]
        

#         for note in notes:
#             new_note = Note(**note)
#             db.session.add(new_note)
#             if(new_note.locked):
#                 session[f'note_{new_note.id}_unlocked'] = False

#         db.session.commit()
#         print("Notes initialized.")

# def init_admin_todo_account():
#     # Check if the admin account is already created
#     admin_user = TodoUser.query.filter_by(username='admin').first()
#     if not admin_user:
#         # Create the admin account
#         admin_user = TodoUser(username='admin', password='P@ssw0rd')
#         db.session.add(admin_user)
#         db.session.commit()
#         print("Admin TodoUser initialized.")

#         # Now, create todo items for admin
#         todos = [
#             {'task': 'change password to notes app to: Flag{S3cr3t_P@ssw0rd_2023}', 'done': True, 'user_id': admin_user.id},
#             {'task': 'buy groceries', 'done': False, 'user_id': admin_user.id},
#             {'task': 'contact gf #10', 'done': False, 'user_id': admin_user.id},
#         ]

#         for todo in todos:
#             new_todo = Todo(**todo)
#             db.session.add(new_todo)

#         db.session.commit()
#         print("Admin Todo items initialized.")
#     else:
#         print("Admin TodoUser already exists.")


# from here is app3

@app.route('/home3')
def home3():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    return render_template('home3.html', prefix=prefix)

@app.route('/account_history')
def account_history():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    # Generate random fake account history data
    transactions = generate_fake_transactions()

    return render_template('account_history.html', transactions=transactions, prefix=prefix)

@app.route('/credit_card')
def credit_card():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    # Generate random fake credit card statement data
    transactions = generate_fake_transactions()

    return render_template('credit_card.html', transactions=transactions, prefix=prefix)

@app.route('/search', methods=['POST'])
def search():
    prefix = request.headers.get('X-Forwarded-Prefix', '').strip('/')
    print(prefix)
    query = request.form['query']

    # Check for both opening and closing script tags
    if "<script>" in query and "</script>" in query:
        # XSS injection detected
        search_result = Markup(' Your CVV number is <strong>{}.</strong>'.format( "Flag{ChocoL@te_C@ke_2023}"))
    else:
        # No XSS injection detected, display the query 
        search_result = "We're sorry, but we couldn't find results for your search {}.".format(query)

    return render_template('home3.html', search_result=search_result, prefix=prefix)

def generate_fake_transactions():
    transactions = []

    for _ in range(10):
        transaction = {
            'date': datetime.now() - timedelta(days=random.randint(1, 30)),
            'description': generate_fake_description(),
            'amount': random.randint(-1000, 1000)
        }
        transactions.append(transaction)

    return transactions

def generate_fake_description():
    descriptions = [
        'Online Shopping',
        'Restaurant Payment',
        'Utility Bill',
        'Gas Station',
        'ATM Withdrawal',
        'Grocery Store',
        'Subscription Payment',
        'Entertainment',
        'Travel Expense'
    ]

    return random.choice(descriptions)


def update_current_task(user_id, task):
    # Use SQLAlchemy to update the user's current task
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        user.current_task = task
        db.session.commit()


def record_entry_time(user_id, task_num):
    user = User.query.filter_by(user_id=user_id).first()
    
    if not user:
        # Handle the case where the user does not exist
        print("User not found")
        return

    current_time = datetime.now()  # datetime object, not a string
    column_name = f"time{task_num}"
    
    # Check if the entry time already exists
    if getattr(user, column_name) is None:
        setattr(user, column_name, current_time)
        try:
            db.session.commit()
            print("Entry time recorded:", current_time)
        except Exception as e:
            db.session.rollback()
            print("Failed to record entry time:", e)
    else:
        print("Entry time already exists:", getattr(user, column_name))



@app.route('/get_remaining_time', methods=['GET'])
def get_remaining_time():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 403

    user = User.query.filter_by(user_id=user_id).first()
    if not user or user.current_task is None:
        return jsonify({'error': 'Invalid User ID or unable to fetch current task'}), 404

    start_time_column = f'time{user.current_task}'
    start_time = getattr(user, start_time_column)
    if not start_time:
        return jsonify({'error': 'Start time not found for current task'}), 404

    # No need to convert start_time since it's already a datetime object
    time_elapsed = (datetime.now() - start_time).total_seconds()
    time_remaining = max(40 * 60 - time_elapsed, 0)  # Ensure that time remaining is not negative

    return jsonify({'time_remaining': time_remaining})


def generate_users(num_users):
    for i in range(1, num_users + 1):
        user_id = f'user{i}'
        # Check if user already exists
        existing_user = User.query.filter_by(user_id=user_id).first()
        if not existing_user:
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            current_task = 1
            new_user = User(user_id=user_id, password=password, current_task=current_task)
            db.session.add(new_user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()  # Roll back the session if there's an error
                print(f"Integrity error occurred, could not add user {user_id}.")


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         generate_users(30)
#     app.run(debug=True, port=9000, host='0.0.0.0')


#docker
if __name__ == '__main__':
    app.run(port=58900, host='0.0.0.0')