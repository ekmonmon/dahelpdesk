import sqlite3

conn = sqlite3.connect("helpdesk.db")
cursor = conn.cursor()

# Function to check if a column exists
def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

# Add submission_time column if it doesn't exist
if not column_exists(cursor, "tickets", "submission_time"):
    cursor.execute("ALTER TABLE tickets ADD COLUMN submission_time TEXT")
    conn.commit()
    print("✅ Column 'submission_time' added successfully.")
else:
    print("⚠️ Column 'submission_time' already exists.")

# Add updated_at column if it doesn't exist
if not column_exists(cursor, "tickets", "updated_at"):
    cursor.execute("ALTER TABLE tickets ADD COLUMN updated_at TEXT")
    conn.commit()
    print("✅ Column 'updated_at' added successfully.")
else:
    print("⚠️ Column 'updated_at' already exists.")

conn.close()
