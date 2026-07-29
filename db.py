import sqlite3

conn = sqlite3.connect("pizza.db")
cursor = conn.cursor()

# Admin Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL1
)
""")

# Review Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS review(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    image TEXT NOT NULL,
    rating INTEGER NOT NULL,
    review TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Tables Created Successfully")

def create_about_stats_table(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS about_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            years_experience TEXT NOT NULL,
            happy_customers TEXT NOT NULL,
            pizza_recipes TEXT NOT NULL,
            fast_delivery TEXT NOT NULL
        )
    ''')
    conn.commit()