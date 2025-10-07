import os
import time
import requests
import sqlite3
from dotenv import load_dotenv




# === Cores para o terminal ===
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"



# === Carrega variáveis do .env ===
load_dotenv()

TINY_API_TOKEN = os.getenv("TINY_API_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./teste_estoque.db").replace("sqlite:///", "")

print("Banco de dados:", DATABASE_URL)

# === Conexão com o banco ===
conn = sqlite3.connect(DATABASE_URL)
cursor = conn.cursor()

# === Cria tabela, se não existir ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE,
    name TEXT,
    cost_price REAL,
    sale_price REAL,
    stock REAL,
    curve TEXT
)
""")

# === Limpa produtos antigos (opcional) ===
print(f"{YELLOW}🧹 Limpando tabela de produtos antes da importação...{RESET}")
cursor.execute("DELETE FROM products;")
conn.commit()

print(f"\n{CYAN}🚀 Iniciando importação de produtos ATIVOS do Tiny...{RESET}\n")

page = 1
total_imported = 0
start_time = time.time()

while True:
    url = f"https://api.tiny.com.br/api2/produtos.pesquisa.php?token={TINY_API_TOKEN}&formato=json&pagina={page}&situacao=Ativo"
    response = requests.get(url)
    
    try:
        data = response.json().get("retorno", {})
    except Exception as e:
        print(f"{RED}❌ Erro ao processar resposta da API: {e}{RESET}")
        break

    produtos = data.get("produtos", [])
    if not produtos:
        print(f"{YELLOW}⚠️ Nenhum produto encontrado na página {page} (ou fim das páginas).{RESET}")
        break

    print(f"{GREEN}📦 Página {page} importada ({len(produtos)} produtos){RESET}")

    for item in produtos:
        p = item.get("produto", {})
        sku = p.get("codigo")

        if not sku:
            print(f"{YELLOW}⚠️ Produto sem SKU, ignorado.{RESET}")
            continue

        # Verifica se o SKU já existe no banco
        cursor.execute("SELECT COUNT(*) FROM products WHERE sku = ?", (sku,))
        if cursor.fetchone()[0] > 0:
            print(f"{CYAN}↪️ Produto {sku} já existe — ignorado.{RESET}")
            continue

        # Calcula o valor total (preço de venda × estoque)
        valor_total = float(p.get("preco", 0) or 0) * float(p.get("estoque_atual", 0) or 0)
    
        cursor.execute("""
        INSERT INTO products (sku, name, cost_price, sale_price, stock, valor_total, curve)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            sku,
            p.get("nome"),
            float(p.get("preco_custo", 0) or 0),
            float(p.get("preco", 0) or 0),
            float(p.get("estoque_atual", 0) or 0),
            None
        ))
        total_imported += 1

    conn.commit()
    page += 1
    time.sleep(0.5)  # evita sobrecarregar a API

end_time = time.time()
duration = end_time - start_time

print(f"\n{GREEN}✅ Importação concluída com sucesso!{RESET}")
print(f"{CYAN}📊 Total de produtos ativos importados: {total_imported}{RESET}")
print(f"{YELLOW}⏱️ Tempo total: {duration:.2f} segundos{RESET}\n")

conn.close()
