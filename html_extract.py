from bs4 import BeautifulSoup
import re
import logging
import datetime
import pandas as pd
import sqlite3
LOG_FILENAME = 'html_extract.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)


if __name__ == '__main__':

    df = pd.read_csv("CaseNumber.csv")
    case_numbers = df["CaseNumber"].to_list()

    con = sqlite3.connect("records.db")
    cur = con.cursor()

    for c in case_numbers:

        print(c)
        con.execute(f"""INSERT INTO Records (CaseNumber) VALUES (\'{c}\')""")
        con.commit()

        try:

            file = open(f"./Records/{c}/{c}.htm",'r')

            con.execute(f"UPDATE Records SET HasRecordDownloaded = 1 WHERE CaseNumber = \"{c}\"")
            con.commit()

            soup = BeautifulSoup( file, "html.parser")
            tds = soup.select('td')

            for td in tds :

                if re.search("summons", td.text, re.IGNORECASE):

                    summons = td
                    objs = list(summons.parent)
                    summons_date = datetime.datetime.strptime(objs[0].text, '%m/%d/%Y').strftime('%Y-%m-%d')
                    summons_path = objs[1].find_all("a", href=True)[0]["href"]
                    text_path = re.sub("pdf", "txt", summons_path)
            
                    summons_file = open(f"./Records/{c}/{text_path}",'r')
                    summons_text = summons_file.read()

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

                if re.search("complaint", td.text, re.IGNORECASE):

                    complaint = td
                    objs = list(complaint.parent)
                    complaint_date = datetime.datetime.strptime(objs[0].text, '%m/%d/%Y').strftime('%Y-%m-%d')
                    complaint_path = objs[1].find_all("a", href=True)[0]["href"]
                    text_path = re.sub("pdf", "txt", complaint_path)
            
                    complaint_file = open(f"./Records/{c}/{text_path}",'r')
                    complaint_text = complaint_file.read()

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

                if re.search("return on writ", td.text, re.IGNORECASE):

                    writ = td
                    objs = list(writ.parent)
                    writ_date = datetime.datetime.strptime(objs[0].text, '%m/%d/%Y').strftime('%Y-%m-%d')
                    writ_path = objs[1].find_all("a", href=True)[0]["href"]
                    text_path = re.sub("pdf", "txt", writ_path)
        
                    writ_file = open(f"./Records/{c}/{text_path}",'r')
                    writ_text = writ_file.read()

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


        except OSError:
            logging.debug(c)
            con.execute(f"UPDATE Records SET HasRecordDownloaded = 0 WHERE CaseNumber = \"{c}\"")
            con.commit()

    con.close()