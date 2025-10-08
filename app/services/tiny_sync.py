from app.database import SessionLocal
from app import models
from app.services.tiny_service import listar_produtos_tiny

def sincronizar_tiny_produtos():
    """
    Busca todos os produtos da Tiny e salva/atualiza no banco local.
    """
    db = SessionLocal()
    pagina = 1
    inseridos = 0
    atualizados = 0

    while True:
        data = listar_produtos_tiny(pagina)
        produtos = data.get("retorno", {}).get("produtos", [])

        if not produtos:
            break

        for p in produtos:
            info = p.get("produto", {})
            if not info.get("codigo"):
                continue

            produto = db.query(models.Product).filter_by(sku=info["codigo"]).first()

            if not produto:
                produto = models.Product(
                    sku=info.get("codigo"),
                    name=info.get("descricao"),
                    cost_price=info.get("preco_custo") or 0,
                    sale_price=info.get("preco") or 0,
                    stock=info.get("estoque_atual") or 0,
                    location="Tiny",
                )
                db.add(produto)
                inseridos += 1
            else:
                produto.sale_price = info.get("preco") or produto.sale_price
                produto.stock = info.get("estoque_atual") or produto.stock
                atualizados += 1

        db.commit()
        pagina += 1

        # Parar se a API Tiny indicar o fim das páginas
        if data.get("retorno", {}).get("status_processamento") == "3":
            break

    db.close()
    return {"inseridos": inseridos, "atualizados": atualizados}
