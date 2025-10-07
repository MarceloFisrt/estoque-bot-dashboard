import csv
import re
from decimal import Decimal, InvalidOperation

IN = 'seed_data.csv'
OUT = 'seed_data_validated.csv'

def to_decimal(s):
    if s is None:
        return None
    s = str(s).strip()
    if s == '':
        return None
    # replace comma decimal separators and remove thousand separators
    s = s.replace('.', '').replace(',', '.') if s.count(',') and s.count('.') == 0 else s.replace(',', '')
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

def to_int(s):
    if s is None:
        return None
    s = str(s).strip()
    if s == '':
        return None
    s = re.sub(r'[^0-9-]', '', s)
    try:
        return int(s)
    except Exception:
        return None

def normalize_row(row):
    # Expected headers: sku,name,cost_price,sale_price,stock,location,margin_percent,curve
    sku = row.get('sku','').strip()
    name = row.get('name','').strip()
    cost_price = to_decimal(row.get('cost_price'))
    sale_price = to_decimal(row.get('sale_price'))
    stock = to_int(row.get('stock'))
    location = row.get('location','').strip()
    margin_percent = None
    if row.get('margin_percent'):
        mp = to_decimal(row.get('margin_percent'))
        if mp is not None:
            margin_percent = mp
    # If we have cost_price and sale_price, compute margin_percent as percent over sale_price
    if cost_price is not None and sale_price is not None and sale_price != 0:
        try:
            margin_percent = ((sale_price - cost_price) / sale_price) * 100
        except Exception:
            margin_percent = margin_percent

    # Format back to strings with normalized decimal point and 2 decimals for prices
    def fmt_dec(d):
        if d is None:
            return ''
        return f"{d:.2f}"

    out = {
        'sku': sku,
        'name': name,
        'cost_price': fmt_dec(cost_price) if cost_price is not None else '',
        'sale_price': fmt_dec(sale_price) if sale_price is not None else '',
        'stock': str(stock) if stock is not None else '',
        'location': location,
        'margin_percent': f"{margin_percent:.2f}" if margin_percent is not None else '',
        'curve': row.get('curve','').strip()
    }
    issues = []
    if sku == '':
        issues.append('missing sku')
    if name == '':
        issues.append('missing name')
    if sale_price is None:
        issues.append('invalid/missing sale_price')
    if stock is None:
        issues.append('invalid/missing stock')
    return out, issues

def main():
    with open(IN, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    seen = set()
    fixed = []
    report = {'total': len(rows), 'fixed': 0, 'duplicates': [], 'issues': []}

    for i, r in enumerate(rows, start=1):
        out, issues = normalize_row(r)
        sku = out['sku']
        if sku in seen:
            report['duplicates'].append((i, sku))
            # append suffix to make unique
            suffix = 1
            new_sku = f"{sku}-{suffix}"
            while new_sku in seen:
                suffix += 1
                new_sku = f"{sku}-{suffix}"
            out['sku'] = new_sku
        seen.add(out['sku'])
        if issues:
            report['issues'].append((i, out['sku'], issues))
        fixed.append(out)
        report['fixed'] += 1

    # write validated CSV
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['sku','name','cost_price','sale_price','stock','location','margin_percent','curve']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in fixed:
            writer.writerow(r)

    # Print short report
    print(f"Validated {report['fixed']} of {report['total']} rows. Duplicates fixed: {len(report['duplicates'])}.")
    if report['duplicates']:
        print('Duplicates (row,sku):')
        for d in report['duplicates']:
            print(d)
    if report['issues']:
        print('Rows with issues (row,sku,issues):')
        for it in report['issues']:
            print(it)
    print(f"Wrote {OUT}")

if __name__ == '__main__':
    main()
