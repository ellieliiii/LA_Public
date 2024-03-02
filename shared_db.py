from flask import Flask, session
from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
import random 
import os
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shared_db.db'  # Change the URI to your desired location
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_FILE_PATH']
db = SQLAlchemy(app)

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


def add_new_user(username, password, fun_fact, private, is_admin=False):
    new_user = User(username=username, password=password, fun_fact=fun_fact, private_fun_fact=private, is_admin=is_admin)
    db.session.add(new_user)
    db.session.commit()


def init_notes():
    # Check if notes are already added
    if Note.query.count() == 0:
        notes = [
            {'title': 'Passwords', 'id': 1, 'content': 'Password to online banking: Flag{Un1corn_R@inbow_2023}.\nPassword to email: fsjoif3243\nPassword to iPad: 234jsdifoj', 'locked': True, 'password': 'P@ssw0rd'},
            {'title': 'Secret Girlfriends List', 'id': 2, 'content': 'Fletcher\nMonica Geller\nRachel Green\nLily Aldrin', 'locked': False},
            {'title': 'Grocery List', 'id': 3, 'content': 'Eggplant\nTomatoes\nCarrots\nGarlic Bread', 'locked': False},
            {'title': 'Secret Boyfriends List', 'id': 4, 'content': 'Christian Bale\nBrad Pitt\nRyan Gosling\nRyan Reynolds\nXu Song\nEugene Fitzherbert\nMatt LeBlanc Young', 'locked': False},
        ]

        for note in notes:
            new_note = Note(**note)
            db.session.add(new_note)

        db.session.commit()
        print("Notes initialized.")


def init_admin_todo_account():
    # Check if the admin account is already created
    admin_user = TodoUser.query.filter_by(username='admin').first()
    if not admin_user:
        # Create the admin account
        admin_user = TodoUser(username='admin', password='P@ssw0rd')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin TodoUser initialized.")

        # Now, create todo items for admin
        todos = [
            {'task': 'change password to notes app to: Flag{S3cr3t_P@ssw0rd_2023}', 'done': True, 'user_id': admin_user.id},
            {'task': 'buy groceries', 'done': False, 'user_id': admin_user.id},
            {'task': 'contact gf #10', 'done': False, 'user_id': admin_user.id},
        ]

        for todo in todos:
            new_todo = Todo(**todo)
            db.session.add(new_todo)

        db.session.commit()
        print("Admin Todo items initialized.")
    else:
        print("Admin TodoUser already exists.")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        generate_users(5)
        init_admin_todo_account()
        init_notes()


