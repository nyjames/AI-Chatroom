# app.py (imports)
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from collections import defaultdict
from openai import OpenAI
import os
from dotenv import load_dotenv

# implementing .env variables
load_dotenv()

# implementing openAI API for chatbot

openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)


# starting flask app

app = Flask(__name__)

# implementing user list to show current users in room

room_users = defaultdict(set)

app.config['SECRET_KEY'] = os.urandom(24)

# implementing DB

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_app.db'  # Path to your SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking for performance
db = SQLAlchemy(app)

# Implementing Socketio to communicate
socketio = SocketIO(app)

# implementing Flask Login Manager

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


# Message Model 

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.username}: {self.message}>'

# user class

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# OpenAI implementation

def get_bot_response_from_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )

        bot_reply = response.choices[0].message.content.strip()
        return bot_reply
    
    # error (prints error on console)

    except Exception as e:
        print(f"Error communicating with OpenAI API: {e}")
        return "Sorry, I couldn't process that request."
    
# registration

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "User already exists"

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('chat'))  # redirect after registration

    return render_template('register.html')

# login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"

    return render_template('login.html')

# logout

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# homepage / login

@app.route('/')

def home():
    return render_template("index.html")

# chat room function

@app.route('/chat')
@login_required
def chat():
    username = current_user.username
    room = request.args.get('room') or 'general'
    limit = int(request.args.get('limit', 20))

    # order messages by showing most recent on bottom

    messages = Message.query.filter_by(room=room).order_by(Message.timestamp.desc()).limit(limit).all()
    messages = messages[::-1]
    return render_template('chat.html', username=username, room=room, messages=messages, limit=limit)

@socketio.on('join_room')

def handle_join_room_event(data):
    username = data['username']
    room = data['room']
    room_users[room].add(username)

    join_room(room)
    # announces when user joins room
    socketio.emit('join_room_announcement', data, room=room)

    # updates list of current users in room
    socketio.emit('update_user_list', list(room_users[room]), room=room)

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info(f"{data['username']} sent: {data['message']} in {data['room']}")

    # Save user's message to database
    new_message = Message(
        username=data['username'],
        room=data['room'],
        message=data['message']
    )
    db.session.add(new_message)
    db.session.commit()

    # Broadcast the user's message
    socketio.emit('receive_message', data, room=data['room'])

    # Check if the message calls the bot
    if data['message'].strip().lower().startswith('@bot'):
        user_prompt = data['message'].split('@bot', 1)[1].strip()

        # Call OpenAI API to get bot's response
        bot_reply = get_bot_response_from_openai(user_prompt)

        # Emit bot's response to the room
        socketio.emit('receive_message', {
            'username': 'ChatBot 🤖',
            'room': data['room'],
            'message': bot_reply
        }, room=data['room'])

# user is leaving room

@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))

    username = data['username']
    room = data['room']
    room_users[room].discard(username)

    leave_room(room)

    # announce user is leaving room

    socketio.emit('leave_room_announcement', data, room=room)
    socketio.emit('update_user_list', list(room_users[room]), room=room)

# load users

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
