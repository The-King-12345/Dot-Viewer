import sqlite3
from pypdf import PdfReader
import re
import argparse
from populate_upload import create_tables, populate, add_timestamps, add_holds

def main():
    parser = argparse.ArgumentParser(description="Populate a database using information from a pdf")
    parser.add_argument("year", help="Input which year to edit")
    parser.add_argument("-c", "--create", action="store_true", help="Create blank tables in the database (clears existing tables)")
    parser.add_argument("-t", "--text", action="store_true", help="Extract text from pdf and store it in a text file")
    parser.add_argument("-p", "--populate", action="store_true", help="Populate the database using the text file")
    parser.add_argument("-a", "--add", action="store_true", help="Add additional information to the database")

    args = parser.parse_args()
    
    if args.year == "2024":
        db_path = "./static/PoP/24database.db"
        txt_path = "./static/PoP/24text.txt"
        mvts = ["./static/PoP/24mvt1.pdf", "./static/PoP/24mvt2.pdf","./static/PoP/24mvt3.pdf"]

    elif args.year == "2023":
        db_path = "./static/PoP/23database.db"
        txt_path = "./static/PoP/23text.txt"
        mvts = ["./static/PoP/23mvt1.pdf", "./static/PoP/23mvt2.pdf","./static/PoP/23mvt3.pdf"]

    elif args.year == "2022":
        db_path = "./static/PoP/22database.db"
        txt_path = "./static/PoP/22text.txt"
        mvts = ["./static/PoP/22mvt1.pdf", "./static/PoP/22mvt2.pdf","./static/PoP/22mvt3.pdf","./static/PoP/22mvt4.pdf"]

    elif args.year == "2021":
        db_path = "./static/PoP/21database.db"
        txt_path = "./static/PoP/21text.txt"
        mvts = ["./static/PoP/21mvt1.pdf", "./static/PoP/21mvt2.pdf","./static/PoP/21mvt3.pdf"]

    else:
        print("Please enter a valid year")
        return

    if args.create:
            create_tables(db_path)
    if args.text:
        create_text_file(mvts, txt_path)
    if args.populate:
        prepare_populate(db_path, txt_path)
    if args.add:
        match args.year:
            case "2024":
                add_info24(db_path)
            case "2023":
                add_info23(db_path)
            case "2022":
                add_info22(db_path)
            case "2021":
                add_info21(db_path)

    return

def add_info24(db_path):
    startDelay = 0.65
    # tempos [bpm, mvt, start_set]
    tempos = [[160,1,1],
              [107,2,24],
              [132,2,28],
              [160,3,38]]
    # delays {set: delay}
    delays = {23:60/107*7,
              37:60/160*4}
    # holds [instruction, vars]
    holds = [["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) AND performer_id IN (SELECT id FROM performers WHERE symbol IN (?))", (12,12,"2","s")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,4,"8")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,3,"9")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) AND performer_id IN (SELECT id FROM performers WHERE symbol IN (?,?))", (0,8,"12","s","X")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) AND performer_id IN (SELECT id FROM performers WHERE performer IN (?,?,?,?,?,?,?))", (0,6,"14","Sousaphone ","Baritone ","Trombone ","Tenor Saxophone ","Bari Saxophone ", "Bass Clarinet ", "Tenor Drum ")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) AND performer_id IN (SELECT id FROM performers WHERE symbol IN (?,?))", (0,8,"39","s","X")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) AND performer_id IN (SELECT id FROM performers WHERE symbol IN (?,?))", (0,8,"41","s","X")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) AND performer_id IN (SELECT id FROM performers WHERE performer IN (?,?,?,?,?,?))", (2,2,"44","Flute ","Clarinet ","Alto Saxophone ","Tenor Saxophone ","Bari Saxophone ", "Bass Clarinet ")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) AND performer_id IN (SELECT id FROM performers WHERE symbol IN (?))", (0,4,"52","s")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) AND performer_id IN (SELECT id FROM performers WHERE symbol IN (?))", (0,4,"53","s")]
             ]
    
    add_timestamps(db_path, startDelay, tempos, delays)
    add_holds(db_path, holds)

    print("Timestamps and holds added successfully.")
    return

def add_info23(db_path):
    startDelay = 0.3
    # tempos [bpm, mvt, start_set]
    tempos = [[168,1,1],
              [132,2,31],
              [126,2,38],
              [112.81,2,39],
              [106,2,40],
              [160,3,41],
              [165.6,3,42],
              [168,3,43],
              [151.75,3,61],
              [142,3,62]]
    # delays {set: delay}
    delays = {30:60/132*5.5}
    # holds [instruction, vars]
    holds = [["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) AND performer_id NOT IN (SELECT id FROM performers WHERE label IN (?))", (20,0,"4","G1")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,6,"12")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,12,"13")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,3,"18")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,8,"20")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,8,"22")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,4,"25")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?)", (0,4,"26")],
             ["UPDATE dots SET start = ?, stop = ? WHERE page_id = (SELECT id FROM pages WHERE page = ?) AND performer_id IN (SELECT id FROM performers WHERE label IN (?))", (18,0,"30","G8")]]

    add_timestamps(db_path, startDelay, tempos, delays)
    add_holds(db_path, holds)

    print("Timestamps and holds added successfully.")
    return

def add_info22(db_path):
    startDelay = 0
    # tempos [bpm, mvt, start_set]
    tempos = [[152,1,1],
              [164,2,15],
              [132,3,51],
              [168,3,64]]
    # delays {set: delay}
    delays = {50: 60/164*16}
    # holds [instruction, vars]
    holds = []

    add_timestamps(db_path, startDelay, tempos, delays)
    add_holds(db_path, holds)

    print("Timestamps and holds added successfully.")
    return

def add_info21(db_path):
    startDelay = 2.2
    # tempos [bpm, mvt, start_set]
    tempos = [[152,1,1],
              [130,2,20],
              [146,2,21],
              [159,2,29],
              [172,2,30],
              [162,3,36]]
    # delays {set: delay}
    delays = {}
    # holds [instruction, vars]
    holds = []

    add_timestamps(db_path, startDelay, tempos, delays)
    add_holds(db_path, holds)

    print("Timestamps and holds added successfully.")
    return
    
def prepare_populate(db_path, txt_path):
    with open(txt_path, "r") as txt_file:
        txt = txt_file.read()

        populate(db_path, txt)

    print("Data inserted successfully")
    
def extract_text_from_pdf(pdf_path):
    text = ""
    
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text()

    return text

def create_text_file(mvts, txt_path):
    text = ""

    for pdf_path in mvts:
        text += extract_text_from_pdf(pdf_path)

    with open(txt_path, "w") as file:
        file.write(text)
        
    print("TEXT file created successfully.")
    return 

if __name__ == "__main__":
    main()