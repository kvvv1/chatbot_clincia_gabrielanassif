#!/usr/bin/env python3
"""
Script para limpar conversas antigas e resetar estados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_fallback_config():
    """Configurar fallback para quando não há .env"""
    from app.config import create_fallback_settings
    import app.config as config_module
    
    # Usar configurações fallback
    config_module.settings = create_fallback_settings()
    print("⚙️  Usando configurações fallback (SQLite)")

def limpar_conversas():
    print("🧹 LIMPEZA DE CONVERSAS ANTIGAS")
    print("=" * 50)
    
    try:
        # Tentar configurar banco
        setup_fallback_config()
        
        from app.models.database import get_db_session, Conversation
        
        db = get_db_session()
        print("✅ Conectado ao banco de dados")
        
        # Contar conversas atuais
        total_conversas = db.query(Conversation).count()
        print(f"📊 Total de conversas no banco: {total_conversas}")
        
        if total_conversas > 0:
            # Mostrar algumas conversas
            conversas = db.query(Conversation).limit(5).all()
            print("\n📋 Últimas conversas:")
            for conv in conversas:
                print(f"   📱 {conv.phone} - Estado: {conv.state} - Context: {conv.context}")
            
            # Perguntar se quer limpar
            resposta = input(f"\n❓ Deseja limpar TODAS as {total_conversas} conversas? (s/N): ")
            
            if resposta.lower() in ['s', 'sim', 'y', 'yes']:
                # Limpar todas as conversas
                db.query(Conversation).delete()
                db.commit()
                print("🗑️  Todas as conversas foram removidas!")
                print("✅ Banco limpo - próximas mensagens começarão do zero")
            else:
                print("❌ Limpeza cancelada")
        else:
            print("✅ Não há conversas para limpar")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {str(e)}")
        print("💡 Verifique as configurações do banco de dados")

def verificar_estrutura_banco():
    print("\n\n🔍 VERIFICAÇÃO DA ESTRUTURA")
    print("=" * 50)
    
    try:
        setup_fallback_config()
        from app.models.database import engine, Base
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📊 Tabelas encontradas: {tables}")
        
        if 'conversations' in tables:
            columns = inspector.get_columns('conversations')
            print("\n📋 Colunas da tabela conversations:")
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
        else:
            print("⚠️  Tabela 'conversations' não encontrada!")
            print("💡 Execute: python -c 'from app.models.database import create_tables; create_tables()'")
            
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {str(e)}")

def criar_conversa_teste():
    print("\n\n🧪 CRIAR CONVERSA DE TESTE")
    print("=" * 50)
    
    try:
        setup_fallback_config()
        from app.models.database import get_db_session, Conversation
        
        db = get_db_session()
        
        # Criar conversa de teste
        test_phone = "5531999999999@c.us"
        
        # Remover conversa anterior se existir
        db.query(Conversation).filter_by(phone=test_phone).delete()
        
        # Criar nova conversa
        conversa_teste = Conversation(
            phone=test_phone,
            state="menu_principal",
            context={}
        )
        
        db.add(conversa_teste)
        db.commit()
        
        print(f"✅ Conversa de teste criada:")
        print(f"   📱 Telefone: {test_phone}")
        print(f"   🔄 Estado: menu_principal")
        print(f"   📋 Contexto: {{}}")
        print("\n💡 Agora teste enviando '1' para este número!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar conversa de teste: {str(e)}")

if __name__ == "__main__":
    try:
        limpar_conversas()
        verificar_estrutura_banco()
        criar_conversa_teste()
        
        print("\n\n🎯 PRÓXIMOS PASSOS:")
        print("1. 🔄 Reinicie a aplicação")
        print("2. 📱 Teste enviando mensagem para o chatbot")
        print("3. 👀 Verifique os logs para ver o processamento")
        print("4. 📊 Se ainda houver problema, verifique configuração do banco")
        
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")