import pytesseract
from pdf2image import convert_from_path
import re
import concurrent.futures
import glob
import os

def pdf_to_text_ocr(pdf_paths):

    for pdf_path in pdf_paths:

        images = convert_from_path(pdf_path)
        text = ""
        
        for image in images:
            text += pytesseract.image_to_string(image)

        text_file_path = re.sub("pdf", "txt", pdf_path)

        with open(text_file_path, "w") as text_file:
            text_file.write(text)

if __name__ == '__main__':

    cases = os.listdir("./Records/")

    paths = [glob.glob("./Records/" + case + "/*.pdf") for case in cases]

    executor = concurrent.futures.ProcessPoolExecutor(16)
    futures = [executor.submit(pdf_to_text_ocr, p) for p in paths]
    concurrent.futures.wait(futures)