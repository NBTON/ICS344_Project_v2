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

        # Emit WebSocket event
        # Import inside function to avoid circular import
        from backend.websocket_handler import socketio

        socketio.emit('new_message', {
            'message_id': msg.message_id,
            'sender_id': msg.sender_id,
            'recipient_id': msg.recipient_id,
            'timestamp': msg.timestamp.isoformat(),
            'content': plaintext
        }, room=recipient_id)

        # Send confirmation to sender
        socketio.emit('message_sent', {
             'message_id': msg.message_id,
             'recipient_id': recipient_id,
             'content': plaintext
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

            # If I am the sender, I should have stored the plaintext or encrypted it for myself too?
            # Wait, the current implementation only encrypts for the recipient!
            # If I am the sender, I cannot decrypt the message unless I encrypted the session key for myself too.
            # The plan says: "Encrypt session key with recipient's public key... Store encrypted message".
            # It does NOT mention encrypting for the sender.
            # This is a common pitfall. Usually, you encrypt for both (multi-recipient) or store plaintext locally.
            # But in a web app, "store locally" means browser storage.
            # If I fetch history from server, and I am the sender, I can't decrypt it.

            # For the purpose of this project, if I am the sender, I might just return "Encrypted Message"
            # OR I should have encrypted it for myself.
            # Given the plan's strict instructions, I followed the "Recipient" encryption.
            # Let's see if I can decrypt it.

            if is_sender:
                # I cannot decrypt it because I don't have the session key encrypted with MY public key.
                # Unless I modify send_message to add support for sender decryption.
                content = "[Encrypted message sent]"
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
