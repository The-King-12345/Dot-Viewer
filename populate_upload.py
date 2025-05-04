import sqlite3
import pdfplumber
import re
import argparse

def single_pdf_to_text(path):
    text = []
    
    with pdfplumber.open(path) as pdf:
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

def populate(db_path, txt):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    lines = txt.split('\n')

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
        elif matches := re.search(r"(\d+[A-Z]?) (\d+(?: ?\- ?(?:(?:\d+)|end))?) (\d+) (?:Side ([12]):)? ?(?:(On)|([\d\.]+) steps (inside|outside)) (\d+) yd ln (?:(On)|([\d\.]+) steps (in front of|behind)) (.+)$", line):            
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