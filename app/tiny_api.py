#!/usr/bin/env python3
"""
Módulo para integração em tempo real com a API do Tiny ERP
Busca produtos ativos com SKU: NR*, GB*, CP*, KIT*
"""
import requests
import time
from typing import List, Dict, Optional
from fastapi import HTTPException
import logging

# Configurações da API Tiny
TINY_API_KEY = "4bf4a44588b5b069cbaa2da62c9bb5d0652ba151df38861d07dbb5ab2745ff59"
TINY_BASE_URL = "https://api.tiny.com.br/api2"

logger = logging.getLogger(__name__)

class TinyAPI:
    def __init__(self):
        self.api_key = TINY_API_KEY
        self.base_url = TINY_BASE_URL
        
    def buscar_produtos_tempo_real(self, filtros: List[str] = ["NR", "GB", "CP", "KIT"]) -> Dict:
        """
        Busca produtos em tempo real da API do Tiny com filtros específicos
        """
        try:
            resultado = {
                "status": "processando",
                "produtos": [],
                "estatisticas": {
                    "total_encontrados": 0,
                    "por_categoria": {},
                    "com_estoque": 0,
                    "sem_estoque": 0,
                    "valor_total_estoque": 0.0
                },
                "timestamp": time.time()
            }
            
            # Buscar produtos de forma síncrona
            produtos = self._buscar_produtos_filtrados(filtros)
            
            if produtos:
                # Processar estatísticas
                resultado["produtos"] = produtos
                resultado["estatisticas"] = self._calcular_estatisticas(produtos, filtros)
                resultado["status"] = "concluido"
            else:
                resultado["status"] = "erro"
                
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao buscar produtos em tempo real: {e}")
            raise HTTPException(status_code=500, detail=f"Erro na API do Tiny: {str(e)}")
    
    def _buscar_produtos_filtrados(self, filtros: List[str]) -> List[Dict]:
        """Busca produtos com filtros específicos"""
        produtos_encontrados = []
        pagina = 1
        max_paginas = 2  # Reduzir para evitar rate limit
        
        while pagina <= max_paginas:
            try:
                # Buscar produtos básicos
                params = {
                    'token': self.api_key,
                    'formato': 'json',
                    'pagina': pagina,
                    'situacao': 'A'  # A = Ativo
                }
                
                response = requests.get(f"{self.base_url}/produtos.pesquisa.php", params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if 'retorno' not in data:
                    break
                    
                retorno = data['retorno']
                
                if 'erro' in retorno:
                    if 'Nenhum registro foi encontrado' in str(retorno['erro']):
                        break
                    else:
                        logger.warning(f"Erro da API Tiny: {retorno['erro']}")
                        break
                
                produtos = retorno.get('produtos', [])
                
                if not produtos:
                    break
                
                # Filtrar produtos por SKU e processar dados básicos sem buscar detalhes
                for produto_item in produtos:
                    produto = produto_item.get('produto', {})
                    sku = produto.get('codigo', '').strip().upper()
                    nome = produto.get('descricao', '').strip()
                    
                    # Verificar se SKU começa com algum filtro
                    if any(sku.startswith(filtro) for filtro in filtros):
                        # Usar dados básicos disponíveis sem buscar detalhes (evita rate limit)
                        produto_basico = {
                            'id': produto.get('id'),
                            'sku': sku,
                            'nome': nome or f"Produto {sku}",
                            'preco_custo': float(produto.get('preco_custo', 0) or 0),
                            'preco_venda': float(produto.get('preco', 0) or 0),
                            'estoque_atual': 0,  # Será atualizado depois se necessário
                            'localizacao': 'Não informado',
                            'situacao': produto.get('situacao', ''),
                            'unidade': produto.get('unidade', 'UN'),
                            'valor_total': 0.0
                        }
                        
                        # Calcular valor total do estoque
                        produto_basico['valor_total'] = produto_basico['preco_venda'] * produto_basico['estoque_atual']
                        
                        produtos_encontrados.append(produto_basico)
                
                pagina += 1
                
                # Adicionar delay para evitar rate limit
                time.sleep(0.5)
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout na página {pagina}")
                break
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro de requisição na página {pagina}: {e}")
                break
            except Exception as e:
                logger.error(f"Erro inesperado na página {pagina}: {e}")
                break
        
        return produtos_encontrados
    
    def _buscar_detalhes_produto(self, produto_id: str, sku: str, nome: str) -> Optional[Dict]:
        """Busca detalhes completos de um produto"""
        try:
            if not produto_id:
                return None
            
            # Buscar dados básicos do produto
            params = {
                'token': self.api_key,
                'formato': 'json',
                'id': produto_id
            }
            
            response = requests.get(f"{self.base_url}/produto.obter.php", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            retorno = data.get('retorno', {})
            
            if 'erro' in retorno:
                logger.warning(f"Erro ao buscar produto {produto_id}: {retorno['erro']}")
                return None
            
            produto = retorno.get('produto', {})
            
            # Buscar estoque
            estoque_info = self._buscar_estoque_produto(produto_id)
            
            # Montar dados completos
            produto_completo = {
                'id': produto_id,
                'sku': produto.get('codigo', '').strip() or sku,
                'nome': produto.get('descricao', '').strip() or nome or f"Produto {sku}",
                'preco_custo': float(produto.get('preco_custo', 0) or 0),
                'preco_venda': float(produto.get('preco', 0) or 0),
                'estoque_atual': estoque_info.get('estoque', 0) if estoque_info else 0,
                'localizacao': produto.get('localizacao', '') or 'Não informado',
                'situacao': produto.get('situacao', ''),
                'unidade': produto.get('unidade', 'UN'),
                'valor_total': 0.0  # Será calculado depois
            }
            
            # Calcular valor total do estoque
            produto_completo['valor_total'] = produto_completo['preco_venda'] * produto_completo['estoque_atual']
            
            return produto_completo
            
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes do produto {produto_id}: {e}")
            return None
    
    def _buscar_estoque_produto(self, produto_id: str) -> Optional[Dict]:
        """Busca informações de estoque de um produto"""
        try:
            params = {
                'token': self.api_key,
                'formato': 'json',
                'id': produto_id
            }
            
            response = requests.get(f"{self.base_url}/produto.obter.estoque.php", params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            retorno = data.get('retorno', {})
            
            if 'erro' in retorno:
                return {'estoque': 0}
                
            produto = retorno.get('produto', {})
            return {
                'estoque': float(produto.get('estoqueAtual', 0) or 0)
            }
            
        except Exception:
            return {'estoque': 0}
    
    def _calcular_estatisticas(self, produtos: List[Dict], filtros: List[str]) -> Dict:
        """Calcula estatísticas dos produtos encontrados"""
        estatisticas = {
            "total_encontrados": len(produtos),
            "por_categoria": {},
            "com_estoque": 0,
            "sem_estoque": 0,
            "valor_total_estoque": 0.0,
            "produto_mais_caro": None,
            "produto_maior_estoque": None
        }
        
        # Inicializar contadores por categoria
        for filtro in filtros:
            estatisticas["por_categoria"][filtro] = 0
        
        produto_mais_caro = None
        produto_maior_estoque = None
        
        for produto in produtos:
            sku = produto.get('sku', '')
            estoque = produto.get('estoque_atual', 0)
            preco = produto.get('preco_venda', 0)
            valor_total = produto.get('valor_total', 0)
            
            # Contar por categoria
            for filtro in filtros:
                if sku.startswith(filtro):
                    estatisticas["por_categoria"][filtro] += 1
                    break
            
            # Contar estoque
            if estoque > 0:
                estatisticas["com_estoque"] += 1
                estatisticas["valor_total_estoque"] += valor_total
            else:
                estatisticas["sem_estoque"] += 1
            
            # Encontrar produto mais caro
            if not produto_mais_caro or preco > produto_mais_caro.get('preco_venda', 0):
                produto_mais_caro = produto
            
            # Encontrar produto com maior estoque
            if not produto_maior_estoque or estoque > produto_maior_estoque.get('estoque_atual', 0):
                produto_maior_estoque = produto
        
        estatisticas["produto_mais_caro"] = produto_mais_caro
        estatisticas["produto_maior_estoque"] = produto_maior_estoque
        
        return estatisticas

# Instância global
tiny_api = TinyAPI()