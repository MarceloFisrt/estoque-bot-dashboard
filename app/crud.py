from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from decimal import Decimal
from typing import List, Dict, Any


def _to_float(v):
    if v is None:
        return 0.0
    if isinstance(v, Decimal):
        return float(v)
    try:
        return float(v)
    except Exception:
        return 0.0


# 1) Produtos por curva (retorna lista compatível com ProductBase)
def get_produtos_por_curva(db: Session, tipo: str) -> List[Dict[str, Any]]:
    tipo = (tipo or "").upper()
    prods = db.query(models.Product).filter(models.Product.curve == tipo).all()
    out = []
    for p in prods:
        sale = _to_float(p.sale_price)
        cost = _to_float(p.cost_price)
        margem_percent = round(((sale - cost) / sale * 100) if sale != 0 else 0.0, 2)
        out.append({
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "cost_price": round(cost, 2),
            "sale_price": round(sale, 2),
            "stock": int(p.stock or 0),
            "margem_percent": margem_percent,
            "curve": p.curve
        })
    return out


# 2) Curva ABC (retorna lista de objetos com campos do CurvaABCItem e atualiza products.curve no DB)
def get_curva_abc(db: Session) -> List[Dict[str, Any]]:
    produtos = db.query(models.Product).all()

    # monta lista intermediária com valores numéricos
    items = []
    for p in produtos:
        sale = _to_float(p.sale_price)
        stock = int(p.stock or 0)
        valor_total = round(sale * stock, 4)
        items.append({
            "id": p.id,
            "sku": p.sku,
            "name": p.name,
            "stock": stock,
            "sale_price": sale,
            "valor_total": valor_total
        })

    # ordena por valor_total desc
    items.sort(key=lambda x: x["valor_total"], reverse=True)

    soma = sum(x["valor_total"] for x in items)
    acumulado = 0.0
    out = []

    for it in items:
        acumulado += it["valor_total"]
        perc_acum = (acumulado / soma * 100) if soma > 0 else 0.0
        # determinar curva
        if perc_acum <= 80:
            curva = "A"
        elif perc_acum <= 95:
            curva = "B"
        else:
            curva = "C"

        # atualizar no banco
        prod = db.query(models.Product).filter(models.Product.id == it["id"]).first()
        if prod:
            prod.curve = curva

        out.append({
            "id": it["id"],
            "sku": it["sku"],
            "name": it["name"],
            "stock": it["stock"],
            "sale_price": round(it["sale_price"], 2),
            "valor_total": round(it["valor_total"], 2),
            "perc_acumulado": round(perc_acum, 6),
            "curva": curva
        })

    # commit das atualizações de curva
    try:
        db.commit()
    except Exception:
        db.rollback()

    return out


# 3) Lucro por curva (margem média e lucro total) -> compatível com LucroPorCurva
def get_lucro_por_curva(db: Session) -> List[Dict[str, Any]]:
    curvas = ["A", "B", "C"]
    resultados = []

    for curva in curvas:
        produtos = db.query(models.Product).filter(models.Product.curve == curva).all()
        if not produtos:
            # opcional: incluir curva com zeros, ou pular (mantive pular)
            continue

        lucro_total = 0.0
        margem_total = 0.0
        count = 0

        for p in produtos:
            sale = _to_float(p.sale_price)
            cost = _to_float(p.cost_price)
            stock = int(p.stock or 0)

            # ignorar sem preços válidos
            if sale == 0 or cost == 0:
                continue

            lucro = (sale - cost) * stock
            margem = ((sale - cost) / sale * 100) if sale != 0 else 0.0
            lucro_total += lucro
            margem_total += margem
            count += 1

        margem_media = (margem_total / count) if count > 0 else 0.0
        resultados.append({
            "curve": curva,
            "margem_media": round(margem_media, 2),
            "lucro_total": round(lucro_total, 2)
        })

    return resultados


# 4) Percentual de lucro por curva (compatível com PercentualLucro)
def get_percentual_lucro_curva(db: Session) -> List[Dict[str, Any]]:
    lucros = get_lucro_por_curva(db)
    total = sum((float(x["lucro_total"]) if x.get("lucro_total") is not None else 0.0) for x in lucros)
    out = []
    for x in lucros:
        lucro_curva = float(x["lucro_total"] or 0.0)
        perc_total = (lucro_curva / total * 100) if total != 0 else 0.0
        out.append({
            "curve": x["curve"],
            "lucro_curva": round(lucro_curva, 2),
            "perc_total": round(perc_total, 2)
        })
    return out


# + Função extra: detectar duplicados exatos por sku e por name
def get_duplicates(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    res = {}

    sku_dupes = (
        db.query(models.Product.sku, func.count(models.Product.sku))
        .group_by(models.Product.sku)
        .having(func.count(models.Product.sku) > 1)
        .all()
    )
    if sku_dupes:
        res["sku"] = [{"sku": s, "qtd": int(c)} for s, c in sku_dupes]

    name_dupes = (
        db.query(models.Product.name, func.count(models.Product.name))
        .group_by(models.Product.name)
        .having(func.count(models.Product.name) > 1)
        .all()
    )
    if name_dupes:
        res["name"] = [{"name": n, "qtd": int(c)} for n, c in name_dupes]

    return res
