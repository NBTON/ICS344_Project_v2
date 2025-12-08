from flask import Blueprint, request, jsonify, session
from backend.database import db, Messages, Users
from backend.message_handler import MessageHandler
from backend.auth import login_required
from sqlalchemy import or_

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/users', methods=['GET'])
@login_required
def get_users():
    users = Users.query.with_entities(Users.user_id, Users.username).all()
    return jsonify([{'user_id': u.user_id, 'username': u.username} for u in users])

@api_bp.route('/api/users/<user_id>/key', methods=['GET'])
@login_required
def get_user_key(user_id):
    user = Users.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    import hashlib
    fingerprint = hashlib.sha256(user.public_key.encode('utf-8')).hexdigest()

    return jsonify({
        'user_id': user.user_id,
        'public_key': user.public_key,
        'fingerprint': fingerprint
    })

@api_bp.route('/api/messages/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    plaintext = data.get('content')

    if not recipient_id or not plaintext:
        return jsonify({'error': 'Recipient and content required'}), 400

    sender_id = session['user_id']
    private_key_pem = session.get('private_key')

    if not private_key_pem:
        return jsonify({'error': 'Session error: Private key not found'}), 401

    try:
        msg = MessageHandler.send_message(sender_id, private_key_pem, recipient_id, plaintext)

        # Emit WebSocket event - SECURITY FIX: Don't send plaintext, only notification
        # Import inside function to avoid circular import
        from backend.websocket_handler import socketio

        # Notify recipient that a new message is available (no plaintext)
        socketio.emit('new_message', {
            'message_id': msg.message_id,
            'sender_id': msg.sender_id,
            'recipient_id': msg.recipient_id,
            'timestamp': msg.timestamp.isoformat()
        }, room=recipient_id)

        # Send confirmation to sender (include plaintext for immediate display only)
        socketio.emit('message_sent', {
             'message_id': msg.message_id,
             'recipient_id': recipient_id,
             'content': plaintext,  # OK to send to sender (they already know it)
             'timestamp': msg.timestamp.isoformat()
        }, room=sender_id)

        return jsonify({'message': 'Message sent successfully', 'message_id': msg.message_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/api/messages/<partner_id>', methods=['GET'])
@login_required
def get_messages(partner_id):
    user_id = session['user_id']
    private_key_pem = session.get('private_key')

    if not private_key_pem:
        return jsonify({'error': 'Session error: Private key not found'}), 401

    # Get conversation history
    messages = Messages.query.filter(
        or_(
            (Messages.sender_id == user_id) & (Messages.recipient_id == partner_id),
            (Messages.sender_id == partner_id) & (Messages.recipient_id == user_id)
        )
    ).order_by(Messages.timestamp).all()

    results = []
    for msg in messages:
        try:
            is_sender = (msg.sender_id == user_id)
            content = ""

            if is_sender:
                # Use sender's encrypted session key to decrypt
                try:
                    content = MessageHandler.decrypt_message_as_sender(private_key_pem, msg)
                except ValueError:
                    # Fallback for old messages without sender_encrypted_session_key
                    content = "[Encrypted message - sent before update]"
            else:
                content = MessageHandler.decrypt_message(private_key_pem, msg)

            results.append({
                'message_id': msg.message_id,
                'sender_id': msg.sender_id,
                'recipient_id': msg.recipient_id,
                'timestamp': msg.timestamp.isoformat(),
                'content': content,
                'is_sender': is_sender
            })
        except Exception as e:
            results.append({
                'message_id': msg.message_id,
                'error': 'Decryption failed',
                'details': str(e)
            })

    return jsonify(results)
