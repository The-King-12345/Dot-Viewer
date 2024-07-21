import sqlite3
import pdfplumber
import re

def main():
    text = extract_text_from_pdf("pdf.pdf")
    populate(text)

def populate(text):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    lines = text.split('\n')
    current_symbol = "MISSING"
    for line in lines:
        if matches := re.search(r"^(\d+A?) (?:\d+\-\d+)? ?(\d+) Side ([12]): (?:(On)|([\d\.]+) steps (inside|outside)) (\d+) yd ln (?:(On)|([\d\.]+) steps (in front of|behind)) (.+)$", line):            
            sets = matches.group(1)
            counts = int(matches.group(2))
            side = int(matches.group(3))
            yd = int(matches.group(7))

            if matches.group(4) != None:
                yd_steps = 0
            else:
                if matches.group(6) == "inside":
                    yd_steps = float(matches.group(5))
                elif matches.group(6) == "outside":
                    yd_steps = float(matches.group(5)) * -1
                else:
                    raise ValueError(f"ERROR setting yd_steps at {matches.group(6)}")
                
            if matches.group(8) != None:
                hash_steps = 0
            else:
                if matches.group(10) == "in front of":
                    hash_steps = float(matches.group(9)) 
                elif matches.group(10) == "behind":
                    hash_steps = float(matches.group(9)) * -1
                else:
                    raise ValueError(f"ERROR setting hash_steps at {matches.group(10)}")
                
            if matches.group(11) == "Front side line":
                hash = 100
            elif matches.group(11) == "Front Hash (HS)":
                hash = 66.6666
            elif matches.group(11) == "Back Hash (HS)":
                hash = 33.3333
            elif matches.group(11) == "Back side line":
                hash = 0
            else:
                raise ValueError(f"ERROR setting hash at {matches.group(11)}")

            try:
                cursor.execute("INSERT INTO performers (symbol, sets, counts, side, yd_steps, yd, hash_steps, hash) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (current_symbol, sets, counts, side, yd_steps, yd, hash_steps, hash))
                conn.commit()
            except sqlite3.Error as e:
                print(f"ERROR: {e}")


        elif matches := re.search(r"Performer: Symbol: ([A-Z]) Label: (\d+)", line):
            current_symbol = matches.group(1) + matches.group(2)
    
    print("Data inserted successfully")
    conn.close()




def extract_text_from_pdf(pdf_path):
    text = []
    with pdfplumber.open(pdf_path) as pdf:
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



if __name__ == "__main__":
    main()