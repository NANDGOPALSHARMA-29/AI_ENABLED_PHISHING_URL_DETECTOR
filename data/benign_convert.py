# benign_convert.py
import pandas as pd, io, sys
encodings = ['utf-8-sig','utf-8','utf-16','utf-16-le','utf-16-be','cp1252','latin1','iso-8859-1']
infile = 'benign_raw.csv'
outfile = 'benign_norm.csv'
ok = False
for e in encodings:
    try:
        df = pd.read_csv(infile, encoding=e, dtype=str, low_memory=False)
        print('read OK with encoding:', e, 'rows:', len(df))
        ok = True
        break
    except Exception as ex:
        print('failed', e, type(ex).__name__)
if not ok:
    print('No encoding worked; file may be binary or xlsx. Exiting.')
    sys.exit(1)

# build url column
if 'domain' in df.columns:
    df2 = df[['domain']].dropna().drop_duplicates()
    df2['url'] = 'https://' + df2['domain'].str.strip()
elif 'url' in df.columns:
    df2 = df[['url']].dropna().drop_duplicates()
else:
    first = df.columns[0]
    df2 = df[[first]].dropna().drop_duplicates()
    df2 = df2.rename(columns={first:'url'})

out = df2[['url']].dropna().drop_duplicates()
out['label'] = 0
out.to_csv(outfile, index=False)
print('✅ Wrote', outfile, 'rows:', len(out))
