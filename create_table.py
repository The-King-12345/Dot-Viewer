import sqlite3

def main():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    print("Connected to database successfully")

    cursor.execute("DROP TABLE performers")
    print("Cleared existing table successfully")

    cursor.execute('''
    CREATE TABLE performers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL, 
        sets TEXT NOT NULL,
        counts INTEGER NOT NULL,          
        side INTEGER NOT NULL,
        yd_steps REAL NOT NULL,
        yd INTEGER NOT NULL,
        hash_steps REAL NOT NULL, 
        hash REAL NOT NULL
    )
    ''')
    print("Created table successfully")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()