import sqlite3
import pdfplumber
import re
import argparse

PDF_PATH = "./static/pdf.pdf"
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
        text = extract_text_from_pdf(PDF_PATH)
        create_text_file(TEXT_PATH, text)
    if args.populate:
        populate(DATABASE_PATH, TEXT_PATH)
    if args.add:
        add_info(DATABASE_PATH)


def add_info(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("ALTER TABLE pages ADD COLUMN tempo INTEGER NOT NULL DEFAULT 168")

    print("Info added successfully")

    cursor.close()
    conn.close()
    return


def populate(db_path, txt_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(txt_path, "r") as txt_file:
        lines = txt_file.readlines()
        for line in lines:

            # populate performers
            if matches := re.search(r"Performer: Symbol: ([A-Z]) Label: (\d+)", line):
                try:
                    cursor.execute("INSERT INTO performers (name, symbol, label) VALUES(?, ?, ?)", (matches.group(1) + matches.group(2), matches.group(1), matches.group(2)))
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"ERROR at populate_performers: {e}")
            
            # populate dots and pages
            elif matches := re.search(r"^(\d+A?) (\d+\-\d+)? ?(\d+) (?:Side ([12]):)? ?(?:(On)|([\d\.]+) steps (inside|outside)) (\d+) yd ln (?:(On)|([\d\.]+) steps (in front of|behind)) (.+)$", line):            
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
                    cursor.execute(f"SELECT EXISTS (SELECT 1 FROM pages WHERE page = '{page}')")
                except sqlite3.Error as e:
                    print(f"ERROR at select_exists: {e}")

                if cursor.fetchone()[0] == False:
                    try:
                        cursor.execute("INSERT INTO pages (page, measures, counts) VALUES(?, ?, ?)", (page, measures, counts))
                        conn.commit()
                    except sqlite3.Error as e:
                        print(f"ERROR at populate_pages: {e}")
                
                # get performer_id
                try:
                    cursor.execute("SELECT id FROM performers ORDER BY id DESC LIMIT 1")
                except sqlite3.Error as e:
                    print(f"ERROR at get_performer_id: {e}")
                performer_id = cursor.fetchone()[0]

                # get page_id
                try:
                    cursor.execute(f"SELECT id FROM pages WHERE page = '{page}' LIMIT 1")
                except sqlite3.Error as e:
                    print(f"ERROR at get_page_id: {e}")
                page_id = cursor.fetchone()[0]

                # populate dots
                try:
                    cursor.execute("INSERT INTO dots (performer_id, page_id, side, yd_steps, yd, hash_steps, hash) VALUES(?, ?, ?, ?, ?, ?, ?)", (performer_id, page_id, side, yd_steps, yd, hash_steps, hash))
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"ERROR at populate_dots: {e}")

            elif matches := re.search(r"^Page .+", line):
                pass
            elif matches := re.search(r"^Set Measure .+", line):
                pass
            else:
                print("No match: ", line)

    
    print("Data inserted successfully")

    cursor.close()
    conn.close()
    return


def extract_text_from_pdf(path):
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


def create_text_file(path, text):
    with open(path, "w") as file:
        file.write(text)
        
    print("TEXT file created successfully.")
    return 


def create_tables(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE performers")
    cursor.execute("DROP TABLE pages")
    cursor.execute("DROP TABLE dots")
    print("Tables cleared successfully.")

    cursor.execute('''
        CREATE TABLE performers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            symbol TEXT NOT NULL,
            label INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page TEXT UNIQUE NOT NULL,
            measures TEXT,
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

    print("Tables created successfully.")

    conn.commit()
    cursor.close()
    conn.close()
    return


if __name__ == "__main__":
    main()