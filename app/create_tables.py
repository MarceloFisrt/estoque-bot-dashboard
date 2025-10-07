from .database import engine, Base
from .models import Product, CompetitorPrice, Alert, SyncLog

def run():
	Base.metadata.create_all(bind=engine)
	print("Tabelas criadas com sucesso.")

if __name__ == "__main__":
	run()

