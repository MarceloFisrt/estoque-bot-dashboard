from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from pathlib import Path

# Carregar o .env da raiz do projeto sempre
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"[DATABASE] Carregando DATABASE_URL: {DATABASE_URL}")  # Debug

if not DATABASE_URL:
	# Deixar aqui para facilitar debugging quando .env não estiver configurado
	raise RuntimeError("DATABASE_URL não encontrado. Configure o arquivo .env na raiz do projeto.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

