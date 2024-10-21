import pytesseract
from pdf2image import convert_from_path
from PIL.Image import DecompressionBombError
import re
import multiprocessing
import glob
import os
import pandas as pd

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def pdf_to_text_ocr(case_number_list):

    for case_number in case_number_list:

        print("working on " + case_number)

        pdf_paths = glob.glob("./Records/" + case_number + "/*.pdf")

        for pdf_path in pdf_paths:

            text_file_path = re.sub("pdf", "txt", pdf_path)

            if not os.path.isfile(text_file_path):
                try:
                    images = convert_from_path(pdf_path)
                    text = ""

                    for image in images:
                        text += pytesseract.image_to_string(image)

                    with open(text_file_path, "w") as text_file:
                        text_file.write(text)
                
                except DecompressionBombError:
                    with open('ocred.log', "a") as log_file:
                        log_file.write(f"{pdf_path} is too big!")

if __name__ == '__main__':
    
    df = pd.read_csv("CaseNumber.csv")
    cases = df["CaseNumber"].to_list()

    cases = [case for case in cases if len(glob.glob("./Records/" + case + "/*.txt")) == 0]

    log = open("html_extract.log", "r")
    # Regex pattern for the exact string
    pattern = r"\d{2}-\d-\d{5}-\d"

    # Use re.findall to find all matches
    cases = re.findall(pattern, log.read())

    N = 8

    cases = split(cases, N)

    processes = []

    for c in cases:
        processes.append(multiprocessing.Process(target=pdf_to_text_ocr, args=(c, )))

    for p in processes:
        p.start()

    for p in processes:
        p.join()

   