from flask import Blueprint, request, jsonify, session
from backend.database import db, Users
from backend.key_manager import KeyManager
import bcrypt
import jwt
from datetime import datetime, timedelta
import functools
from backend.config import Config

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if Users.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400

    # Hash password for storage
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Generate and encrypt keys
    public_key, encrypted_private_key = KeyManager.generate_user_keys(password)

    # Calculate fingerprint (SHA256 of public key)
    import hashlib
    fingerprint = hashlib.sha256(public_key.encode('utf-8')).hexdigest()

    new_user = Users(
        username=username,
        password_hash=password_hash,
        public_key=public_key,
        encrypted_private_key=encrypted_private_key
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully',
        'user_id': new_user.user_id,
        'fingerprint': fingerprint
    }), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = Users.query.filter_by(username=username).first()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Attempt to decrypt private key to verify it works (and load into session)
    private_key_pem = KeyManager.decrypt_private_key(password, user.encrypted_private_key)
    if not private_key_pem:
         return jsonify({'error': 'Failed to decrypt private key. Password mismatch or corruption.'}), 500

    # Create session
    session['user_id'] = user.user_id
    session['username'] = user.username
    # Store private key in session (In a real production app, this should be handled more carefully,
    # e.g., kept in memory only, or client-side only. Per plan, we load it into session).
    session['private_key'] = private_key_pem.decode('utf-8')

    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Login successful', 'user_id': user.user_id}), 200

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/api/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({
        'user_id': session['user_id'],
        'username': session['username']
    }), 200
