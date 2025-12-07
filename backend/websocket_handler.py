from flask import request
from flask_socketio import emit, join_room, disconnect
from backend.database import db
from backend.app import create_app
from backend.auth import auth_bp
from backend.api_routes import api_bp
from flask_socketio import SocketIO
from flask_cors import CORS

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

def register_extensions(app):
    socketio.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

@socketio.on('connect')
def handle_connect():
    # In a real app we'd verify the JWT token here
    # For now, we assume the session is handled via cookies or auth header logic
    # but socketio context is tricky with Flask session sometimes.
    # The client should join a room identified by their user_id.
    pass

@socketio.on('join')
def handle_join(data):
    user_id = data.get('user_id')
    if user_id:
        join_room(user_id)
        emit('status', {'msg': f'Joined room {user_id}'})

@socketio.on('typing')
def handle_typing(data):
    recipient_id = data.get('recipient_id')
    sender_id = data.get('sender_id')
    if recipient_id:
        emit('typing', {'sender_id': sender_id}, room=recipient_id)

@socketio.on('stop_typing')
def handle_stop_typing(data):
    recipient_id = data.get('recipient_id')
    sender_id = data.get('sender_id')
    if recipient_id:
        emit('stop_typing', {'sender_id': sender_id}, room=recipient_id)
