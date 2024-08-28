import sqlite3
import pdfplumber
import re
import argparse

MVT1_PATH = "./static/mvt1.pdf"
MVT2_PATH = "./static/mvt2.pdf"
DATABASE_PATH = "./static/database.db"
TEXT_PATH = "./static/text.txt"

def main():
    parser = argparse.ArgumentParser(description="Populate a database using information from a pdf")
    parser.add_argument("-c", "--create", action="store_true", help="Create blank tables in the database (clears existing tables)")
    parser.add_argument("-t", "--text", action="store_true", help="Extract text from pdf and store it in a text file")
    parser.add_argument("-p", "--populate", action="store_true", help="Populate the database using the text file")
    parser.add_argument("-a", "--add", action="store_true", help="Add additional information to the database")

    args = parser.parse_args()

    # Run all if no args provided
    if not any(vars(args).values()):
        args.text = True
        args.create = True
        args.populate = True
        args.add = True

    if args.create:
        create_tables(DATABASE_PATH)
    if args.text:
        text = extract_text_from_pdf(MVT1_PATH, MVT2_PATH)
        create_text_file(TEXT_PATH, text)
    if args.populate:
        populate(DATABASE_PATH, TEXT_PATH)
    if args.add:
        add_info(DATABASE_PATH)


def add_info(db_path):
    add_timestamps(db_path)
    add_holds(db_path)


