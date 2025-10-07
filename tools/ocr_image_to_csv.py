"""
OCR helper: tenta extrair uma tabela de uma imagem e salvar como CSV

Requisitos:
 - Tesseract OCR instalado no sistema (https://github.com/tesseract-ocr/tesseract)
 - biblioteca Python: pytesseract pillow pandas

Uso:
  .\venv\Scripts\python.exe tools\ocr_image_to_csv.py caminho\para\imagem.png out.csv

Notas:
 - A extração de tabelas por OCR nem sempre é perfeita. Se o PDF for escaneado com boa resolução, a saída costuma ser razoável.
 - Se não quiser instalar Tesseract, cole aqui o texto da tabela e eu converto manualmente.
"""
import sys
import os
from PIL import Image
import pytesseract
import csv
import re

def normalize_whitespace(s):
    return re.sub(r"\s+", " ", s).strip()

def image_to_text(path):
    img = Image.open(path)
    text = pytesseract.image_to_string(img, lang='por+eng')
    return text

def guess_rows_from_text(text):
    # tenta dividir por quebras de linha e limpar
    lines = [normalize_whitespace(l) for l in text.splitlines() if normalize_whitespace(l)]
    # remover linhas que parecem cabeçalhos repetidos ou notas
    return lines

def try_parse_table(lines):
    # heurística: encontrar linha que contenha cabeçalhos (codigo, quant, valor, %)
    header_idx = None
    for i, l in enumerate(lines[:6]):
        low = l.lower()
        if 'codigo' in low or 'quant' in low or '%' in low or 'valor' in low:
            header_idx = i
            break
    if header_idx is None:
        # assume as primeiras linhas são dados
        data_lines = lines
    else:
        data_lines = lines[header_idx+1:]

    rows = []
    for l in data_lines:
        # separar por múltiplos espaços ou tab
        parts = re.split(r"\s{2,}|\t|;|,", l)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 4:
            # heurística: Produto (nome pode ter espaços) + Código + Quantidade + Valor + ...
            # assumimos código é um token curto (<=8) e valores contêm dígitos e vírgula/ponto
            # procurar índice do código
            code_idx = None
            for idx, p in enumerate(parts):
                if re.match(r"^[A-Za-z0-9\-_/]+$", p) and len(p) <= 12 and re.search(r"\d", p):
                    code_idx = idx
                    break
            if code_idx is not None and code_idx+2 < len(parts):
                name = ' '.join(parts[:code_idx])
                code = parts[code_idx]
                qty = parts[code_idx+1]
                valor = parts[code_idx+2]
                rows.append((name, code, qty, valor))
        else:
            # fallback: tentar extrair números do final da linha
            m = re.search(r"(\d+[\.,]\d+)\s*$", l)
            if m:
                valor = m.group(1)
                rows.append((l.replace(valor, '').strip(), '', '', valor))
    return rows

def write_csv(rows, out_path):
    # formato compatível com app/seed.py: sku,name,cost_price,sale_price,stock,location,margin_percent,curve
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['sku','name','cost_price','sale_price','stock','location','margin_percent','curve'])
        for name, code, qty, valor in rows:
            # tentar limpar valor e quantidade
            valor_n = valor.replace('.', '').replace(',', '.') if valor else ''
            qty_n = qty.replace('.', '').replace(',', '') if qty else ''
            writer.writerow([code, name, '', valor_n, qty_n, '', '', ''])

def main():
    if len(sys.argv) < 2:
        print('Usage: ocr_image_to_csv.py input_image [out_csv]')
        return
    img = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else 'seed_data.csv'
    if not os.path.exists(img):
        print('File not found:', img)
        return
    print('Running OCR on', img)
    text = image_to_text(img)
    lines = guess_rows_from_text(text)
    rows = try_parse_table(lines)
    write_csv(rows, out)
    print(f'Wrote {len(rows)} rows to {out}')

if __name__ == '__main__':
    main()
