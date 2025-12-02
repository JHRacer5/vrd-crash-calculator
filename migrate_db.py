import sqlite3
import os

DB_PATH = 'instance/crash_reports.db'

def migrate_database():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. It will be created when the app starts.")
        return

    print(f"Migrating database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if chassis column exists
        cursor.execute("PRAGMA table_info(report)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'chassis' not in columns:
            print("Adding 'chassis' column to 'report' table...")
            cursor.execute("ALTER TABLE report ADD COLUMN chassis TEXT")
            conn.commit()
            print("✅ Successfully added 'chassis' column.")
        else:
            print("ℹ️ 'chassis' column already exists.")
            
    except Exception as e:
        print(f"❌ Error migrating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
