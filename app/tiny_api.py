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
TINY_API_KEY = "d639ddb9c33895df8ba20bd70c82665c9d98d1e17bd553eb5816ff1313def6f0"
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
        """
        Busca produtos com filtros específicos da nova API
        Puxa: produto, nome, unidades, localização, preço, variação preço promocional, código
        Filtros: NR, GB, KIT, CP apenas ativos (com ou sem estoque)
        """
        produtos_encontrados = []
        pagina = 1
        max_paginas = 10  # Aumentar para pegar mais produtos
        
        logger.info(f"🔴 TEMPO REAL: Buscando produtos com filtros: {','.join(filtros)}")
        
        while pagina <= max_paginas:
            try:
                # Parâmetros para buscar produtos
                params = {
                    'token': self.api_key,
                    'formato': 'json',
                    'pagina': pagina,
                    'situacao': 'A'  # A = Ativo
                }
                
                response = requests.get(f"{self.base_url}/produtos.pesquisa.php", params=params, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                if 'retorno' not in data:
                    break
                    
                retorno = data['retorno']
                
                if 'erro' in retorno:
                    erro_msg = str(retorno['erro'])
                    if 'Nenhum registro foi encontrado' in erro_msg or 'não encontrado' in erro_msg.lower():
                        break
                    else:
                        logger.warning(f"Erro da API Tiny: {erro_msg}")
                        break
                
                produtos = retorno.get('produtos', [])
                
                if not produtos:
                    break
                
                # Processar produtos da página
                for produto_item in produtos:
                    produto = produto_item.get('produto', {})
                    sku = produto.get('codigo', '').strip().upper()
                    nome = produto.get('descricao', '').strip()
                    
                    # Verificar se SKU começa com algum filtro (NR, GB, KIT, CP)
                    if any(sku.startswith(filtro) for filtro in filtros):
                        
                        # Buscar detalhes específicos do produto
                        produto_detalhado = self._buscar_detalhes_produto_novo(
                            produto.get('id'), sku, nome, produto
                        )
                        
                        if produto_detalhado:
                            produtos_encontrados.append(produto_detalhado)
                
                pagina += 1
                
                # Delay para evitar rate limit
                time.sleep(0.3)
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout na página {pagina}")
                break
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro de requisição na página {pagina}: {e}")
                break
            except Exception as e:
                logger.error(f"Erro inesperado na página {pagina}: {e}")
                break
        
        logger.info(f"✅ TEMPO REAL: Encontrados {len(produtos_encontrados)} produtos")
        return produtos_encontrados
    
    def _buscar_detalhes_produto_novo(self, produto_id: str, sku: str, nome: str, produto_basico: Dict) -> Optional[Dict]:
        """
        Busca detalhes completos de um produto com as novas especificações
        Retorna: produto, nome, unidades, localização, preço, variação preço promocional, código
        """
        try:
            # Dados básicos do produto já disponíveis
            preco_venda = float(produto_basico.get('preco', 0) or 0)
            preco_custo = float(produto_basico.get('preco_custo', 0) or 0)
            preco_promocional = float(produto_basico.get('preco_promocional', 0) or 0)
            unidade = produto_basico.get('unidade', 'UN')
            situacao = produto_basico.get('situacao', 'A')
            
            # Tentar buscar estoque se o produto_id estiver disponível
            estoque_atual = 0
            localizacao = "Não informado"
            
            if produto_id:
                estoque_data = self._buscar_estoque_produto(produto_id)
                if estoque_data:
                    estoque_atual = estoque_data.get('estoque', 0)
                    localizacao = estoque_data.get('localizacao', 'Não informado')
            
            # Calcular variação de preço promocional
            variacao_preco = 0.0
            if preco_venda > 0 and preco_promocional > 0:
                variacao_preco = ((preco_venda - preco_promocional) / preco_venda) * 100
            
            # Determinar curva ABC baseada no preço
            curva_abc = self._calcular_curva_abc_por_preco(preco_venda)
            
            produto_completo = {
                'id': produto_id,
                'sku': sku,
                'codigo': sku,  # Alias para compatibilidade
                'nome': nome or f"Produto {sku}",
                'unidade': unidade,
                'localizacao': localizacao,
                'preco_venda': preco_venda,
                'preco_custo': preco_custo,
                'preco_promocional': preco_promocional,
                'variacao_preco_promocional': round(variacao_preco, 2),
                'estoque_atual': int(estoque_atual),
                'situacao': situacao,
                'valor_total': preco_venda * estoque_atual,
                'curva_abc': curva_abc,
                'categoria': self._determinar_categoria(sku)
            }
            
            return produto_completo
            
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes do produto {sku}: {e}")
            # Retornar produto básico mesmo com erro
            return {
                'id': produto_id,
                'sku': sku,
                'codigo': sku,
                'nome': nome or f"Produto {sku}",
                'unidade': produto_basico.get('unidade', 'UN'),
                'localizacao': 'Não informado',
                'preco_venda': float(produto_basico.get('preco', 0) or 0),
                'preco_custo': float(produto_basico.get('preco_custo', 0) or 0),
                'preco_promocional': 0.0,
                'variacao_preco_promocional': 0.0,
                'estoque_atual': 0,
                'situacao': produto_basico.get('situacao', 'A'),
                'valor_total': 0.0,
                'curva_abc': 'C',
                'categoria': self._determinar_categoria(sku)
            }
    
    def _buscar_estoque_produto(self, produto_id: str) -> Optional[Dict]:
        """Busca informações de estoque de um produto específico"""
        try:
            params = {
                'token': self.api_key,
                'formato': 'json',
                'id': produto_id
            }
            
            response = requests.get(f"{self.base_url}/produto.obter.estoque.php", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                retorno = data.get('retorno', {})
                
                if 'produto' in retorno:
                    produto_estoque = retorno['produto']
                    return {
                        'estoque': int(float(produto_estoque.get('saldo', 0) or 0)),
                        'localizacao': produto_estoque.get('localizacao', 'Não informado')
                    }
            
            return None
            
        except Exception as e:
            logger.warning(f"Não foi possível buscar estoque para produto {produto_id}: {e}")
            return None
    
    def _calcular_curva_abc_por_preco(self, preco: float) -> str:
        """Calcula curva ABC baseada no preço do produto"""
        if preco >= 100.0:
            return 'A'  # Produtos mais caros
        elif preco >= 50.0:
            return 'B'  # Produtos médios
        else:
            return 'C'  # Produtos mais baratos
    
    def _determinar_categoria(self, sku: str) -> str:
        """Determina categoria baseada no SKU"""
        if sku.startswith('NR'):
            return 'Nacional'
        elif sku.startswith('GB'):
            return 'Global'
        elif sku.startswith('CP'):
            return 'Compra'
        elif sku.startswith('KIT'):
            return 'Kit'
        else:
            return 'Outros'
    
    def _calcular_estatisticas(self, produtos: List[Dict], filtros: List[str]) -> Dict:
        """Calcula estatísticas dos produtos encontrados com novos campos"""
        estatisticas = {
            "total_produtos": len(produtos),
            "total_encontrados": len(produtos),
            "por_categoria": {},
            "com_estoque": 0,
            "sem_estoque": 0,
            "valor_total_estoque": 0.0,
            "produto_mais_caro": None,
            "produto_maior_estoque": None,
            "preco_medio": 0.0,
            "produtos_promocionais": 0,
            "curva_abc": {"A": 0, "B": 0, "C": 0}
        }
        
        # Inicializar contadores por categoria
        for filtro in filtros:
            estatisticas["por_categoria"][filtro] = 0
        
        produto_mais_caro = None
        produto_maior_estoque = None
        soma_precos = 0.0
        
        for produto in produtos:
            sku = produto.get('sku', '')
            estoque = produto.get('estoque_atual', 0)
            preco = produto.get('preco_venda', 0)
            preco_promocional = produto.get('preco_promocional', 0)
            valor_total = produto.get('valor_total', 0)
            curva = produto.get('curva_abc', 'C')
            
            # Contar por categoria
            categoria_encontrada = False
            for filtro in filtros:
                if sku.startswith(filtro):
                    estatisticas["por_categoria"][filtro] += 1
                    categoria_encontrada = True
                    break
            
            if not categoria_encontrada:
                if "Outros" not in estatisticas["por_categoria"]:
                    estatisticas["por_categoria"]["Outros"] = 0
                estatisticas["por_categoria"]["Outros"] += 1
            
            # Contar estoque
            if estoque > 0:
                estatisticas["com_estoque"] += 1
                estatisticas["valor_total_estoque"] += valor_total
            else:
                estatisticas["sem_estoque"] += 1
            
            # Contar produtos promocionais
            if preco_promocional > 0 and preco_promocional < preco:
                estatisticas["produtos_promocionais"] += 1
            
            # Contar curva ABC
            if curva in estatisticas["curva_abc"]:
                estatisticas["curva_abc"][curva] += 1
            
            # Somar preços para média
            soma_precos += preco
            
            # Encontrar produto mais caro
            if not produto_mais_caro or preco > produto_mais_caro.get('preco_venda', 0):
                produto_mais_caro = produto
            
            # Encontrar produto com maior estoque
            if not produto_maior_estoque or estoque > produto_maior_estoque.get('estoque_atual', 0):
                produto_maior_estoque = produto
        
        # Calcular preço médio
        if len(produtos) > 0:
            estatisticas["preco_medio"] = soma_precos / len(produtos)
        
        estatisticas["produto_mais_caro"] = produto_mais_caro
        estatisticas["produto_maior_estoque"] = produto_maior_estoque
        
        return estatisticas

# Instância global
tiny_api = TinyAPI()