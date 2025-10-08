from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sku: str
    name: str
    cost_price: Optional[float] = None
    sale_price: Optional[float] = None
    stock: Optional[int] = 0
    margem_percent: Optional[float] = None
    curve: Optional[str] = None

class CurvaABCItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sku: str
    name: str
    stock: int
    sale_price: float
    valor_total: float
    perc_acumulado: float
    curva: str

class LucroPorCurva(BaseModel):
    curve: str
    margem_media: Optional[float] = 0.0
    lucro_total: Optional[float] = 0.0

class PercentualLucro(BaseModel):
    curve: str
    lucro_curva: Optional[float] = 0.0
    perc_total: Optional[float] = 0.0

    