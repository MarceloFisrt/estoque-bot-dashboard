#!/usr/bin/env python3
"""
Script para popular o banco com dados de teste dos produtos
Simula produtos do Tiny ERP para demonstração
"""

from app.database import SessionLocal
from app import models
import random

def criar_produtos_teste():
    """Cria produtos de teste baseados nos padrões do Tiny ERP"""
    
    db = SessionLocal()
    
    try:
        # Verificar se já existem produtos
        count = db.query(models.Product).count()
        if count > 0:
            print(f"🟡 Já existem {count} produtos no banco. Removendo para inserir dados de teste...")
            db.query(models.Product).delete()
            db.commit()
        
        # Dados de produtos de teste baseados nos padrões NR, GB, CP, KIT
        produtos_teste = [
            # Produtos NR (Nacional)
            {"sku": "NR001", "name": "Notebook Dell Inspiron 15", "stock": 25, "sale_price": 2500.00, "curve": "A", "location": "A1-001"},
            {"sku": "NR002", "name": "Mouse Logitech MX Master", "stock": 150, "sale_price": 350.00, "curve": "B", "location": "B2-015"},
            {"sku": "NR003", "name": "Teclado Mecânico Gamer", "stock": 80, "sale_price": 450.00, "curve": "B", "location": "B2-020"},
            {"sku": "NR004", "name": "Monitor Samsung 24\" Full HD", "stock": 45, "sale_price": 800.00, "curve": "A", "location": "A1-010"},
            {"sku": "NR005", "name": "Webcam Logitech C920", "stock": 60, "sale_price": 280.00, "curve": "C", "location": "C3-005"},
            
            # Produtos GB (Global)
            {"sku": "GB001", "name": "iPhone 14 Pro Max 256GB", "stock": 15, "sale_price": 8500.00, "curve": "A", "location": "A1-002"},
            {"sku": "GB002", "name": "Samsung Galaxy S23 Ultra", "stock": 20, "sale_price": 6800.00, "curve": "A", "location": "A1-003"},
            {"sku": "GB003", "name": "MacBook Air M2", "stock": 8, "sale_price": 12000.00, "curve": "A", "location": "A1-001"},
            {"sku": "GB004", "name": "iPad Pro 11\" Wi-Fi", "stock": 30, "sale_price": 4500.00, "curve": "A", "location": "A1-005"},
            {"sku": "GB005", "name": "AirPods Pro 2ª Geração", "stock": 75, "sale_price": 1800.00, "curve": "B", "location": "B2-008"},
            
            # Produtos CP (Compra)
            {"sku": "CP001", "name": "Cabo USB-C para Lightning", "stock": 200, "sale_price": 85.00, "curve": "C", "location": "C3-010"},
            {"sku": "CP002", "name": "Carregador Turbo 65W", "stock": 120, "sale_price": 150.00, "curve": "C", "location": "C3-012"},
            {"sku": "CP003", "name": "Película de Vidro Temperado", "stock": 300, "sale_price": 25.00, "curve": "C", "location": "C3-020"},
            {"sku": "CP004", "name": "Suporte para Celular", "stock": 180, "sale_price": 45.00, "curve": "C", "location": "C3-015"},
            {"sku": "CP005", "name": "Fone de Ouvido Bluetooth", "stock": 95, "sale_price": 120.00, "curve": "C", "location": "C3-008"},
            
            # Produtos KIT (Kit)
            {"sku": "KIT001", "name": "Kit Gamer Completo", "stock": 12, "sale_price": 1200.00, "curve": "A", "location": "A1-015"},
            {"sku": "KIT002", "name": "Kit Home Office Premium", "stock": 18, "sale_price": 980.00, "curve": "B", "location": "B2-025"},
            {"sku": "KIT003", "name": "Kit Streaming Profissional", "stock": 8, "sale_price": 1800.00, "curve": "A", "location": "A1-020"},
            {"sku": "KIT004", "name": "Kit Proteção Smartphone", "stock": 50, "sale_price": 180.00, "curve": "C", "location": "C3-030"},
            {"sku": "KIT005", "name": "Kit Acessórios Notebook", "stock": 25, "sale_price": 350.00, "curve": "B", "location": "B2-018"},
            
            # Produtos adicionais para mais variedade
            {"sku": "NR006", "name": "Impressora HP LaserJet", "stock": 35, "sale_price": 1200.00, "curve": "B", "location": "B2-030"},
            {"sku": "GB006", "name": "Google Pixel 7 Pro", "stock": 22, "sale_price": 4200.00, "curve": "A", "location": "A1-008"},
            {"sku": "CP006", "name": "Hub USB 3.0", "stock": 140, "sale_price": 95.00, "curve": "C", "location": "C3-025"},
            {"sku": "NR007", "name": "SSD Samsung 1TB", "stock": 65, "sale_price": 580.00, "curve": "B", "location": "B2-012"},
            {"sku": "GB007", "name": "Apple Watch Series 9", "stock": 40, "sale_price": 3200.00, "curve": "A", "location": "A1-012"},
        ]
        
        # Inserir produtos no banco
        for produto_data in produtos_teste:
            produto = models.Product(
                sku=produto_data["sku"],
                name=produto_data["name"],
                stock=produto_data["stock"],
                sale_price=produto_data["sale_price"],
                curve=produto_data["curve"],
                location=produto_data["location"]
            )
            db.add(produto)
        
        db.commit()
        
        # Verificar inserção
        total_inseridos = db.query(models.Product).count()
        print(f"✅ {total_inseridos} produtos de teste inseridos com sucesso!")
        
        # Mostrar estatísticas
        curva_a = db.query(models.Product).filter(models.Product.curve == "A").count()
        curva_b = db.query(models.Product).filter(models.Product.curve == "B").count()
        curva_c = db.query(models.Product).filter(models.Product.curve == "C").count()
        
        print(f"📊 Distribuição por curva:")
        print(f"   Curva A: {curva_a} produtos")
        print(f"   Curva B: {curva_b} produtos")
        print(f"   Curva C: {curva_c} produtos")
        
        # Mostrar por categoria
        nr_count = db.query(models.Product).filter(models.Product.sku.like("NR%")).count()
        gb_count = db.query(models.Product).filter(models.Product.sku.like("GB%")).count()
        cp_count = db.query(models.Product).filter(models.Product.sku.like("CP%")).count()
        kit_count = db.query(models.Product).filter(models.Product.sku.like("KIT%")).count()
        
        print(f"🏷️ Distribuição por categoria:")
        print(f"   NR (Nacional): {nr_count} produtos")
        print(f"   GB (Global): {gb_count} produtos")
        print(f"   CP (Compra): {cp_count} produtos")
        print(f"   KIT (Kit): {kit_count} produtos")
        
    except Exception as e:
        print(f"❌ Erro ao inserir dados de teste: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Populando banco com dados de teste...")
    criar_produtos_teste()
    print("✅ Concluído!")