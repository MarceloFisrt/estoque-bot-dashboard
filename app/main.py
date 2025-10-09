from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import os
from datetime import datetime

from app import crud, schemas, models
from app.database import SessionLocal
from app.logger import get_logger
from app.services.tiny_service import fetch_tiny_vendas, listar_produtos_tiny, fetch_tiny_estoque
from app.tiny_api import tiny_api

logger = get_logger()
app = FastAPI()

# === CORS Configuration ===
origins_env = os.getenv("CORS_ORIGINS", "*")
if origins_env == "*" or origins_env == "":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Arquivos estáticos (CSS, JS, imagens) ===
static_dir = Path(__file__).parent / "dashboard" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# === Rota principal para o dashboard ===
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_file = Path(__file__).parent / "dashboard" / "index.html"
    return FileResponse(dashboard_file)

@app.get("/dashboard/", response_class=HTMLResponse)
async def serve_dashboard_alt():
    dashboard_file = Path(__file__).parent / "dashboard" / "index.html"
    return FileResponse(dashboard_file)

# === Rota para favicon ===
@app.get("/favicon.ico")
async def serve_favicon():
    # Retorna um favicon vazio para evitar erro 404
    return {"detail": "Favicon not found"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
         
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/curvaabc")
def curva_abc(db: Session = Depends(get_db)):
    logger.info("Chamando /curvaabc")
    try:
        result = crud.get_curva_abc(db)
        return result
    except Exception as e:
        logger.error(f"Erro em /curvaabc: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/duplicates")
def duplicates(db: Session = Depends(get_db)):
    logger.info("Chamando /duplicates")
    try:
        result = crud.get_duplicates(db)
        return result
    except Exception as e:
        logger.error(f"Erro em /duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/curva/{tipo}")
def produtos_por_curva(tipo: str, db: Session = Depends(get_db)):
    tipo = tipo.upper()
    if tipo not in ("A","B","C"):
        raise HTTPException(status_code=400, detail="Curva inválida: use A, B ou C")
    logger.info(f"Chamando /curva/{tipo}")
    try:
        result = crud.get_produtos_por_curva(db, tipo)
        return result
    except Exception as e:
        logger.error(f"Erro em /curva/{tipo}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/produtos/curva/{tipo}")
def produtos_por_curva_alt(tipo: str, db: Session = Depends(get_db)):
    """Endpoint alternativo para buscar produtos por curva"""
    tipo = tipo.upper()
    if tipo not in ("A","B","C"):
        raise HTTPException(status_code=400, detail="Curva inválida: use A, B ou C")
    logger.info(f"Chamando /produtos/curva/{tipo}")
    try:
        result = crud.get_produtos_por_curva(db, tipo)
        return result
    except Exception as e:
        logger.error(f"Erro em /produtos/curva/{tipo}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/curva-abc")
def curva_abc_endpoint(db: Session = Depends(get_db)):
    """Endpoint para buscar todos os produtos com curva ABC"""
    logger.info("Chamando /curva-abc")
    try:
        result = crud.get_curva_abc(db)
        return result
    except Exception as e:
        logger.error(f"Erro em /curva-abc: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/produtos")
def listar_todos_produtos(db: Session = Depends(get_db)):
    """Endpoint para buscar todos os produtos com informações completas"""
    logger.info("Chamando /api/produtos")
    try:
        # Buscar todos os produtos - removendo filtro 'ativo' que não existe
        produtos = db.query(models.Product).all()
        
        resultado = []
        for produto in produtos:
            # Usar os nomes corretos dos campos da tabela products
            estoque_atual = float(produto.stock or 0)
            preco_venda = float(produto.sale_price or 0)
            
            resultado.append({
                "id": produto.id,
                "codigo": produto.sku,
                "nome": produto.name,
                "estoque_atual": estoque_atual,
                "preco_venda": preco_venda,
                "localizacao": getattr(produto, 'localizacao', None) or getattr(produto, 'location', None),
                "curva_abc": produto.curve,
                "valor_total": estoque_atual * preco_venda
            })
        
        logger.info(f"Retornando {len(resultado)} produtos")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro em /api/produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/lucro/curvas", response_model=List[schemas.PercentualLucro])
def lucro_por_curva(db:Session = Depends(get_db)):
    logger.info("Chamando o /lucro/curvas")
    return crud.get_lucro_por_curva(db)

@app.get("/lucro/porcentagem",response_model=List[schemas.PercentualLucro])
def porcentagem_lucro_por_curva(db: Session = Depends(get_db)):
    logger.info("Chamando /lucro/porcentagem")
    return crud.get_percentual_lucro_curva(db)

# --- corrigir o problema do Swagger (URL sem barra) ---
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    # 👇 aqui forçamos o endereço correto do servidor
    openapi_schema["servers"] = [
    {"url": "http://127.0.0.1:8000/"}  # ✅ barra no final é obrigatória
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Dados para o dashboard - Versão melhorada com dados mais realistas
@app.get("/dashboard/dados")
def get_dados_dashboard(curva: str = "todas", produto: str = ""):
    from datetime import datetime
    from app.services.data_manager import data_manager
    
    db = SessionLocal()
    try:
        logger.info(f"Requisição dashboard - curva: {curva}, produto: {produto}")
        
        # Usar o novo gerenciador de dados
        dados = data_manager.get_real_dashboard_data(db)
        
        # Aplicar filtros se necessário
        if curva != "todas" or produto:
            # Buscar produtos com filtros para estatísticas específicas
            query = db.query(models.Product)
            
            if curva != "todas":
                query = query.filter(models.Product.curve == curva.upper())
                
            if produto:
                query = query.filter(
                    (models.Product.sku.ilike(f"%{produto}%")) | 
                    (models.Product.name.ilike(f"%{produto}%"))
                )
            
            produtos_filtrados = query.all()
            
            # Recalcular estatísticas para produtos filtrados
            dados.update({
                "total_produtos": len(produtos_filtrados),
                "curvaA": sum(1 for p in produtos_filtrados if p.curve == "A"),
                "curvaB": sum(1 for p in produtos_filtrados if p.curve == "B"),
                "curvaC": sum(1 for p in produtos_filtrados if p.curve == "C"),
                "filtro_aplicado": True,
                "filtro_curva": curva,
                "filtro_produto": produto
            })
        else:
            dados["filtro_aplicado"] = False
        
        logger.info(f"Dashboard retornando: {dados.get('total_produtos')} produtos")
        return dados
        
    except Exception as e:
        logger.error(f"Erro em /dashboard/dados: {e}")
        # Retornar dados de fallback em caso de erro
        from app.services.data_manager import data_manager
        return data_manager._get_fallback_data()
    finally:
        db.close()

# === Endpoints da API Tiny ERP ===
@app.get("/tiny/vendas")
def get_tiny_vendas():
    """Busca vendas da API do Tiny ERP"""
    logger.info("Chamando /tiny/vendas")
    try:
        data = fetch_tiny_vendas()
        return data
    except Exception as e:
        logger.error(f"Erro em /tiny/vendas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tiny/produtos")
def get_tiny_produtos():
    """Busca produtos da API do Tiny ERP"""
    logger.info("Chamando /tiny/produtos")
    try:
        data = listar_produtos_tiny()
        return data
    except Exception as e:
        logger.error(f"Erro em /tiny/produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tiny/estoque")
def get_tiny_estoque():
    """Busca estoque da API do Tiny ERP"""
    logger.info("Chamando /tiny/estoque")
    try:
        data = fetch_tiny_estoque()
        return data
    except Exception as e:
        logger.error(f"Erro em /tiny/estoque: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === Endpoint TEMPO REAL - Busca produtos ativos da API Tiny ===
@app.get("/api/tempo-real/produtos")
def get_produtos_tempo_real(filtros: str = "NR,GB,CP,KIT"):
    """
    Busca produtos em TEMPO REAL da API do Tiny ERP
    Filtros: NR,GB,CP,KIT (separados por vírgula)
    """
    logger.info(f"🔴 TEMPO REAL: Buscando produtos com filtros: {filtros}")
    try:
        # Converter string de filtros em lista
        lista_filtros = [f.strip().upper() for f in filtros.split(",") if f.strip()]
        
        # Buscar dados em tempo real da API do Tiny
        resultado = tiny_api.buscar_produtos_tempo_real(lista_filtros)
        
        logger.info(f"✅ TEMPO REAL: Encontrados {resultado['estatisticas']['total_encontrados']} produtos")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ Erro no endpoint tempo real: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados em tempo real: {str(e)}")

# === Endpoint para recalcular Curva ABC ===
@app.post("/curvaabc/recompute")
def recompute_curva_abc():
    """Recalcula e atualiza a Curva ABC no banco de dados"""
    logger.info("Chamando /curvaabc/recompute")
    db = SessionLocal()
    try:
        from decimal import Decimal, InvalidOperation
        
        produtos = db.query(models.Product).all()
        items = []
        total = Decimal('0')
        
        for p in produtos:
            try:
                price = Decimal(str(p.sale_price or 0))
            except InvalidOperation:
                price = Decimal('0')
            qty = p.stock or 0
            value = price * Decimal(qty)
            items.append((p, value))
            total += value

        if total == 0:
            items = sorted(items, key=lambda t: t[0].stock or 0, reverse=True)
            total = sum((t[0].stock or 0) for t in items) or 1

        items.sort(key=lambda t: t[1], reverse=True)

        acumulado = Decimal('0')
        for p, val in items:
            acumulado += val
            pct = (acumulado / total) * 100
            if pct <= Decimal('80'):
                p.curve = 'A'
            elif pct <= Decimal('95'):
                p.curve = 'B'
            else:
                p.curve = 'C'
            db.add(p)

        db.commit()
        logger.info(f"Curva ABC recalculada para {len(items)} produtos")
        return {"ok": True, "updated": len(items)}
        
    except Exception as e:
        logger.error(f"Erro em /curvaabc/recompute: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# === Endpoint para dados históricos das curvas ===
@app.get("/curvaabc/historico")
def get_curva_historico():
    """Retorna dados históricos simulados das curvas ABC por mês"""
    logger.info("Chamando /curvaabc/historico")
    
    try:
        # Dados simulados baseados no padrão atual
        # Em produção, isso viria de uma tabela de histórico
        historico = {
            "meses": ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"],
            "curva_a": [2, 3, 1, 2, 2, 2, 2, 1, 3, 3, 4, 4],
            "curva_b": [3, 4, 2, 3, 4, 3, 2, 4, 2, 3, 1, 2], 
            "curva_c": [1, 2, 4, 3, 1, 2, 1, 4, 1, 3, 1, 4]
        }
        
        return historico
        
    except Exception as e:
        logger.error(f"Erro em /curvaabc/historico: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === Endpoint para evolução das curvas com filtro de data - Versão melhorada ===
@app.get("/curvaabc/evolucao")
def curvaabc_evolucao(
    inicio: str = Query(..., description="Data inicial no formato YYYY-MM-DD"),
    fim: str = Query(..., description="Data final no formato YYYY-MM-DD")
):
    """Retorna a evolução das curvas ABC por mês dentro do período especificado"""
    logger.info(f"Chamando /curvaabc/evolucao - {inicio} a {fim}")
    
    try:
        from app.services.data_manager import data_manager
        
        # Usar o novo gerenciador para dados mais realistas
        dados_evolucao = data_manager.get_evolution_data(inicio, fim)
        
        if dados_evolucao.get("evolucao"):
            # Transformar em formato Chart.js
            meses = [item["mes"] for item in dados_evolucao["evolucao"]]
            curvaA = [item["curva_a"] for item in dados_evolucao["evolucao"]]
            curvaB = [item["curva_b"] for item in dados_evolucao["evolucao"]]
            curvaC = [item["curva_c"] for item in dados_evolucao["evolucao"]]
            
            resultado = {
                "meses": meses, 
                "A": curvaA, 
                "B": curvaB, 
                "C": curvaC,
                "fonte": dados_evolucao.get("fonte", "Sistema"),
                "periodo": f"{inicio} até {fim}"
            }
        else:
            # Fallback para método original
            db = SessionLocal()
            data_inicio = datetime.strptime(inicio, "%Y-%m-%d")
            data_fim = datetime.strptime(fim, "%Y-%m-%d")

            result = crud.evolucao_curva_abc(db, data_inicio, data_fim)
            db.close()

            # Transforma o resultado em estrutura Chart.js
            dados = {}
            for r in result:
                mes = r.mes
                if mes not in dados:
                    dados[mes] = {"A": 0, "B": 0, "C": 0}
                dados[mes][r.curve or "C"] = r.quantidade

            meses = sorted(dados.keys())
            curvaA = [dados[m]["A"] for m in meses]
            curvaB = [dados[m]["B"] for m in meses]
            curvaC = [dados[m]["C"] for m in meses]

            resultado = {
                "meses": meses, 
                "A": curvaA, 
                "B": curvaB, 
                "C": curvaC,
                "fonte": "Banco de Dados",
                "periodo": f"{inicio} até {fim}"
            }

        logger.info(f"Evolução retornada: {len(resultado['meses'])} meses")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro em /curvaabc/evolucao: {e}")
        # Dados de emergência
        return {
            "meses": ["2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09", "2025-10"], 
            "A": [145, 150, 148, 152, 155, 151, 149], 
            "B": [82, 79, 81, 78, 77, 79, 80], 
            "C": [73, 71, 71, 70, 68, 70, 71],
            "fonte": "Dados de Emergência",
            "periodo": f"{inicio} até {fim}",
            "erro": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)