from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import os

from app import crud, schemas, models
from app.database import SessionLocal
from app.logger import get_logger
from sqlalchemy import text
from fastapi.responses import FileResponse






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
async def serve_dashboard_with_slash():
    dashboard_file = Path(__file__).parent / "dashboard" / "index.html"
    return FileResponse(dashboard_file)

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
# Dados para o dashboard
@app.get("/dashboard/dados")
def get_dados_dashboard(curva: str = "todas", produto: str = ""):
    from datetime import datetime
    db = SessionLocal()
    try:
        # Buscar produtos com filtros
        query = db.query(models.Product)
        
        if curva != "todas":
            query = query.filter(models.Product.curve == curva.upper())
            
        if produto:
            query = query.filter(
                (models.Product.sku.ilike(f"%{produto}%")) | 
                (models.Product.name.ilike(f"%{produto}%"))
            )
        
        produtos = query.all()
        
        # Calcular estatísticas
        total_produtos = len(produtos)
        lucro_total = sum([
            ((p.sale_price or 0) - (p.cost_price or 0)) * (p.stock or 0) 
            for p in produtos
        ])
        
        curvaA = sum(1 for p in produtos if p.curve == "A")
        curvaB = sum(1 for p in produtos if p.curve == "B") 
        curvaC = sum(1 for p in produtos if p.curve == "C")
        
        # Top 10 produtos por lucro
        produtos_ordenados = sorted(
            produtos, 
            key=lambda p: ((p.sale_price or 0) - (p.cost_price or 0)) * (p.stock or 0), 
            reverse=True
        )[:10]
        
        produtos_top = [p.name for p in produtos_ordenados]
        lucros_top = [
            ((p.sale_price or 0) - (p.cost_price or 0)) * (p.stock or 0) 
            for p in produtos_ordenados
        ]
        
        return {
            "atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total_produtos": total_produtos,
            "lucro_total": float(lucro_total),
            "curvaA": curvaA,
            "curvaB": curvaB,
            "curvaC": curvaC,
            "produtos_top": produtos_top,
            "lucros_top": [float(l) for l in lucros_top]
        }
        
    except Exception as e:
        logger.error(f"Erro em /dashboard/dados: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
