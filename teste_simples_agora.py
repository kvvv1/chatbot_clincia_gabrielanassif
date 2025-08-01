#!/usr/bin/env python3
"""
Teste simples e direto - SEM imports complexos
"""
import os
import sys

def test_basic_imports():
    """Teste básico de imports"""
    print("🔍 TESTE BÁSICO - IMPORTS")
    print("=" * 30)
    
    try:
        # Adicionar path
        sys.path.append('.')
        
        # Configurar ambiente
        os.environ['ENVIRONMENT'] = 'development'
        
        print("✅ Path configurado")
        print("✅ Environment configurado")
        
        # Testar import config
        from app.config import settings
        print("✅ Config importado")
        
        # Testar database URL
        from app.models.database import get_database_url
        db_url = get_database_url()
        print(f"✅ Database URL: {db_url}")
        
        # Verificar se é SQLite (deve ser local)
        if 'sqlite' in db_url.lower():
            print("✅ Usando SQLite (correto para desenvolvimento)")
        else:
            print(f"⚠️ Usando PostgreSQL: {db_url[:50]}...")
        
        print("\n🎉 CONFIGURAÇÃO BÁSICA FUNCIONANDO!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_conversation_import():
    """Teste import conversation manager"""
    print("\n🔍 TESTE CONVERSATION MANAGER")
    print("=" * 35)
    
    try:
        from app.services.conversation import ConversationManager
        conversation_manager = ConversationManager()
        print("✅ ConversationManager criado")
        
        # Testar método específico
        if hasattr(conversation_manager, 'processar_mensagem'):
            print("✅ Método processar_mensagem existe")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no ConversationManager: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE RÁPIDO DO CHATBOT")
    print("=" * 40)
    
    # Teste 1: Imports básicos
    if not test_basic_imports():
        print("❌ Teste básico falhou")
        return
    
    # Teste 2: Conversation Manager
    if not test_conversation_import():
        print("❌ ConversationManager falhou")
        return
    
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("💡 O chatbot deve estar funcionando")
    print("📱 Teste enviando 'oi' no WhatsApp")

if __name__ == "__main__":
    main()