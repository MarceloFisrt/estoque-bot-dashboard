import csv
import sys
path = sys.argv[1] if len(sys.argv)>1 else 'seed_data.csv'
with open(path, encoding='utf-8') as f:
    r = csv.reader(f)
    for i,row in enumerate(r):
        print(i, row)
        if i>40:
            break
