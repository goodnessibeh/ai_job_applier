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
        # Get current columns in user table
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Migration 1: Add display_name column if it doesn't exist
        if 'display_name' not in column_names:
            print("Migration 1: Adding display_name column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN display_name TEXT")
            
            # Update existing users to set display_name to username as default
            cursor.execute("UPDATE user SET display_name = username")
            
            conn.commit()
            print("Migration 1 completed successfully.")
        else:
            print("Migration 1: display_name column already exists. Skipping.")
        
        # Migration 2: Add profile picture columns to user table
        columns_to_add = [
            ('profile_picture', 'TEXT'),
            ('profile_picture_type', 'TEXT'),
            ('profile_picture_updated_at', 'DATETIME')
        ]
        
        for column, data_type in columns_to_add:
            if column not in column_names:
                print(f"Migration 2: Adding {column} column to user table...")
                cursor.execute(f"ALTER TABLE user ADD COLUMN {column} {data_type}")
                conn.commit()
                print(f"Migration 2: Added {column} column successfully.")
            else:
                print(f"Migration 2: {column} column already exists. Skipping.")
        
        # Migration 3: Add job preferences columns to user table
        job_preference_columns = [
            ('job_titles', 'TEXT'),
            ('min_salary', 'INTEGER'),
            ('max_commute_distance', 'INTEGER'),
            ('preferred_locations', 'TEXT'),
            ('remote_only', 'BOOLEAN DEFAULT 0'),
            ('auto_apply_enabled', 'BOOLEAN DEFAULT 0'),
            ('minimum_match_score', 'INTEGER DEFAULT 70')
        ]
        
        for column, data_type in job_preference_columns:
            if column not in column_names:
                print(f"Migration 3: Adding {column} column to user table...")
                cursor.execute(f"ALTER TABLE user ADD COLUMN {column} {data_type}")
                conn.commit()
                print(f"Migration 3: Added {column} column successfully.")
            else:
                print(f"Migration 3: {column} column already exists. Skipping.")
        
        # Migration 4: Add match-score columns to application_history table
        cursor.execute("PRAGMA table_info(application_history)")
        app_columns = cursor.fetchall()
        app_column_names = [column[1] for column in app_columns]
        
        match_score_columns = [
            ('match_score', 'INTEGER'),
            ('match_reasons', 'TEXT'),
            ('auto_applied', 'BOOLEAN DEFAULT 0')
        ]
        
        for column, data_type in match_score_columns:
            if column not in app_column_names:
                print(f"Migration 4: Adding {column} column to application_history table...")
                cursor.execute(f"ALTER TABLE application_history ADD COLUMN {column} {data_type}")
                conn.commit()
                print(f"Migration 4: Added {column} column successfully.")
            else:
                print(f"Migration 4: {column} column already exists. Skipping.")
        
        # Migration 5: Update user_settings table for RapidAPI
        cursor.execute("PRAGMA table_info(user_settings)")
        settings_columns = cursor.fetchall()
        settings_column_names = [column[1] for column in settings_columns]
        
        # Add RapidAPI key column
        if 'rapidapi_key' not in settings_column_names:
            print("Migration 5: Adding rapidapi_key column to user_settings table...")
            cursor.execute("ALTER TABLE user_settings ADD COLUMN rapidapi_key TEXT")
            conn.commit()
            print("Migration 5: Added rapidapi_key column successfully.")
        else:
            print("Migration 5: rapidapi_key column already exists. Skipping.")
        
        # Add new job API preference columns
        new_job_api_columns = [
            ('use_upwork', 'BOOLEAN DEFAULT 1'),
            ('use_google_jobs', 'BOOLEAN DEFAULT 1'),
            ('use_workday', 'BOOLEAN DEFAULT 1'),
            ('use_startup_jobs', 'BOOLEAN DEFAULT 1'),
            ('use_job_search', 'BOOLEAN DEFAULT 1'),
            ('use_internships', 'BOOLEAN DEFAULT 1'),
            ('use_active_jobs', 'BOOLEAN DEFAULT 1')
        ]
        
        for column, data_type in new_job_api_columns:
            if column not in settings_column_names:
                print(f"Migration 5: Adding {column} column to user_settings table...")
                cursor.execute(f"ALTER TABLE user_settings ADD COLUMN {column} {data_type}")
                conn.commit()
                print(f"Migration 5: Added {column} column successfully.")
            else:
                print(f"Migration 5: {column} column already exists. Skipping.")
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'profile_pictures')
        os.makedirs(uploads_dir, exist_ok=True)
        
        print("All migrations completed successfully.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {str(e)}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    run_migrations()