def add_holds(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # add columns
    cursor.execute("PRAGMA table_info(dots);")
    columns = [row[1] for row in cursor.fetchall()]

    if "start" not in columns:
        cursor.execute("ALTER TABLE dots ADD COLUMN start INTEGER NOT NULL DEFAULT 0")
    if "stop" not in columns:
        cursor.execute("ALTER TABLE dots ADD COLUMN stop INTEGER NOT NULL DEFAULT 0")

    conn.commit()

    # MANUALLY populate holds
    cursor.execute("UPDATE dots SET start = 0, stop = 0")

    cursor.execute('''UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) 
                   AND performer_id IN (SELECT id FROM performers WHERE symbol IN (?))''', (12,12,"2","s"))

    cursor.execute("UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,4,"8"))
    cursor.execute("UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,3,"9"))

    cursor.execute('''UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) 
                   AND performer_id IN (SELECT id FROM performers WHERE symbol IN (?,?))''', (0,8,"12","s","X"))
    
    cursor.execute('''UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) 
                   AND performer_id IN (SELECT id FROM performers WHERE performer IN (?,?,?,?,?,?,?))
                   ''', (0,6,"14","Sousaphone ","Baritone ","Trombone ","Tenor Saxophone ","Bari Saxophone ", "Bass Clarinet ", "Tenor Drum "))
    
    conn.commit()
    print("Holds added successfully")
    cursor.close()
    conn.close()


def add_timestamps(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # add columns
    cursor.execute("PRAGMA table_info(pages);")
    columns = [row[1] for row in cursor.fetchall()]

    if "tempo" not in columns:
        cursor.execute("ALTER TABLE pages ADD COLUMN tempo INTEGER NOT NULL DEFAULT 0")
    if "timestamp" not in columns:
        cursor.execute("ALTER TABLE pages ADD COLUMN timestamp INTEGER NOT NULL DEFAULT 0")
    if "mvt" not in columns:
        cursor.execute("ALTER TABLE pages ADD COLUMN mvt INTEGER NOT NULL DEFAULT 0")

    conn.commit()
    cursor.execute("UPDATE pages SET tempo = 0, timestamp = 0, mvt = 0")

    # MANUALLY populate tempo and mvt
    cursor.execute("UPDATE pages SET tempo = ?, mvt = ? WHERE id >= ? AND id <= ?", (160,1,1,23))
    cursor.execute("UPDATE pages SET tempo = ?, mvt = ? WHERE id >= ? AND id <= ?", (107,2,24,27))
    cursor.execute("UPDATE pages SET tempo = ?, mvt = ? WHERE id >= ? AND id <= ?", (132,2,28,37))

    # populate timestamps
    time = 0.45

    try:
        cursor.execute("SELECT id, page, counts, tempo, mvt FROM pages")
    except sqlite3.Error as e:
        print(f"ERROR at populate_timestamp: {e}")
    rows = cursor.fetchall()

    for row in rows:
        if row[0] == 23:
            time += 60 / 107 * 15 #manual delay

        time += 60 / row[3] * row[2] # 60 / tempo * counts
        cursor.execute("UPDATE pages SET timestamp = ? WHERE id = ?", (time, row[0]))

    conn.commit()
    print("Timestamps added successfully")
    cursor.close()
    conn.close()


def populate(db_path, txt_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(txt_path, "r") as txt_file:
        lines = txt_file.readlines()

        performer_id = "ERROR"

        for line in lines:

            # populate performers
            if matches := re.search(r"Performer: (.+)? ?Symbol: ([a-zA-Z]) Label: (.+)? ?ID:(\d+) PHS .+", line):
                try:
                    if matches.group(1) == None:
                        performer = "(unnamed)"
                    else:
                        performer = matches.group(1)
                    
                    if matches.group(3) == None:
                        label = "(unlabeled)"
                    else: 
                        label = matches.group(3)

                    performer_id = matches.group(4)

                    cursor.execute("SELECT 1 FROM performers WHERE id = ?", (performer_id,))
                    exists = cursor.fetchone()

                    # If the performer doesn't exist, insert the new record
                    if not exists:
                        cursor.execute("INSERT INTO performers (id, performer, symbol, label) VALUES(?, ?, ?, ?)",(performer_id, performer, matches.group(2), label))
                        conn.commit()

                except sqlite3.Error as e:
                    print(f"ERROR at populate_performers: {e}")
            
            # populate dots and pages
            elif matches := re.search(r"(\d+[A-Z]?) (\d+(?: ?\- ?\d+)?) (\d+) (?:Side ([12]):)? ?(?:(On)|([\d\.]+) steps (inside|outside)) (\d+) yd ln (?:(On)|([\d\.]+) steps (in front of|behind)) (.+)$", line):            
                page = matches.group(1)
                measures = matches.group(2) 
                counts = int(matches.group(3))
                yd = int(matches.group(8))
                
                # set side
                if matches.group(4) == None:
                    side = 1
                else: 
                    side = int(matches.group(4))

                # set yd_steps
                if matches.group(5) != None:
                    yd_steps = 0
                else:
                    if matches.group(7) == "inside":
                        yd_steps = float(matches.group(6))
                    elif matches.group(7) == "outside":
                        yd_steps = float(matches.group(6)) * -1
                    else:
                        raise ValueError(f"ERROR setting yd_steps at {matches.group(7)}")
                
                # set hash_steps
                if matches.group(9) != None:
                    hash_steps = 0
                else:
                    if matches.group(11) == "in front of":
                        hash_steps = float(matches.group(10)) 
                    elif matches.group(11) == "behind":
                        hash_steps = float(matches.group(10)) * -1
                    else:
                        raise ValueError(f"ERROR setting hash_steps at {matches.group(11)}")
                    
                # set hash
                if matches.group(12) == "Front side line":
                    hash = 100
                elif matches.group(12) == "Front Hash (HS)":
                    hash = 66.6666
                elif matches.group(12) == "Back Hash (HS)":
                    hash = 33.3333
                elif matches.group(12) == "Back side line":
                    hash = 0
                else:
                    raise ValueError(f"ERROR setting hash at {matches.group(12)}")
                
                # populate pages
                try:
                    cursor.execute(f"SELECT EXISTS (SELECT 1 FROM pages WHERE page = ?)", (page,))
                except sqlite3.Error as e:
                    print(f"ERROR at select_exists: {e}")

                if cursor.fetchone()[0] == False:
                    try:
                        cursor.execute("INSERT INTO pages (page, measures, counts) VALUES(?, ?, ?)", (page, measures, counts))
                        conn.commit()
                    except sqlite3.Error as e:
                        print(f"ERROR at populate_pages: {e}")

                # get page_id
                try:
                    cursor.execute(f"SELECT id FROM pages WHERE page = ? LIMIT 1", (page,))
                except sqlite3.Error as e:
                    print(f"ERROR at get_page_id: {e}")
                page_id = cursor.fetchone()[0]


                # populate dots
                cursor.execute("SELECT 1 FROM dots WHERE performer_id = ? AND page_id = ?", (performer_id, page_id))
                exists = cursor.fetchone()

                # If the performer doesn't exist, insert the new record
                if not exists:
                    try:
                        cursor.execute("INSERT INTO dots (performer_id, page_id, side, yd_steps, yd, hash_steps, hash) VALUES(?, ?, ?, ?, ?, ?, ?)", (performer_id, page_id, side, yd_steps, yd, hash_steps, hash))
                        conn.commit()
                    except sqlite3.Error as e:
                        print(f"ERROR at populate_dots: {e}")

            elif matches := re.search(r"^Printed: .+", line):
                pass
            elif matches := re.search(r"^Set Measure .+", line):
                pass
            else:
                print("No match: ", line)

    
    print("Data inserted successfully")
    cursor.close()
    conn.close()


def extract_text_from_pdf(path1, path2):
    text = []
    with pdfplumber.open(path1) as pdf:
        for page in pdf.pages:
            width, height = page.width, page.height
            quarters = [
                (0, 0, width / 2, height / 2),       # Top-left
                (width / 2, 0, width, height / 2),   # Top-right
                (0, height / 2, width / 2, height),  # Bottom-left
                (width / 2, height / 2, width, height) # Bottom-right
            ]
            for quarter in quarters:
                cropped_page = page.within_bbox(quarter)
                text.append(cropped_page.extract_text())

    with pdfplumber.open(path2) as pdf:
        for page in pdf.pages:
            width, height = page.width, page.height
            quarters = [
                (0, 0, width / 2, height / 2),       # Top-left
                (width / 2, 0, width, height / 2),   # Top-right
                (0, height / 2, width / 2, height),  # Bottom-left
                (width / 2, height / 2, width, height) # Bottom-right
            ]
            for quarter in quarters:
                cropped_page = page.within_bbox(quarter)
                text.append(cropped_page.extract_text())
    return "\n".join(text)


def create_text_file(path, text):
    with open(path, "w") as file:
        file.write(text)
        
    print("TEXT file created successfully.")
    return 


def create_tables(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS performers")
    cursor.execute("DROP TABLE IF EXISTS pages")
    cursor.execute("DROP TABLE IF EXISTS dots")
    print("Tables cleared successfully.")

    cursor.execute('''
        CREATE TABLE performers (
            id INTEGER PRIMARY KEY UNIQUE NOT NULL,
            performer TEXT NOT NULL,
            symbol TEXT NOT NULL,
            label TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page TEXT UNIQUE NOT NULL,
            measures TEXT NOT NULL,
            counts INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE dots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            performer_id INTEGER NOT NULL,
            page_id INTEGER NOT NULL,   
            side INTEGER NOT NULL,
            yd_steps REAL NOT NULL,
            yd INTEGER NOT NULL,
            hash_steps REAL NOT NULL, 
            hash REAL NOT NULL,
            FOREIGN KEY (performer_id) REFERENCES performers(id),
            FOREIGN KEY (page_id) REFERENCES pages(id)
        )
    ''')

    conn.commit()
    print("Tables created successfully.")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()