import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('retail_eye.db')
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(shelf_snapshots);")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'product_breakdown' not in columns:
            print("Adding product_breakdown column to shelf_snapshots...")
            cursor.execute("ALTER TABLE shelf_snapshots ADD COLUMN product_breakdown JSON;")
            conn.commit()
            print("✅ Migration successful")
        else:
            print("✅ Column product_breakdown already exists")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    migrate()
