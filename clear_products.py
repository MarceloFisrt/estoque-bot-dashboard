from app.database import SessionLocal
from app import models

db = SessionLocal()

confirm = input("Tem certeza que quer APAGAR todos os produtos? (s/n): ")
if confirm.lower() == 's':
    deleted = db.query(models.Product).delete()
    db.commit()
    print(f"✅ {deleted} produtos apagados do banco.")
else:
    print("❌ Operação cancelada.")

db.close()
