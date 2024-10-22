from bs4 import BeautifulSoup
import re
import logging
import datetime
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
from PIL.Image import DecompressionBombError
import sqlite3
import os
from zipfile import ZipFile 
LOG_FILENAME = 'html_extract.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

def convert_to_text(pdf):

    try:
        images = convert_from_path(pdf)
        text = ""

        for image in images:
            text += pytesseract.image_to_string(image)

        return text

    except DecompressionBombError:
        with open('ocred.log', "a") as log_file:
            log_file.write(f"{pdf} is too big!")

if __name__ == '__main__':

    df = pd.read_csv("CaseNumber.csv")
    case_numbers = df["CaseNumber"].to_list()

    con = sqlite3.connect("records.db")
    cur = con.cursor()

    res = cur.execute("SELECT CaseNumber from Records WHERE SummonsText is not null")
    processed_cases = [c[0] for c in res.fetchall()] 

    case_numbers = [c for c in case_numbers if c not in processed_cases] + ["15-2-06784-8", "16-2-10260-9", "16-2-10277-3", "16-2-10276-5", "16-2-10269-2", "16-2-10284-6"]

    print("We have", str(len(case_numbers)), "left!")

    for c in case_numbers:

        print(c)
        res = cur.execute(f"SELECT * FROM Records WHERE CaseNumber='{c}'")
        
        if res.fetchone() is None:
            con.execute(f"INSERT INTO Records (CaseNumber) VALUES (\'{c}\')")
            con.commit()

        res = cur.execute(f"SELECT SummonsText FROM Records WHERE CaseNumber='{c}'")

        try:

            with ZipFile(f"./Records/{c}.zip", mode = "r") as zip_case:

                file = zip_case.open(f"{c}.htm",'r').read()

                con.execute(f"UPDATE Records SET HasRecordDownloaded = 1 WHERE CaseNumber = \"{c}\"")
                con.commit()

                soup = BeautifulSoup( file, "html.parser" )
                tds = soup.select('td')

                for td in tds :

                    if re.search("summons", td.text, re.IGNORECASE):

                        summons = td
                        objs = list(summons.parent)
                        summons_date = datetime.datetime.strptime(objs[0].text, '%m/%d/%Y').strftime('%Y-%m-%d')
                        summons_path = objs[1].find_all("a", href=True)[0]["href"]
                        summons_path = zip_case.extract(summons_path)
                
                        summons_text = convert_to_text(summons_path)

                        summons_text = re.sub(r"\'", "\'\'", summons_text)
                        summons_text = re.sub(r"\"", "\"\"", summons_text)

                        cur.execute(f"""
                            UPDATE Records SET
                                SummonsPath = \"{summons_path}\",
                                SummonsText = \"{summons_text}\",
                                SummonsDate = \"{summons_date}\"
                            WHERE CaseNumber = \"{c}\"
                            """)
                        
                        con.commit()

                        os.remove(summons_path)

                    if re.search("complaint", td.text, re.IGNORECASE):

                        complaint = td
                        objs = list(complaint.parent)
                        complaint_date = datetime.datetime.strptime(objs[0].text, '%m/%d/%Y').strftime('%Y-%m-%d')
                        complaint_path = objs[1].find_all("a", href=True)[0]["href"]
                        complaint_path = zip_case.extract(complaint_path)
                
                        complaint_text = convert_to_text(complaint_path)
                
                        complaint_text = re.sub(r"\'", "\'\'", complaint_text)
                        complaint_text = re.sub(r"\"", "\"\"", complaint_text)

                        cur.execute(f"""
                            UPDATE Records SET
                                ComplaintPath = \"{complaint_path}\",
                                ComplaintText = \"{complaint_text}\",
                                ComplaintDate = \"{complaint_date}\"
                            WHERE CaseNumber = \"{c}\"
                            """)
                        
                        con.commit()

                        os.remove(complaint_path)

                    if re.search("return on writ", td.text, re.IGNORECASE):

                        writ = td
                        objs = list(writ.parent)
                        writ_date = datetime.datetime.strptime(objs[0].text, '%m/%d/%Y').strftime('%Y-%m-%d')
                        writ_path = objs[1].find_all("a", href=True)[0]["href"]
                        writ_path = zip_case.extract(writ_path)
                
                        writ_text = convert_to_text(writ_path)
    
                        writ_text = re.sub(r"\'", "\'\'", writ_text)
                        writ_text = re.sub(r"\"", "\"\"", writ_text)

                        cur.execute(f"""
                            UPDATE Records SET
                                WritIssued = 1,
                                WritPath = \"{writ_path}\",
                                WritText = \"{writ_text}\",
                                WritDate = \"{writ_date}\"
                            WHERE CaseNumber = \"{c}\"
                            """)
                        
                        con.commit()

                        os.remove(writ_path)

                if len(tds) > 5:
                    last_entry = tds[-5]
                    objs = list(tds[-5].parent)

                    last_entry_date = datetime.datetime.strptime(objs[0].text, '%m/%d/%Y').strftime('%Y-%m-%d')
                    last_entry_action = objs[1].text

                    cur.execute(f"""
                            UPDATE Records SET
                                LastFilingEntry = \"{last_entry_action}\",
                                LastFilingDate = \"{last_entry_date}\"
                            WHERE CaseNumber = \"{c}\"
                            """)
                    
                con.commit()


        except:

            logging.debug(c)

            con.execute(f"UPDATE Records SET HasRecordDownloaded = 0 WHERE CaseNumber = \"{c}\"")
            con.commit()

    con.close()