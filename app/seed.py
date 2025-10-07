import csv
from decimal import Decimal, InvalidOperation
from .database import SessionLocal
from .models import Product

CSV_PATH = "seed_data.csv"


def to_decimal(v):
    if v is None or v == "":
        return None
    try:
        # normalizar vírgula -> ponto e remover pontos de milhar
        s = str(v).strip()
        s = s.replace('.', '').replace(',', '.') if s.count(',') == 1 and s.count('.') >= 1 else s.replace(',', '.')
        return Decimal(s)
    except (InvalidOperation, AttributeError):
        return None


def to_int(v):
    try:
        s = str(v).strip()
        s = s.replace('.', '').replace(',', '')
        return int(float(s))
    except (ValueError, TypeError):
        return None


def find_column_mapping(fieldnames):
    # mapeia colunas comuns para nomes internos
    lower = [f.lower() for f in fieldnames]
    mapping = {}
    for i, f in enumerate(fieldnames):
        lf = f.lower()
        if lf in ('sku', 'codigo', 'code'):
            mapping['sku'] = f
        if 'name' in lf or 'produto' in lf:
            mapping.setdefault('name', f)
        if 'quant' in lf or 'qtd' in lf:
            mapping['quantity'] = f
        if 'valor' in lf or 'value' in lf or 'total' in lf:
            mapping['total_value'] = f
        if 'price' in lf and 'sale' in lf or lf == 'preco' or lf == 'sale_price':
            mapping['sale_price'] = f
        if 'stock' in lf:
            mapping['stock'] = f
    return mapping


def run():
    db = SessionLocal()
    try:
        # tentamos o CSV padrão primeiro
        processed = 0
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                mapping = find_column_mapping(reader.fieldnames)
                count = 0
                skipped = 0
                for row in reader:
                    # Alguns leitores podem devolver list se o arquivo estiver muito quebrado; garantir dict
                    if not isinstance(row, dict):
                        continue
                    sku = (row.get(mapping.get('sku')) or row.get('sku') or row.get('Codigo') or row.get('CÓDIGO') or '').strip()
                    if not sku:
                        skipped += 1
                        continue

                    name = row.get(mapping.get('name')) or row.get('name') or ''

                    qty_raw = row.get(mapping.get('quantity')) or row.get('Quantidade') or row.get('quantidade') or ''
                    total_raw = row.get(mapping.get('total_value')) or row.get('Valor') or row.get('valor') or ''
                    sale_raw = row.get(mapping.get('sale_price')) or row.get('sale_price') or ''

                    qty = to_int(qty_raw) if qty_raw else None
                    total = to_decimal(total_raw) if total_raw else None
                    sale_price = to_decimal(sale_raw) if sale_raw else None

                    if (sale_price is None or sale_price == 0) and qty and total:
                        try:
                            sale_price = (total / Decimal(qty)).quantize(Decimal('0.01'))
                        except Exception:
                            sale_price = None

                    stock = qty if qty is not None else (to_int(row.get('stock')) or 0)

                    cost_price = to_decimal(row.get('cost_price') or row.get('cost') or '')
                    location = row.get('location') or ''
                    margin_percent = to_decimal(row.get('margin_percent') or '')
                    curve = (row.get('curve') or '').strip()[:1]

                    existing = db.query(Product).filter(Product.sku == sku).first()
                    if existing:
                        existing.name = name
                        existing.cost_price = cost_price
                        existing.sale_price = sale_price
                        existing.stock = stock
                        existing.location = location
                        existing.margin_percent = margin_percent
                        existing.curve = curve
                    else:
                        p = Product(
                            sku=sku,
                            name=name,
                            cost_price=cost_price,
                            sale_price=sale_price,
                            stock=stock,
                            location=location,
                            margin_percent=margin_percent,
                            curve=curve
                        )
                        db.add(p)
                    count += 1
                db.commit()
                processed = count

        # Se nada foi processado pelo CSV, tentamos um parser tolerante (split por tabs ou por múltiplos espaços)
        if processed == 0:
            import re
            lines = []
            with open(CSV_PATH, encoding='utf-8') as f:
                for l in f:
                    s = l.strip()
                    if s:
                        lines.append(s)
            if not lines:
                print('Arquivo vazio')
                return
            # detectar header
            header = lines[0]
            header_tokens = re.split(r'\t+|\s{2,}', header)
            hdr = [t.strip().lower() for t in header_tokens]
            # encontrar índices
            try:
                idx_codigo = next(i for i,t in enumerate(hdr) if 'codigo' in t or 'code' in t or 'sku' in t)
            except StopIteration:
                idx_codigo = 1 if len(hdr)>1 else 0
            try:
                idx_quant = next(i for i,t in enumerate(hdr) if 'quant' in t or 'qtd' in t)
            except StopIteration:
                idx_quant = 2 if len(hdr)>2 else 2
            try:
                idx_valor = next(i for i,t in enumerate(hdr) if 'valor' in t or 'value' in t or 'total' in t)
            except StopIteration:
                idx_valor = 3 if len(hdr)>3 else 3

            count2 = 0
            for l in lines[1:]:
                parts = re.split(r'\t+|\s{2,}', l)
                parts = [p.strip() for p in parts if p.strip()]
                if len(parts) <= max(idx_codigo, idx_quant, idx_valor):
                    # tentar pular
                    continue
                sku = parts[idx_codigo]
                name = parts[0]
                qty_raw = parts[idx_quant]
                total_raw = parts[idx_valor]
                qty = to_int(qty_raw)
                total = to_decimal(total_raw)
                sale_price = None
                if qty and total:
                    try:
                        sale_price = (total / Decimal(qty)).quantize(Decimal('0.01'))
                    except Exception:
                        sale_price = None
                stock = qty or 0
                existing = db.query(Product).filter(Product.sku == sku).first()
                if existing:
                    existing.name = name
                    existing.sale_price = sale_price
                    existing.stock = stock
                else:
                    db.add(Product(sku=sku, name=name, sale_price=sale_price, stock=stock))
                count2 += 1
            db.commit()
            print(f"Seed (fallback) concluído: {count2} linhas processadas.")
            return
        print(f"Seed concluído: {count} linhas processadas. {skipped} linhas puladas.")
    except FileNotFoundError:
        print(f"Arquivo {CSV_PATH} não encontrado. Crie um CSV com colunas. Ex.: Codigo,Produto,Quantidade,Valor")
    finally:
        db.close()


if __name__ == '__main__':
    run()
