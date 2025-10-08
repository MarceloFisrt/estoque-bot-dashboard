import os
import requests
from dotenv import load_dotenv

load_dotenv()
TINY_TOKEN = os.getenv("TINY_TOKEN")

def fetch_tiny_vendas():
    """Busca vendas da API do Tiny ERP"""
    url = "https://api.tiny.com.br/api2/pedidos.pesquisa.php"
    params = {
        "token": TINY_TOKEN,
        "formato": "json",
        "pagina": 1
    }
    
    try:
        res = requests.post(url, data=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados do Tiny: {e}")
        return {"erro": str(e)}

def listar_produtos_tiny(pagina=1):
    """Busca produtos da API do Tiny ERP"""
    url = "https://api.tiny.com.br/api2/produtos.pesquisa.php"
    params = {
        "token": TINY_TOKEN,
        "formato": "json",
        "pagina": 1
    }
    
    try:
        res = requests.post(url, data=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar produtos do Tiny: {e}")
        return {"erro": str(e)}

def fetch_tiny_estoque():
    """Busca estoque da API do Tiny ERP"""
    url = "https://api.tiny.com.br/api2/produtos.estoque.php"
    params = {
        "token": TINY_TOKEN,
        "formato": "json"
    }
    
    try:
        res = requests.post(url, data=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar estoque do Tiny: {e}")
        return {"erro": str(e)}