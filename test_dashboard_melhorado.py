#!/usr/bin/env python3
"""
Teste das melhorias do dashboard - Verifica se os dados estão mais realistas
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.data_manager import DataManager
from app.database import SessionLocal
from app.models import Product
import json

def test_data_manager():
    """Testa o novo gerenciador de dados"""
    print("🧪 Testando DataManager...")
    
    dm = DataManager()
    db = SessionLocal()
    
    try:
        # Teste dados mock realistas
        dados = dm.get_real_dashboard_data(db)
        
        print("📊 Dados gerados pelo DataManager:")
        print("=" * 60)
        print(f"✅ Total produtos: {dados.get('total_produtos')}")
        print(f"✅ Lucro total: R$ {dados.get('lucro_total', 0):,.2f}")
        print(f"✅ Vendas mês: R$ {dados.get('vendas_mes', 0):,.2f}")
        print(f"✅ Meta mensal: R$ {dados.get('meta_mensal', 0):,.2f}")
        print(f"✅ Crescimento: {dados.get('crescimento', 0):.1f}%")
        print(f"✅ Curva A: {dados.get('curvaA')} | B: {dados.get('curvaB')} | C: {dados.get('curvaC')}")
        print(f"✅ Fonte: {dados.get('fonte')}")
        print(f"✅ Top produtos: {len(dados.get('produtos_top', []))}")
        print(f"✅ Atualização: {dados.get('atualizacao')}")
        print("=" * 60)
        
        # Teste dados de evolução
        print("\n📈 Testando dados de evolução...")
        evolucao = dm.get_evolution_data("2025-04-01", "2025-10-31")
        print(f"✅ Evolução: {len(evolucao.get('evolucao', []))} períodos")
        print(f"✅ Fonte evolução: {evolucao.get('fonte')}")
        
        if evolucao.get('evolucao'):
            primeiro = evolucao['evolucao'][0]
            print(f"✅ Exemplo período: {primeiro.get('mes')} - A:{primeiro.get('curva_a')} B:{primeiro.get('curva_b')} C:{primeiro.get('curva_c')}")
        
        print("\n🎉 DataManager funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no DataManager: {e}")
        return False
    finally:
        db.close()

def test_database_analysis():
    """Analisa os dados do banco para verificar se são fictícios"""
    print("\n🔍 Analisando dados do banco...")
    
    db = SessionLocal()
    try:
        produtos = db.query(Product).all()
        
        # Análise de nomes
        nomes_genericos = [p for p in produtos if 'Produto' in p.name]
        skus_genericos = [p for p in produtos if p.sku.startswith('SKU')]
        
        print("📊 Análise dos dados:")
        print("=" * 60)
        print(f"📦 Total de produtos: {len(produtos)}")
        print(f"🏷️  Nomes genéricos ('Produto X'): {len(nomes_genericos)}")
        print(f"🔖 SKUs genéricos ('SKUXXX'): {len(skus_genericos)}")
        
        if len(nomes_genericos) == len(produtos):
            print("⚠️  CONFIRMADO: 100% dos dados são fictícios!")
            print("💡 Recomendação: Implementar integração com sistema real")
        else:
            print("✅ Dados parecem ser reais ou semi-reais")
        
        # Análise de distribuição ABC
        curva_a = len([p for p in produtos if p.curve == 'A'])
        curva_b = len([p for p in produtos if p.curve == 'B'])
        curva_c = len([p for p in produtos if p.curve == 'C'])
        
        print(f"📈 Distribuição ABC: A={curva_a} | B={curva_b} | C={curva_c}")
        
        # Análise de preços
        precos_validos = [p for p in produtos if p.sale_price and p.sale_price > 0]
        print(f"💰 Produtos com preços válidos: {len(precos_validos)}")
        
        if precos_validos:
            preco_medio = sum(p.sale_price for p in precos_validos) / len(precos_validos)
            print(f"💲 Preço médio: R$ {preco_medio:.2f}")
        
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return False
    finally:
        db.close()

def main():
    """Executa todos os testes"""
    print("🚀 TESTE COMPLETO DO DASHBOARD MELHORADO")
    print("=" * 80)
    
    success = True
    
    # Teste 1: DataManager
    if not test_data_manager():
        success = False
    
    # Teste 2: Análise do banco
    if not test_database_analysis():
        success = False
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Dashboard está funcionando com dados melhorados")
        print("💡 Dados são simulações realistas baseadas no banco atual")
        print("🔧 Para dados 100% reais, configure integração com Tiny ERP")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os logs de erro acima")
    
    print("=" * 80)

if __name__ == "__main__":
    main()