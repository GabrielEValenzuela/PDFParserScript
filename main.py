"""
    Copyright (C) 2022, Gabriel Valenzuela (gabriel \dot valenzuela \at mi \dot unc \dot edu \dot ar).
    All rights reserved.

    This program is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public
    License (version 2) as published by the FSF - Free Software
    Foundation.
"""


import getopt, sys
import re
import platform
import pandas as pd
from PyPDF2 import PdfFileReader
from typing import Dict, List

DATABASE:Dict[str,List[float]]  = dict()
FORMAT:str                      = r"([+-]?[0-9]*[.]?[0-9]+)\s([0-9]+)([^$]*)"
SEP:str                         = ";" if platform.system() == "Windows" else ","


def check_and_warning(no_products:List[str]):
    if(len(no_products)):
        print("WARNING: The following products are no present in the database.")
        for p in no_products:
            print(p)

def process_database(text:str,update_set:bool=False):
    no_products:List[str] = list()
    lst_text:List[str] = text.split("\n")
    for d in lst_text:
        if re.search(FORMAT,d.strip()) is not None:
            data:List[str] = d.strip().split()
            product:str = " ".join(data[2:]).replace(",",".") #Prevent the error on the csv
            if update_set:
                try:
                    DATABASE[product][0] = float(data[1])
                except KeyError:
                    no_products.append(product)
            else:
                DATABASE[product] = [float(data[1])]
    check_and_warning(no_products)

def write_pdf():
    df = pd.DataFrame.from_dict(DATABASE,orient="index")
    df.columns=["PRECIO"]
    df.to_csv("NewDatabase.csv",sep=SEP)

def process_pdfs(input_file:str,update_file:str):
    print(f"Processing the origintal file: {input_file}")
    with open(input_file, 'rb') as original_pdf:
        PDF_read = PdfFileReader(original_pdf)
        for n in range(PDF_read.getNumPages()):
            process_database(PDF_read.getPage(n).extract_text())
    print(f"Processing the update file: {update_file}")
    with open(update_file, 'rb') as update_pdf:
        PDF_read = PdfFileReader(update_pdf)
        for n in range(PDF_read.getNumPages()):
            process_database(PDF_read.getPage(n).extract_text(),update_set=True)
    print("Dumping database in new PDF")
    write_pdf()
    print("\n=== DONE ===\n")

def main():
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "o:u:h", ["original=","help", "update="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        sys.exit(2)
    original_file:str   = ""
    update_file:str     = ""
    for o,arg in opts:
        if o in ("-o","--original"):
            original_file = arg
        elif o in ("-u","--update"):
            update_file   = arg
        elif o in ("-h","--help"):
            print("Run this program providing -o orinal.pdf -u update.pdf")
        else:
            assert False, "Unhandle exception"
    if original_file and update_file:
        process_pdfs(original_file,update_file)
    
if __name__=="__main__":
    main()