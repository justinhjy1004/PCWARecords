import pandas as pd
from bs4 import BeautifulSoup
import pytesseract
from pdf2image import convert_from_path
from PIL.Image import DecompressionBombError
from zipfile import ZipFile 
import re
import os
import sqlite3
import multiprocessing

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

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def pdf_to_text_ocr(case_number_list):

    for c in case_number_list:

        try:
            with ZipFile(f"./Records/{c}.zip", mode = "r") as zip_case:

                file = zip_case.open(f"{c}.htm",'r').read()

                soup = BeautifulSoup( file, "html.parser" )
                tds = soup.select('td')

                tds = soup.select('td')

                for td in tds :
                    
                    if re.search("summons", td.text, re.IGNORECASE):

                        summons = td
                        objs = list(summons.parent)

                        summons_path = objs[1].find_all("a", href=True)[0]["href"]
                        summons_path = zip_case.extract(summons_path)
                        
                        summons_text = convert_to_text(summons_path)

                        with open(f"./Records/{c}_summons.txt", "w") as summons_file:
                            summons_file.write(summons_text)

                        os.remove(summons_path)

                    if re.search("complaint", td.text, re.IGNORECASE):

                        complaint = td
                        objs = list(complaint.parent)

                        complaint_path = objs[1].find_all("a", href=True)[0]["href"]
                        complaint_path = zip_case.extract(complaint_path)
                        
                        complaint_text = convert_to_text(complaint_path)

                        with open(f"./Records/{c}_complaint.txt", "w") as complaint_file:
                            complaint_file.write(complaint_text)

                        os.remove(complaint_path)

                    if re.search("return on writ", td.text, re.IGNORECASE):

                        writ = td
                        objs = list(writ.parent)

                        writ_path = objs[1].find_all("a", href=True)[0]["href"]
                        writ_path = zip_case.extract(writ_path)
                        
                        writ_text = convert_to_text(writ_path)

                        with open(f"./Records/{c}_writ.txt", "w") as writ_file:
                            writ_file.write(writ_text)
                        
                        os.remove(writ_path)
        except:
            print(f"Error in {c}!")

if __name__ == '__main__':
    
    df = pd.read_csv("CaseNumber.csv")
    cases = df["CaseNumber"].to_list()

    processed_cases = [file[:12] for file in os.listdir("./Records") if file.endswith("writ.txt")]
    processed_cases = list(set(processed_cases))

    cases = [c for c in cases if c not in processed_cases] 

    N = 8

    cases = split(cases, N)

    processes = []

    for c in cases:
        processes.append(multiprocessing.Process(target=pdf_to_text_ocr, args=(c, )))

    for p in processes:
        p.start()

    for p in processes:
        p.join()

   