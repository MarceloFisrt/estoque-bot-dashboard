"""
seed_mock.py
Gera dados de teste e popula o banco SQLite usado pelo projeto (teste_estoque.db).
Uso:
    python seed_mock.py          # gera 200 produtos por padrão
    python seed_mock.py 50       # gera 50 produtos
    python seed_mock.py 500 --dupes  # gera 500 produtos e adiciona duplicados intencionais
"""

import random
import sys
import argparse
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

def create_args():
    p = argparse.ArgumentParser(description="Seed mock data into teste_estoque.db")
    p.add_argument("n", nargs="?", type=int, default=200, help="Número de produtos a gerar (padrão 200)")
    p.add_argument("--dupes", action="store_true", help="Adicionar duplicados intencionais (2 entradas)")
    return p.parse_args()

def generate_name(i):
    bases = ["Sensor","Modulo","Cabo","Fonte","Placa","Resistor","Capacitor","Transistor","Conector","Display","Motor","Bateria","Rele","Arduino","ESP32","LED","Módulo"]
    desc = ["Mini","Pro","Plus","V2","Kit","Pack","Alta Temp","Standard","OEM","Gen2","SMD","TH"]
    return f"{random.choice(bases)} {random.choice(desc)} {i:04d}"

def main():
    args = create_args()
    n = args.n if args.n > 0 else 200

    # cria tabelas se não existirem
    models.Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # opcional: apagar produtos existentes antes de inserir novos
    # ATENÇÃO: descomente se quiser reset completo
    # db.query(models.Product).delete()
    # db.commit()

    produtos = []
    for i in range(1, n+1):
        cost = round(random.uniform(0.5, 200.0), 2)
        sale = round(cost * random.uniform(1.1, 3.5), 2)
        stock = random.randint(0, 2000)
        sku = f"MOCK-{i:06d}"
        name = generate_name(i)
        p = models.Product(
            sku=sku,
            name=name,
            cost_price=Decimal(str(cost)),
            sale_price=Decimal(str(sale)),
            stock=stock,
            location=f"A{random.randint(1,50):02d}-{random.randint(1,20):02d}",
            margin_percent=round(((sale - cost) / sale * 100) if sale else 0, 2),
            curve=None
        )
        produtos.append(p)

    db.add_all(produtos)
    db.commit()

    if args.dupes and n >= 2:
        # cria 2 duplicados intencionais para testar /duplicates
        first = db.query(models.Product).order_by(models.Prdouct.id).first()
        if first:
            d1 = models.Product(sku=first.sku, name=first.name + " DUP", cost_price=first.cost_price, sale_price=first.sale_price, stock=first.stock, location=first.location)
            db.add(d1)
        second = db.query(models.Product).order_by(models.Product.id).offset(1).first()
        if second:
            d2 = models.Product(sku=second.sku + "-ALT", name=second.name, cost_price=second.cost_price, sale_price=second.sale_price, stock=second.stock, location=second.location)
            db.add(d2)
        db.commit()

    total = db.query(models.Product).count()
    print(f"✅ Inseridos: {n} produtos. Total no DB agora: {total}")
    if args.dupes:
        print("✅ Duplicados adicionados (2 itens).")

    db.close()

if __name__ == '__main__':
    main()
