import os
import bcrypt
from app import create_app
from app.models.user import User

app = create_app()
with app.app_context():
    email = 'admin@akd.app'
    password = 'admin123'
    user = User.query.filter_by(email=email).first()
    if user:
        print(f"User found: {user.email}")
        print(f"Password Hash: {user.password_hash}")
        try:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
            print(f"Password Valid (admin123): {is_valid}")
        except Exception as e:
            print(f"Error checking password: {e}")
    else:
        print("User not found")
