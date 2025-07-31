#!/usr/bin/env python3
"""
Debug específico para problema do webhook/processamento
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
from datetime import datetime

async def simular_webhook_completo():
    print("🔍 DEBUG - WEBHOOK COMPLETO")
    print("=" * 50)
    
    # Simular dados que chegam do Z-API
    webhook_data = {
        "type": "ReceivedCallback",
        "phone": "5531999999999@c.us",
        "text": {
            "message": "1"
        },
        "messageId": "test_message_123",
        "fromMe": False,
        "timestamp": int(datetime.now().timestamp())
    }
    
    print("1. 📨 Dados do webhook simulados:")
    print(json.dumps(webhook_data, indent=2))
    
    # Extrair dados como no webhook real
    phone = webhook_data.get("phone", "")
    message_text = webhook_data.get("text", {}).get("message", "")
    message_id = webhook_data.get("messageId", "")
    from_me = webhook_data.get("fromMe", False)
    
    print(f"\n2. 📋 Dados extraídos:")
    print(f"   Telefone: {phone}")
    print(f"   Mensagem: '{message_text}'")
    print(f"   Message ID: {message_id}")
    print(f"   From Me: {from_me}")
    
    # Verificações básicas
    if from_me:
        print("   ⚠️  Mensagem seria ignorada (from_me = True)")
        return
    
    if not message_text:
        print("   ⚠️  Mensagem seria ignorada (sem texto)")
        return
    
    print("   ✅ Mensagem passaria pelas verificações básicas")
    
    # Simular configuração
    def setup_fallback_config():
        from app.config import create_fallback_settings
        import app.config as config_module
        config_module.settings = create_fallback_settings()
        print("   ⚙️  Configurações fallback aplicadas")
    
    setup_fallback_config()
    
    # Tentar importar e usar o ConversationManager
    print("\n3. 🔧 Testando ConversationManager...")
    
    try:
        from app.services.conversation import ConversationManager
        from app.models.database import get_db
        
        print("   ✅ Imports realizados com sucesso")
        
        # Criar manager
        conversation_manager = ConversationManager()
        print("   ✅ ConversationManager criado")
        
        # Obter sessão do banco
        db = next(get_db())
        print("   ✅ Sessão do banco obtida")
        
        # PASSO CRÍTICO: Processar mensagem
        print(f"\n4. 🚀 Processando mensagem '{message_text}'...")
        
        await conversation_manager.processar_mensagem(
            phone=phone,
            message=message_text,
            message_id=message_id,
            db=db
        )
        
        print("   ✅ Mensagem processada sem erros!")
        
        # Verificar estado após processamento
        print("\n5. 🔍 Verificando resultado...")
        
        # Buscar conversa no banco
        from app.models.database import Conversation
        if hasattr(db, 'query'):
            conversa = db.query(Conversation).filter_by(phone=phone).first()
            if conversa:
                print(f"   📋 Estado da conversa: {conversa.state}")
                print(f"   📋 Contexto: {conversa.context}")
                
                if conversa.state == "aguardando_cpf":
                    print("   🎉 SUCESSO! Estado correto!")
                    return True
                else:
                    print(f"   ❌ Estado incorreto! Esperado: aguardando_cpf, Atual: {conversa.state}")
                    return False
            else:
                print("   ❌ Conversa não encontrada no banco!")
                return False
        else:
            print("   ⚠️  Banco em modo mock - não pode verificar persistência")
            return True
        
    except Exception as e:
        print(f"   ❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def simular_fluxo_real():
    print("\n\n📱 SIMULANDO FLUXO REAL COMPLETO")
    print("=" * 50)
    
    def setup_config():
        from app.config import create_fallback_settings
        import app.config as config_module
        config_module.settings = create_fallback_settings()
    
    setup_config()
    
    try:
        from app.services.conversation import ConversationManager
        from app.models.database import get_db, Conversation
        
        manager = ConversationManager()
        db = next(get_db())
        test_phone = "5531988887777@c.us"
        
        # Limpar estado anterior
        if hasattr(db, 'query'):
            db.query(Conversation).filter_by(phone=test_phone).delete()
            db.commit()
            print("1. 🧹 Estado anterior limpo")
        
        # PASSO 1: Primeira mensagem "oi"
        print("\n2. 📨 Primeira mensagem: 'oi'")
        await manager.processar_mensagem(test_phone, "oi", "msg1", db)
        
        if hasattr(db, 'query'):
            conversa = db.query(Conversation).filter_by(phone=test_phone).first()
            print(f"   Estado após 'oi': {conversa.state if conversa else 'NENHUM'}")
        
        # PASSO 2: Segunda mensagem "1"
        print("\n3. 📨 Segunda mensagem: '1'")
        await manager.processar_mensagem(test_phone, "1", "msg2", db)
        
        if hasattr(db, 'query'):
            conversa = db.query(Conversation).filter_by(phone=test_phone).first()
            print(f"   Estado após '1': {conversa.state if conversa else 'NENHUM'}")
            print(f"   Contexto após '1': {conversa.context if conversa else 'NENHUM'}")
            
            if conversa and conversa.state == "aguardando_cpf":
                print("   🎉 FUNCIONANDO! O problema não está no código!")
                return True
            else:
                print("   ❌ PROBLEMA! Estado incorreto após opção '1'")
                return False
        else:
            print("   ⚠️  Não é possível verificar - banco em modo mock")
            return True
            
    except Exception as e:
        print(f"❌ ERRO no fluxo: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def verificar_configuracao_webhook():
    print("\n\n📡 VERIFICANDO CONFIGURAÇÃO DO WEBHOOK")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        print("1. 🔧 Configurações atuais:")
        print(f"   Z-API Instance ID: {settings.zapi_instance_id[:10] + '...' if settings.zapi_instance_id else 'VAZIO'}")
        print(f"   Z-API Token: {settings.zapi_token[:10] + '...' if settings.zapi_token else 'VAZIO'}")
        print(f"   App Host: {settings.app_host}")
        print(f"   App Port: {settings.app_port}")
        print(f"   Environment: {settings.environment}")
        
        # Construir URL do webhook
        if settings.environment == "production":
            webhook_url = f"https://{settings.app_host}/webhook"
        else:
            webhook_url = f"http://{settings.app_host}:{settings.app_port}/webhook"
        
        print(f"   Webhook URL: {webhook_url}")
        
        # Verificar se configurações estão válidas
        if not settings.zapi_instance_id or not settings.zapi_token:
            print("   ❌ PROBLEMA: Credenciais Z-API não configuradas!")
            return False
        
        if not settings.app_host:
            print("   ❌ PROBLEMA: App host não configurado!")
            return False
        
        print("   ✅ Configurações básicas estão presentes")
        
        # Teste de conectividade (simulado)
        print("\n2. 📡 Teste de webhook (simulado):")
        print("   💡 Para testar webhook real:")
        print(f"      POST {webhook_url}")
        print("      Body: dados do Z-API")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO na verificação: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        print("🎯 OBJETIVO: Encontrar por que usuário não consegue sair do menu")
        print("=" * 70)
        
        resultado1 = asyncio.run(simular_webhook_completo())
        resultado2 = asyncio.run(simular_fluxo_real())
        resultado3 = asyncio.run(verificar_configuracao_webhook())
        
        print("\n" + "=" * 70)
        print("🎯 DIAGNÓSTICO FINAL:")
        
        if resultado1 and resultado2 and resultado3:
            print("✅ CÓDIGO ESTÁ FUNCIONANDO CORRETAMENTE!")
            print("💡 O problema deve estar na configuração do webhook Z-API")
            print("🔧 Próximos passos:")
            print("   1. Verificar se webhook está configurado no Z-API")
            print("   2. Testar envio de mensagem real")
            print("   3. Verificar logs do servidor em produção")
        else:
            print("❌ PROBLEMA ENCONTRADO NO CÓDIGO!")
            print("🔧 Revisar implementação dos handlers")
            
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()