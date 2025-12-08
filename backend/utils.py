import os
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Derives a 32-byte key from a password using PBKDF2-HMAC-SHA256.

    Args:
        password (str): The user's password.
        salt (bytes): The salt used for derivation. If None, a new salt is generated.

    Returns:
        tuple: (derived_key, salt)
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )

    key = kdf.derive(password.encode())
    return key, salt


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """
    Rate limiting decorator that uses the RateLimits database table.
    
    Args:
        max_requests (int): Maximum number of requests allowed in the time window.
        window_seconds (int): Time window in seconds.
    
    Returns:
        Decorator function that enforces rate limiting.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from backend.database import db, RateLimits
            
            ip_address = request.remote_addr
            endpoint = request.endpoint
            
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=window_seconds)
            
            # Find or create rate limit record
            rate_record = RateLimits.query.filter_by(
                ip_address=ip_address,
                endpoint=endpoint
            ).first()
            
            if rate_record:
                # Check if the window has expired
                if rate_record.window_start < window_start:
                    # Reset the window
                    rate_record.request_count = 1
                    rate_record.window_start = now
                else:
                    # Increment counter
                    rate_record.request_count += 1
                    
                    # Check if limit exceeded
                    if rate_record.request_count > max_requests:
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'message': f'Maximum {max_requests} requests per {window_seconds} seconds allowed',
                            'retry_after': window_seconds
                        }), 429
            else:
                # Create new rate limit record
                rate_record = RateLimits(
                    ip_address=ip_address,
                    endpoint=endpoint,
                    request_count=1,
                    window_start=now
                )
                db.session.add(rate_record)
            
            db.session.commit()
            return f(*args, **kwargs)
        return decorated_function
    return decorator

