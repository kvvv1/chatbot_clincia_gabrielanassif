#!/usr/bin/env python3
"""
Teste Rápido da API Z-API
==========================

Teste simples e rápido para verificar se a API Z-API está funcionando.
Ideal para verificações rápidas antes de usar o sistema.

Uso: python test_zapi_rapido.py
"""

import asyncio
import sys
import os
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.services.whatsapp import WhatsAppService

async def teste_rapido_zapi():
    """Teste rápido da API Z-API"""
    print("🚀 TESTE RÁPIDO Z-API")
    print("=" * 40)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # 1. Verificar configurações
    print("1️⃣ Verificando configurações...")
    config_ok = True
    for var in ['zapi_instance_id', 'zapi_token', 'zapi_client_token']:
        value = getattr(settings, var, None)
        if not value:
            print(f"   ❌ {var}: FALTANDO")
            config_ok = False
        else:
            print(f"   ✅ {var}: Configurado")
    
    if not config_ok:
        print("\n❌ CONFIGURAÇÕES INCOMPLETAS!")
        print("Configure as variáveis de ambiente necessárias.")
        return False
    
    print("   ✅ Todas as configurações estão presentes")
    print()
    
    # 2. Testar status da instância
    print("2️⃣ Verificando status da instância...")
    try:
        whatsapp = WhatsAppService()
        status = await whatsapp.check_status()
        
        if status and status.get('status') == 'connected':
            print("   ✅ Instância conectada e funcionando")
            print(f"   📊 Status: {status.get('status')}")
        else:
            print("   ❌ Instância não está conectada")
            print(f"   📊 Status recebido: {status}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar status: {str(e)}")
        return False
    
    print()
    
    # 3. Testar envio de mensagem simples
    print("3️⃣ Testando envio de mensagem...")
    try:
        test_phone = "+553198600366"  # Telefone da clínica
        test_message = f"🧪 Teste rápido - {datetime.now().strftime('%H:%M:%S')}"
        
        result = await whatsapp.send_text(test_phone, test_message)
        
        if result and result.get('status') == 'success':
            print("   ✅ Mensagem enviada com sucesso!")
            print(f"   📱 Para: {test_phone}")
            print(f"   💬 Mensagem: {test_message}")
        else:
            print("   ❌ Falha ao enviar mensagem")
            print(f"   📊 Resposta: {result}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao enviar mensagem: {str(e)}")
        return False
    
    print()
    print("🎉 TESTE RÁPIDO CONCLUÍDO COM SUCESSO!")
    print("✅ API Z-API está funcionando perfeitamente!")
    return True

async def main():
    """Função principal"""
    try:
        success = await teste_rapido_zapi()
        
        if success:
            print("\n✅ SISTEMA PRONTO PARA USO!")
            sys.exit(0)
        else:
            print("\n❌ PROBLEMAS DETECTADOS!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Teste interrompido")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 