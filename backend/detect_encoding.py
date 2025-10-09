# backend/detect_encoding.py
import pandas as pd

path = "../data/openphish_norm.csv"
encodings = ['utf-8-sig','utf-8','utf-16','utf-16-le','utf-16-be','cp1252','latin1','iso-8859-1']

for e in encodings:
    try:
        pd.read_csv(path, encoding=e, nrows=5)
        print("OK encoding:", e)
        break
    except Exception as ex:
        print("failed", e, type(ex).__name__, str(ex)[:120])
