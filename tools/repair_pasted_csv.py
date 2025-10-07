import csv
import sys
import re

in_path = sys.argv[1] if len(sys.argv) > 1 else 'seed_data.csv'
out_path = sys.argv[2] if len(sys.argv) > 2 else 'seed_data_fixed.csv'

def normalize_number_token(tok):
    # remove spaces
    t = tok.replace(' ', '')
    # turn comma decimal into dot
    if ',' in t and '.' not in t:
        t = t.replace(',', '.')
    else:
        t = t.replace(',', '')
    return t

fixed = []
with open(in_path, encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        if not s:
            continue
        # skip header lines that are already CSV-like
        if s.lower().startswith('produto') and ('codigo' in s.lower() or 'codigo' in s.lower()):
            continue
        parts = [p.strip() for p in s.split(',') if p.strip()]
        if len(parts) < 4:
            continue
        sku = parts[1] if len(parts) > 1 else ''
        name = parts[0]
        qty = parts[2] if len(parts) > 2 else ''
        # valor may be split into multiple tokens; join tokens from index 3 until we find something that looks like percent or classification
        valor_tokens = parts[3:]
        # remove trailing tokens that look like percentages or classification (letters)
        while valor_tokens and (re.match(r'^[%\d,\.]+$', valor_tokens[-1]) == False or len(valor_tokens[-1]) < 1):
            # break only if last token looks like percent/class; otherwise keep
            break
        # attempt to find the token that contains at least one digit and a comma or dot
        joined = ''
        for i in range(len(valor_tokens)):
            candidate = ','.join(valor_tokens[:i+1])
            candidate_clean = normalize_number_token(candidate)
            # consider valid if contains a dot and digits
            if re.search(r'\d', candidate_clean) and '.' in candidate_clean:
                joined = candidate_clean
                break
        if not joined:
            # fallback: join all and normalize
            joined = normalize_number_token(','.join(valor_tokens))

        qty_norm = qty.replace('.', '').replace(',', '')
        fixed.append((sku, name, qty_norm, joined))

with open(out_path, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['sku','name','stock','total_value'])
    for sku, name, qty, valor in fixed:
        w.writerow([sku, name, qty, valor])

print('Wrote', len(fixed), 'rows to', out_path)
