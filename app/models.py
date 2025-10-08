from sqlalchemy import Column, Integer, String, Numeric, DateTime, CHAR, ForeignKey, JSON, func
from .database import Base
from datetime import datetime

class Product(Base):
	__tablename__ = "products"
	id = Column(Integer, primary_key=True, index=True)
	sku = Column(String, unique=True, index=True, nullable=False)
	name = Column(String, index=True, nullable=False)
	cost_price = Column(Numeric(12,2))
	sale_price = Column(Numeric(12,2))
	stock = Column(Integer, default=0)
	location = Column(String)
	margin_percent = Column(Numeric(6,2))
	curve = Column(CHAR(1))
	last_sync = Column(DateTime, server_default=func.now(), onupdate=func.now())
	created_at = Column(DateTime, default=datetime.utcnow)

class CompetitorPrice(Base):
	__tablename__ = "competitor_prices"
	id = Column(Integer, primary_key=True, index=True)
	product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
	source = Column(String, nullable=False)
	competitor_price = Column(Numeric(12,2))
	my_price = Column(Numeric(12,2))
	collected_at = Column(DateTime, server_default=func.now())

class Alert(Base):
	__tablename__ = "alerts"
	id = Column(Integer, primary_key=True, index=True)
	product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
	type = Column(String, nullable=False)
	message = Column(String, nullable=False)
	status = Column(String, default="ativo")
	created_at = Column(DateTime, server_default=func.now())
	resolved_at = Column(DateTime)

class SyncLog(Base):
	__tablename__ = "sync_logs"
	id = Column(Integer, primary_key=True, index=True)
	source = Column(String, nullable=False)
	status = Column(String, nullable=False)
	details = Column(JSON)
	created_at = Column(DateTime, server_default=func.now())

