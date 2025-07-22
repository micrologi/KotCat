#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar a tabela cidades ao banco de dados kotcat.db existente
"""

import sqlite3
import os


def adicionar_tabela_cidades():
    """Adiciona a tabela cidades ao banco de dados existente"""
    
    db_path = "data/kotcat.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        print("💡 Execute primeiro o script criar_banco_kotcat.py")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"🔧 Conectado ao banco: {db_path}")
        
        # Verificar se a tabela já existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='cidades'
        """)
        
        if cursor.fetchone():
            print("⚠️  Tabela 'cidades' já existe!")
            return True
        
        # Criar tabela cidades
        cursor.execute('''
            CREATE TABLE cidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estado TEXT NOT NULL,
                cidade TEXT NOT NULL,
                sigla_estado TEXT,
                codigo_ibge INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(estado, cidade)
            )
        ''')
        
        conn.commit()
        print("✅ Tabela 'cidades' criada com sucesso!")
        
        # Verificar estrutura
        cursor.execute("PRAGMA table_info(cidades)")
        colunas = cursor.fetchall()
        
        print("\n📊 ESTRUTURA DA TABELA CIDADES:")
        print("=" * 40)
        for col in colunas:
            print(f"  - {col[1]} ({col[2]}) - {'PRIMARY KEY' if col[5] else 'DEFAULT: ' + str(col[4]) if col[4] else ''}")
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        
        print(f"\n📋 TABELAS NO BANCO:")
        for tabela in tabelas:
            print(f"  - {tabela[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False
        
    finally:
        if conn:
            conn.close()


def testar_conexao():
    """Testa a conexão com o banco e as tabelas"""
    
    db_path = "data/kotcat.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🧪 TESTANDO BANCO DE DADOS")
        print("=" * 40)
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        
        print(f"1. Tabelas encontradas: {[t[0] for t in tabelas]}")
        
        # Verificar dados da tabela tipos
        if 'tipos' in [t[0] for t in tabelas]:
            cursor.execute("SELECT COUNT(*) FROM tipos")
            total_tipos = cursor.fetchone()[0]
            print(f"2. Total de tipos: {total_tipos}")
        
        # Verificar dados da tabela cidades
        if 'cidades' in [t[0] for t in tabelas]:
            cursor.execute("SELECT COUNT(*) FROM cidades")
            total_cidades = cursor.fetchone()[0]
            print(f"3. Total de cidades: {total_cidades}")
            
            if total_cidades > 0:
                cursor.execute("SELECT COUNT(DISTINCT estado) FROM cidades")
                total_estados = cursor.fetchone()[0]
                print(f"4. Total de estados: {total_estados}")
        
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print("🔧 ATUALIZANDO BANCO DE DADOS")
    print("=" * 40)
    
    if adicionar_tabela_cidades():
        testar_conexao()
        print("\n🎉 Banco de dados atualizado com sucesso!")
        print("\n📝 PRÓXIMOS PASSOS:")
        print("1. Execute carregar_cidades.py para carregar os dados")
        print("2. Use a classe BancoKotCat para acessar os dados")
    else:
        print("❌ Falha ao atualizar banco de dados!") 