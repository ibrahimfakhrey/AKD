import os
import bcrypt
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()
with app.app_context():
    email = 'admin@akd.app'
    password = 'admin123'
    user = User.query.filter_by(email=email).first()
    if user:
        print(f"User found: {user.email}")
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password_hash = pw_hash
        db.session.commit()
        print(f"Password updated for {user.email}")
    else:
        print("User not found")
