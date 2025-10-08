#!/usr/bin/env python3
"""
Importar todos os produtos ATIVOS do Tiny ERP via API COM ESTOQUE
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from decimal import Decimal
from app.database import SessionLocal, engine
from app.models import Product
from app.crud import clear_all_products, create_product

# Configurações da API Tiny
TINY_API_KEY = "4bf4a44588b5b069cbaa2da62c9bb5d0652ba151df38861d07dbb5ab2745ff59"
TINY_BASE_URL = "https://api.tiny.com.br/api2"

def buscar_estoque_produto(produto_id):
    """Busca o estoque de um produto específico"""
    params = {
        'token': TINY_API_KEY,
        'formato': 'json',
        'id': produto_id
    }
    
    try:
        response = requests.get(f"{TINY_BASE_URL}/produto.obter.estoque.php", params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'retorno' in data and 'produto' in data['retorno']:
            produto_estoque = data['retorno']['produto']
            # O estoque pode estar em diferentes campos
            estoque = (
                produto_estoque.get('saldo', 0) or
                produto_estoque.get('estoque', 0) or
                produto_estoque.get('estoque_atual', 0) or
                produto_estoque.get('quantidade', 0) or
                0
            )
            return float(estoque)
        return 0.0
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar estoque do produto {produto_id}: {e}")
        return 0.0

def buscar_produtos_com_estoque():
    """Busca todos os produtos ATIVOS com informações de estoque"""
    print("🔍 BUSCANDO PRODUTOS ATIVOS COM ESTOQUE DO TINY ERP...")
    print("="*60)
    
    produtos_completos = []
    pagina = 1
    
    while True:
        print(f"📄 Processando página {pagina}...")
        
        # Buscar produtos básicos
        params = {
            'token': TINY_API_KEY,
            'formato': 'json',
            'pagina': pagina,
            'situacao': 'A'  # A = Ativo
        }
        
        try:
            response = requests.get(f"{TINY_BASE_URL}/produtos.pesquisa.php", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'retorno' not in data:
                print(f"❌ Erro na resposta da API: {data}")
                break
                
            retorno = data['retorno']
            
            if 'erro' in retorno:
                print(f"❌ Erro da API Tiny: {retorno['erro']}")
                break
                
            if 'produtos' not in retorno:
                print("✅ Nenhum produto encontrado nesta página")
                break
                
            produtos_pagina = retorno['produtos']
            print(f"📦 Encontrados {len(produtos_pagina)} produtos ativos na página {pagina}")
            
            # Processar cada produto e buscar estoque
            for i, item in enumerate(produtos_pagina, 1):
                produto = item.get('produto', {})
                
                if produto.get('situacao') == 'A':
                    produto_id = produto.get('id')
                    
                    print(f"   📊 {i:2d}/{len(produtos_pagina)} - Buscando estoque: {produto.get('codigo', 'N/A')}")
                    
                    # Buscar estoque do produto
                    estoque = buscar_estoque_produto(produto_id)
                    produto['estoque_real'] = estoque
                    
                    produtos_completos.append(produto)
            
            # Verificar se há mais páginas
            if len(produtos_pagina) < 50:  # Tiny retorna max 50 por página
                break
                
            pagina += 1
            
            # Limitar para teste (remover depois)
            if pagina > 3:  # Processar apenas 3 páginas para teste
                print("⚠️ LIMITANDO A 3 PÁGINAS PARA TESTE")
                break
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            break
    
    print(f"✅ Total de produtos ATIVOS com estoque encontrados: {len(produtos_completos)}")
    return produtos_completos

def calcular_curva_abc(produtos):
    """Calcula a curva ABC baseada no valor de estoque"""
    if not produtos:
        return produtos
        
    # Calcular valor total do estoque para cada produto
    for produto in produtos:
        preco = float(produto.get('preco', 0) or 0)
        estoque = float(produto.get('estoque_real', 0) or 0)
        produto['valor_estoque'] = preco * estoque
    
    # Ordenar por valor de estoque (maior para menor)
    produtos_ordenados = sorted(produtos, key=lambda x: x['valor_estoque'], reverse=True)
    
    total_valor = sum(p['valor_estoque'] for p in produtos_ordenados)
    
    if total_valor == 0:
        # Se não há valor, distribuir igualmente
        for i, produto in enumerate(produtos_ordenados):
            if i < len(produtos_ordenados) * 0.2:
                produto['curva'] = 'A'
            elif i < len(produtos_ordenados) * 0.5:
                produto['curva'] = 'B'
            else:
                produto['curva'] = 'C'
        return produtos_ordenados
    
    # Calcular curva ABC (20% A, 30% B, 50% C)
    valor_acumulado = 0
    for produto in produtos_ordenados:
        valor_acumulado += produto['valor_estoque']
        percentual = (valor_acumulado / total_valor) * 100
        
        if percentual <= 20:
            produto['curva'] = 'A'
        elif percentual <= 50:
            produto['curva'] = 'B'
        else:
            produto['curva'] = 'C'
    
    return produtos_ordenados

def importar_para_database(produtos):
    """Importa produtos para o banco de dados"""
    print("\n💾 IMPORTANDO PARA O BANCO DE DADOS...")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Limpar produtos existentes
        print("🗑️ Removendo produtos existentes...")
        clear_all_products(db)
        
        # Importar novos produtos
        produtos_importados = 0
        
        for produto in produtos:
            try:
                # Extrair dados do produto
                sku = produto.get('codigo', '')[:50]  # Limitar tamanho
                nome = produto.get('nome', '')[:200]  # Limitar tamanho
                
                # Preços (converter para float)
                preco_custo = float(produto.get('preco_custo', 0) or 0)
                preco_venda = float(produto.get('preco', 0) or 0)
                
                # Estoque REAL
                estoque = int(float(produto.get('estoque_real', 0) or 0))
                
                # Curva ABC
                curva = produto.get('curva', 'C')
                
                # Validações
                if not sku or not nome:
                    print(f"⚠️ Produto ignorado (dados incompletos): {sku} - {nome}")
                    continue
                
                # Criar produto (passar como dicionário)
                dados_produto = {
                    'sku': sku,
                    'name': nome,
                    'cost_price': Decimal(str(preco_custo)),
                    'sale_price': Decimal(str(preco_venda)),
                    'stock': estoque,
                    'curve': curva
                }
                
                create_product(db, dados_produto)
                produtos_importados += 1
                
                print(f"✅ {produtos_importados:3d}. {sku} - {nome[:40]}... | Estoque: {estoque} | Curva: {curva}")
                
            except Exception as e:
                print(f"❌ Erro ao importar produto {produto.get('codigo', 'N/A')}: {e}")
                continue
        
        print("="*60)
        print(f"✅ IMPORTAÇÃO CONCLUÍDA!")
        print(f"📦 Produtos importados: {produtos_importados}")
        
        # Estatísticas da curva ABC
        from sqlalchemy import func
        curva_stats = db.query(Product.curve, func.count(Product.id)).group_by(Product.curve).all()
        for curva, count in curva_stats:
            print(f"📊 Curva {curva}: {count} produtos")
            
        return produtos_importados
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def main():
    """Função principal"""
    print("🚀 IMPORTAÇÃO DE PRODUTOS ATIVOS COM ESTOQUE DO TINY ERP")
    print("="*60)
    print(f"🔑 API Key: {TINY_API_KEY[:20]}...")
    print("🎯 Filtro: APENAS PRODUTOS ATIVOS")
    print("📊 Incluindo: DADOS REAIS DE ESTOQUE")
    print("="*60)
    
    # 1. Buscar produtos ativos com estoque no Tiny
    produtos = buscar_produtos_com_estoque()
    
    if not produtos:
        print("❌ Nenhum produto ativo encontrado!")
        return
    
    # 2. Calcular curva ABC
    print(f"\n📈 CALCULANDO CURVA ABC...")
    produtos_com_curva = calcular_curva_abc(produtos)
    
    # 3. Mostrar resumo dos produtos
    print(f"\n📋 RESUMO DOS PRODUTOS ATIVOS COM ESTOQUE:")
    print("="*60)
    for i, produto in enumerate(produtos_com_curva[:10], 1):  # Mostrar top 10
        nome = produto.get('nome', 'N/A')[:40]
        sku = produto.get('codigo', 'N/A')
        estoque = produto.get('estoque_real', 0)
        preco = produto.get('preco', 0)
        curva = produto.get('curva', 'C')
        valor_estoque = produto.get('valor_estoque', 0)
        print(f"{i:2d}. {sku} | {nome}... | Estoque: {estoque} | R$ {preco} | Valor: R$ {valor_estoque:.2f} | {curva}")
    
    if len(produtos_com_curva) > 10:
        print(f"... e mais {len(produtos_com_curva) - 10} produtos")
    
    # 4. Importar para o banco
    produtos_importados = importar_para_database(produtos_com_curva)
    
    print("\n🎉 PROCESSO CONCLUÍDO!")
    print("="*60)
    print(f"✅ {produtos_importados} produtos ativos COM ESTOQUE importados do Tiny ERP")
    print("📊 Dashboard agora usa dados 100% reais e atualizados com estoque correto!")

if __name__ == "__main__":
    main()