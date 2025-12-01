#!/usr/bin/env python3
"""
GLEH Database Initialization Script
Initializes database schema and creates initial admin user
"""
import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app import app, db
from src.models import User
from werkzeug.security import generate_password_hash


def init_database():
    """Initialize database schema and create admin user"""

    print("=" * 60)
    print("GLEH Database Initialization")
    print("=" * 60)

    with app.app_context():
        # Create all tables
        print("\n[1/3] Creating database tables...")
        db.create_all()
        print("✓ Database tables created")

        # Check if admin user already exists
        print("\n[2/3] Checking for admin user...")
        admin = User.query.filter_by(username='admin').first()

        if admin:
            print("✓ Admin user already exists")
        else:
            print("Creating admin user...")
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created")
            print(f"  Username: admin")
            print(f"  Password: admin123")
            print(f"  IMPORTANT: Change this password after first login!")

        # Verify database
        print("\n[3/3] Verifying database...")
        user_count = User.query.count()
        print(f"✓ Database verified - {user_count} user(s) in database")

        print("\n" + "=" * 60)
        print("Database initialization complete!")
        print("=" * 60)
        print("\nYou can now access GLEH at http://localhost")
        print("Login with: admin / admin123")
        print("")


if __name__ == '__main__':
    init_database()
