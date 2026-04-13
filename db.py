import sqlite3

conn = sqlite3.connect("health.db")
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age REAL,
    gender TEXT,
    bp REAL,
    cholesterol REAL,
    glucose REAL,
    smoking INTEGER,
    alcohol INTEGER,
    exercise INTEGER,
    bmi REAL,
    family INTEGER,
    result TEXT
)
''')

conn.commit()
conn.close()

print("✅ Database created successfully!")