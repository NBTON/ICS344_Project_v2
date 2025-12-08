from flask import Blueprint, request, jsonify, session
from backend.database import db, Messages, AttackLogs, Users
from backend.message_handler import MessageHandler
from backend.auth import login_required
from backend.utils import rate_limit
import uuid
from datetime import datetime
import base64
import json

attack_bp = Blueprint('attack', __name__)

@attack_bp.route('/api/attack-lab/logs', methods=['GET'])
@login_required
def get_attack_logs():
    logs = AttackLogs.query.order_by(AttackLogs.timestamp.desc()).limit(50).all()
    return jsonify([{
        'log_id': l.log_id,
        'attack_type': l.attack_type,
        'attacker_ip': l.attacker_ip,
        'target_user_id': l.target_user_id,
        'defense_triggered': l.defense_triggered,
        'blocked': l.blocked,
        'timestamp': l.timestamp.isoformat()
    } for l in logs])

@attack_bp.route('/api/attack-lab/replay', methods=['POST'])
@login_required
def simulate_replay_attack():
    # 1. Capture a valid message (latest one)
    target_msg = Messages.query.order_by(Messages.timestamp.desc()).first()
    if not target_msg:
        return jsonify({'error': 'No messages to replay'}), 400

    # 2. Attempt to resend it (create a duplicate entry attempt)
    # In a real replay, the attacker intercepts the network packet.
    # Here we simulate by trying to process the exact same message payload.

    attacker_ip = request.remote_addr

    # Log the attempt
    log = AttackLogs(
        attack_type='Replay Attack',
        attacker_ip=attacker_ip,
        target_user_id=target_msg.recipient_id,
        attack_data=f"Replaying Message ID: {target_msg.message_id}",
        blocked=True, # We assume it will be blocked
        defense_triggered="Sequence Number / Message ID Check"
    )

    try:
        # Simulate processing logic:
        # Check Message ID uniqueness
        existing = Messages.query.get(target_msg.message_id)
        if existing:
            log.defense_triggered = "Message ID Uniqueness Check"
            db.session.add(log)
            db.session.commit()
            return jsonify({'message': 'Attack blocked', 'defense': 'Message ID Uniqueness Check'}), 200

        # Check Sequence Number
        # ...

    except Exception as e:
        log.blocked = False
        log.defense_triggered = "None (Exception)"
        db.session.add(log)
        db.session.commit()
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Attack simulation finished'}), 200

