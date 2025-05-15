import os
import sys
import sqlite3

def run_migrations():
    """Run database migrations"""
    # Get the database path from environment variable or use default
    database_path = os.environ.get('DATABASE_URL', None)
    if database_path and database_path.startswith('sqlite:///'):
        database_path = database_path.replace('sqlite:///', '')
    else:
        # Default path
        instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance')
        database_path = os.path.join(instance_path, 'ai_job_applier.sqlite')
    
    if not os.path.exists(database_path):
        print(f"Database file not found at {database_path}")
        sys.exit(1)
    
    print(f"Running migrations on database: {database_path}")
    
    # Connect to the database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    try:
        # Check if display_name column exists in the user table
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Add display_name column if it doesn't exist
        if 'display_name' not in column_names:
            print("Adding display_name column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN display_name TEXT")
            
            # Update existing users to set display_name to username as default
            cursor.execute("UPDATE user SET display_name = username")
            
            conn.commit()
            print("Migration completed successfully.")
        else:
            print("display_name column already exists. No migration needed.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {str(e)}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    run_migrations()