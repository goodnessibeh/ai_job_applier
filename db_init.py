#!/usr/bin/env python3
"""
Database initialization script for Heroku.
Run this with: heroku run python db_init.py
"""
import sys
from sqlalchemy import inspect
from app import create_app, db
from app.models import User

def init_db():
    print("Starting database initialization...")
    app = create_app()
    
    with app.app_context():
        # Check if tables exist
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'user' not in existing_tables:
            print("Creating database tables...")
            try:
                db.create_all()
                print("Tables created successfully.")
                
                # Create admin user
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True
                )
                admin_user.set_password('Mascerrano@Cyber2025--')
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created successfully.")
                return True
            except Exception as e:
                print(f"Error creating tables: {str(e)}")
                return False
        else:
            print("Tables already exist, checking for admin user...")
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                try:
                    admin_user = User(
                        username='admin',
                        email='admin@example.com',
                        is_admin=True
                    )
                    admin_user.set_password('Mascerrano@Cyber2025--')
                    db.session.add(admin_user)
                    db.session.commit()
                    print("Admin user created in existing database.")
                except Exception as e:
                    print(f"Error creating admin user: {str(e)}")
                    return False
            else:
                print("Admin user already exists.")
            
            return True

if __name__ == "__main__":
    success = init_db()
    if success:
        print("Database initialization completed successfully.")
        sys.exit(0)
    else:
        print("Database initialization failed.")
        sys.exit(1)