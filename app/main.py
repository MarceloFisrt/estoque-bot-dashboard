from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import os

from app import crud, schemas
from app.database import SessionLocal
from app.logger import get_logger
from sqlalchemy import text
from fastapi.responses import FileResponse






logger = get_logger()

app = FastAPI()

# === CORS (permite o front acessar o backend) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # pode restringir para ['http://127.0.0.1:8000'] depois
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Arquivos estáticos (CSS, JS, imagens) ===
from pathlib import Path
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory=Path("app/dashboard/static")), name="static")

# === Rota principal para o dashboard ===
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return FileResponse("app/dashboard/index.html")



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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
         
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/curvaabc", response_model=List[schemas.CurvaABCItem])
def curva_abc(db: Session = Depends(get_db)):
    logger.info("Chamando /curvaabc")
    return crud.get_curva_abc(db)

@app.get("/duplicates")
def duplicates(db: Session = Depends(get_db)):
    logger.info("Chamando /duplicates")
    return crud.get_duplicates(db)

@app.get("/curva/{tipo}", response_model=List[schemas.ProductBase])
def produtos_por_curva(tipo: str, db: Session = Depends(get_db)):
    tipo = tipo.upper()
    if tipo not in ("A","B","C"):
        raise HTTPException(status_code=400, detail="Curva inválida: use A, B ou C")
    logger.info(f"Chamando /curva/{tipo}")
    return crud.get_produtos_por_curva(db, tipo)
    
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
# --- fim da correção ---

from fastapi import APIRouter, Query
from app.database import SessionLocal


router = APIRouter()

@router.get("/dashboard/dados")
def get_dados_dashboard(curva: str = "todas", produto: str = ""):
    db = SessionLocal()

    query = text("SELECT sku, name, sale_price, cost_price, stock, curve FROM products WHERE 1=1")
    produtos = db.execute(query, params).fetchall()

    if curva != "todas":
        query += " AND curve = ?"
        params.append(curva)

    if produto:
        query += " AND (sku LIKE ? OR name LIKE ?)"
        params.extend([f"%{produto}%", f"%{produto}%"])

    produtos = db.execute(query, params).fetchall()

    total_produtos = len(produtos)
    lucro_total = sum([(p[2] - p[3]) * p[4] for p in produtos])
    curvaA = sum(1 for p in produtos if p[5] == "A")
    curvaB = sum(1 for p in produtos if p[5] == "B")
    curvaC = sum(1 for p in produtos if p[5] == "C")

    top = sorted(produtos, key=lambda p: (p[2] - p[3]) * p[4], reverse=True)[:10]
    produtos_top = [p[1] for p in top]
    lucros_top = [(p[2] - p[3]) * p[4] for p in top]

    return {
        "atualizacao": "07/10/2025 15:55",
        "total_produtos": total_produtos,
        "lucro_total": lucro_total,
        "curvaA": curvaA,
        "curvaB": curvaB,
        "curvaC": curvaC,
        "produtos_top": produtos_top,
        "lucros_top": lucros_top
    }

@router.get("/dashboard/dados")
def get_dados_dashboard(curva: str = "todas", produto: str = ""):
    db = SessionLocal()
    try:
        query = text("""
            SELECT sku, name, sale_price, cost_price, stock, curve
            FROM products
            WHERE 1=1
        """)
        params = {}

        if curva.lower() != "todas":
            query = text(str(query) + " AND curve = :curva")
            params["curva"] = curva.upper()

        if produto:
            query = text(str(query) + " AND (sku LIKE :produto OR name LIKE :produto)")
            params["produto"] = f"%{produto}%"

        produtos = db.execute(query, params).fetchall()

        total_produtos = len(produtos)
        lucro_total = sum([(p[2] - p[3]) * p[4] for p in produtos])
        curvaA = sum(1 for p in produtos if p[5] == "A")
        curvaB = sum(1 for p in produtos if p[5] == "B")
        curvaC = sum(1 for p in produtos if p[5] == "C")

        top = sorted(produtos, key=lambda p: (p[2] - p[3]) * p[4], reverse=True)[:10]
        produtos_top = [p[1] for p in top]
        lucros_top = [(p[2] - p[3]) * p[4] for p in top]

        return {
            "atualizacao": "07/10/2025 15:55",
            "total_produtos": total_produtos,
            "lucro_total": lucro_total,
            "curvaA": curvaA,
            "curvaB": curvaB,
            "curvaC": curvaC,
            "produtos_top": produtos_top,
            "lucros_top": lucros_top,
        }

    except Exception as e:
        print("❌ Erro no get_dados_dashboard:", e)
        raise
    finally:
        db.close()



app.include_router(router)