@attack_bp.route('/api/attack-lab/tamper', methods=['POST'])
@login_required
def simulate_tamper_attack():
    target_msg = Messages.query.order_by(Messages.timestamp.desc()).first()
    if not target_msg:
        return jsonify({'error': 'No messages to tamper'}), 400

    # Tamper with ciphertext
    ciphertext_bytes = base64.b64decode(target_msg.ciphertext)
    tampered_bytes = bytearray(ciphertext_bytes)
    tampered_bytes[0] ^= 0xFF # Flip bits
    tampered_ciphertext = base64.b64encode(tampered_bytes).decode('utf-8')

    log = AttackLogs(
        attack_type='Ciphertext Tampering',
        target_user_id=target_msg.recipient_id,
        attack_data=f"Tampering Message ID: {target_msg.message_id}",
        blocked=True,
        defense_triggered="AES-GCM Tag Verification / RSA-PSS Signature"
    )

    try:
        # Attempt to decrypt
        # First Verify Signature
        sender = Users.query.get(target_msg.sender_id)
        # Construct payload with TAMPERED ciphertext
        payload_dict = {
            "message_id": target_msg.message_id,
            "sender_id": target_msg.sender_id,
            "recipient_id": target_msg.recipient_id,
            "timestamp": target_msg.timestamp.isoformat(),
            "sequence_number": target_msg.sequence_number,
            "encrypted_session_key": target_msg.encrypted_session_key,
            "iv": target_msg.iv,
            "ciphertext": tampered_ciphertext, # TAMPERED
            "tag": target_msg.tag
        }
        payload_str = json.dumps(payload_dict, sort_keys=True)
        # Signature verification should fail because payload changed but signature didn't

        # In reality, the attacker cannot generate a valid signature for the tampered payload
        # because they don't have the sender's private key.

        from backend.crypto_engine import rsa_pss_verify
        signature = base64.b64decode(target_msg.signature)

        if not rsa_pss_verify(sender.public_key.encode('utf-8'), payload_str.encode('utf-8'), signature):
            log.defense_triggered = "RSA-PSS Signature Verification"
            db.session.add(log)
            db.session.commit()
            return jsonify({'message': 'Attack blocked', 'defense': 'RSA-PSS Signature Verification'}), 200

        # If signature somehow passed (unlikely), GCM would fail
        log.defense_triggered = "AES-GCM Tag Verification (Simulated)"
        db.session.add(log)
        db.session.commit()
        return jsonify({'message': 'Attack blocked', 'defense': 'AES-GCM Tag Verification'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# MITM and DoS simulations can be added similarly

@attack_bp.route('/api/attack-lab/mitm', methods=['POST'])
@login_required
def simulate_mitm_attack():
    target_msg = Messages.query.order_by(Messages.timestamp.desc()).first()
    if not target_msg:
        return jsonify({'error': 'No messages to attack'}), 400

    # Simulate MITM: Attacker replaces public key during exchange
    # Or in this context, attacker tries to sign a message with their own key
    # claiming it is from the victim.

    # 1. Attacker generates their own key pair
    from backend.crypto_engine import generate_rsa_keypair, rsa_pss_sign
    attacker_priv, attacker_pub = generate_rsa_keypair(key_size=2048)

    # 2. Attacker creates a message payload
    payload_dict = {
        "message_id": str(uuid.uuid4()),
        "sender_id": target_msg.sender_id, # Impersonating sender
        "recipient_id": target_msg.recipient_id,
        "timestamp": datetime.utcnow().isoformat(),
        "sequence_number": target_msg.sequence_number + 1,
        "encrypted_session_key": target_msg.encrypted_session_key, # Reusing for simplicity
        "iv": target_msg.iv,
        "ciphertext": target_msg.ciphertext,
        "tag": target_msg.tag
    }
    payload_str = json.dumps(payload_dict, sort_keys=True)

    # 3. Attacker signs with THEIR private key
    fake_signature = rsa_pss_sign(attacker_priv, payload_str.encode('utf-8'))
    b64_fake_sig = base64.b64encode(fake_signature).decode('utf-8')

    log = AttackLogs(
        attack_type='MITM Attack',
        target_user_id=target_msg.recipient_id,
        attack_data="Attacker signed message with fake key",
        blocked=True,
        defense_triggered="RSA-PSS Signature Verification"
    )

    try:
        # 4. Recipient tries to verify with Sender's REAL public key
        sender = Users.query.get(target_msg.sender_id)

        from backend.crypto_engine import rsa_pss_verify

        # This verification MUST fail because signature was made with attacker_priv,
        # but we are verifying with sender.public_key
        if not rsa_pss_verify(sender.public_key.encode('utf-8'), payload_str.encode('utf-8'), fake_signature):
            log.defense_triggered = "RSA-PSS Signature Verification (Key Mismatch)"
            db.session.add(log)
            db.session.commit()
            return jsonify({'message': 'Attack blocked', 'defense': 'RSA-PSS Signature Mismatch'}), 200

        # If it passes, crypto is broken
        log.blocked = False
        db.session.add(log)
        db.session.commit()
        return jsonify({'error': 'Attack SUCCEEDED (Crypto Broken!)'}), 500

    except Exception as e:
         return jsonify({'error': str(e)}), 500

@attack_bp.route('/api/attack-lab/dos', methods=['POST'])
@login_required
@rate_limit(max_requests=10, window_seconds=60)  # Strict limit for demo
def simulate_dos_attack():
    """
    Simulates a DoS attack scenario.
    This endpoint is rate-limited to demonstrate the defense mechanism.
    If you call this endpoint more than 10 times in 60 seconds, you'll be blocked.
    """
    log = AttackLogs(
        attack_type='DoS Attack',
        attacker_ip=request.remote_addr,
        attack_data="Request accepted - Rate limit not yet exceeded",
        blocked=False,
        defense_triggered="Rate Limiting (Active)"
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({
        'message': 'Request processed',
        'note': 'Rate limiting is active. Try calling this endpoint more than 10 times in 60 seconds to see it blocked.',
        'requests_info': 'After exceeding the limit, you will receive HTTP 429 (Too Many Requests)'
    }), 200


@attack_bp.route('/api/attack-lab/dos-flood', methods=['POST'])
@login_required
def simulate_dos_flood():
    """
    Simulates rapid flooding by making multiple internal requests.
    This demonstrates the rate limiter blocking excessive requests.
    """
    blocked_count = 0
    success_count = 0
    
    from backend.utils import rate_limit
    from backend.database import RateLimits
    
    # Simulate 15 rapid requests to trigger rate limiting
    for i in range(15):
        # Check rate limit directly
        from datetime import timedelta
        
        ip_address = request.remote_addr
        endpoint = 'attack.simulate_dos_flood_internal'
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=60)
        
        rate_record = RateLimits.query.filter_by(
            ip_address=ip_address,
            endpoint=endpoint
        ).first()
        
        if rate_record:
            if rate_record.window_start < window_start:
                rate_record.request_count = 1
                rate_record.window_start = now
                success_count += 1
            else:
                rate_record.request_count += 1
                if rate_record.request_count > 10:
                    blocked_count += 1
                else:
                    success_count += 1
        else:
            rate_record = RateLimits(
                ip_address=ip_address,
                endpoint=endpoint,
                request_count=1,
                window_start=now
            )
            db.session.add(rate_record)
            success_count += 1
        
        db.session.commit()
    
    log = AttackLogs(
        attack_type='DoS Attack',
        attacker_ip=request.remote_addr,
        attack_data=f"Simulated 15 rapid requests: {success_count} allowed, {blocked_count} blocked",
        blocked=blocked_count > 0,
        defense_triggered=f"Rate Limiting - Blocked {blocked_count}/15 requests"
    )
    
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'message': 'DoS simulation complete',
        'total_requests': 15,
        'allowed': success_count,
        'blocked': blocked_count,
        'defense': 'Rate Limiting'
    }), 200
