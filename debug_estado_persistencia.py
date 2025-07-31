#!/usr/bin/env python3
"""
Debug específico para problema de persistência de estado
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_config():
    from app.config import create_fallback_settings
    import app.config as config_module
    config_module.settings = create_fallback_settings()

async def debug_estado_step_by_step():
    print("🔍 DEBUG - PERSISTÊNCIA DE ESTADO PASSO A PASSO")
    print("=" * 60)
    
    setup_config()
    
    from app.services.conversation import ConversationManager
    from app.models.database import get_db, Conversation
    from app.utils.nlu_processor import NLUProcessor
    
    manager = ConversationManager()
    db = next(get_db())
    test_phone = "5531999999999@c.us"
    
    print("1. 🧹 Limpando estado anterior...")
    
    # Para banco Mock, temos que fazer diferente
    if hasattr(db, 'conversations'):
        # Modo Mock - limpar lista
        db.conversations = [c for c in db.conversations if c.get('phone') != test_phone]
        print("   ✅ Estado Mock limpo")
    else:
        # Banco real
        try:
            db.query(Conversation).filter_by(phone=test_phone).delete()
            db.commit()
            print("   ✅ Estado real limpo")
        except:
            print("   ⚠️  Não foi possível limpar (banco mock)")
    
    print("\n2. 📨 Primeira mensagem: 'oi'")
    print("   ⏳ Processando...")
    
    await manager.processar_mensagem(test_phone, "oi", "msg1", db)
    
    # Verificar estado após primeira mensagem
    conversa = manager._get_or_create_conversation(test_phone, db)
    print(f"   📋 Estado após 'oi': {conversa.state}")
    print(f"   📋 Contexto: {conversa.context}")
    print(f"   📋 ID da conversa: {getattr(conversa, 'id', 'Mock')}")
    
    if conversa.state != "menu_principal":
        print(f"   ❌ PROBLEMA: Estado deveria ser 'menu_principal', mas é '{conversa.state}'")
        return False
    
    print("\n3. 📨 Segunda mensagem: '1'")
    print("   🎯 ESTADO ANTES DO PROCESSAMENTO:")
    conversa_antes = manager._get_or_create_conversation(test_phone, db)
    print(f"      Estado: {conversa_antes.state}")
    print(f"      Contexto: {conversa_antes.context}")
    print(f"      ID: {getattr(conversa_antes, 'id', 'Mock')}")
    
    print("   ⏳ Processando mensagem '1'...")
    
    # AQUI ESTÁ O PONTO CRÍTICO - vamos debug passo a passo
    
    # Passo 1: Verificar comandos globais
    is_global = manager._is_global_command("1")
    print(f"   🌐 É comando global? {is_global}")
    
    if is_global:
        print("   ❌ PROBLEMA: '1' foi detectado como comando global!")
        return False
    
    # Passo 2: Simular _process_by_state
    estado = conversa_antes.state or "inicio"
    print(f"   🔧 Estado para processamento: {estado}")
    
    # Passo 3: Verificar se handler existe
    handlers = {
        "inicio": "_handle_inicio",
        "menu_principal": "_handle_menu_principal",
        "aguardando_cpf": "_handle_cpf",
    }
    
    handler_name = handlers.get(estado, "_handle_estado_desconhecido")
    print(f"   🔧 Handler selecionado: {handler_name}")
    
    if handler_name != "_handle_menu_principal":
        print(f"   ❌ PROBLEMA: Handler incorreto para estado '{estado}'")
        return False
    
    # Passo 4: Simular handler menu_principal
    print("   🔧 Simulando _handle_menu_principal...")
    
    opcao = "1".strip()
    opcoes = {
        "1": ("agendar", "aguardando_cpf", "Mensagem de agendamento"),
        "2": ("visualizar", "aguardando_cpf", "Mensagem de visualização"),
        "3": ("cancelar", "aguardando_cpf", "Mensagem de cancelamento"),
        "4": ("lista_espera", "aguardando_cpf", "Mensagem de lista"),
        "5": (None, None, "função_contato")
    }
    
    if opcao in opcoes:
        acao, novo_estado, mensagem = opcoes[opcao]
        print(f"      ✅ Opção '{opcao}' encontrada!")
        print(f"      📋 Ação: {acao}")
        print(f"      📋 Novo estado: {novo_estado}")
        
        # Simular mudança
        conversa_antes.state = novo_estado
        conversa_antes.context = {"acao": acao} if acao else {}
        
        print(f"      🔄 Estado mudado para: {conversa_antes.state}")
        print(f"      📋 Contexto mudado para: {conversa_antes.context}")
        
    else:
        print(f"      ❌ Opção '{opcao}' NÃO encontrada!")
        return False
    
    # Passo 5: Simular commit
    print("   💾 Simulando db.commit()...")
    if hasattr(db, 'commit'):
        db.commit()
        print("      ✅ Commit executado")
    else:
        print("      ⚠️  Banco Mock - commit simulado")
    
    # Agora processar a mensagem real
    print("\n   🚀 Processando mensagem real...")
    await manager.processar_mensagem(test_phone, "1", "msg2", db)
    
    print("   🎯 ESTADO DEPOIS DO PROCESSAMENTO:")
    conversa_depois = manager._get_or_create_conversation(test_phone, db)
    print(f"      Estado: {conversa_depois.state}")
    print(f"      Contexto: {conversa_depois.context}")
    print(f"      ID: {getattr(conversa_depois, 'id', 'Mock')}")
    
    # Verificar resultado
    if conversa_depois.state == "aguardando_cpf" and conversa_depois.context.get("acao") == "agendar":
        print("   🎉 SUCESSO! Estado mudou corretamente!")
        return True
    else:
        print("   ❌ PROBLEMA! Estado não mudou!")
        print(f"      Esperado: state='aguardando_cpf', context={{'acao': 'agendar'}}")
        print(f"      Atual: state='{conversa_depois.state}', context={conversa_depois.context}")
        return False

async def debug_banco_mock():
    print("\n\n🗄️ DEBUG - BANCO MOCK")
    print("=" * 60)
    
    setup_config()
    
    from app.models.database import get_db
    
    db = next(get_db())
    
    print("1. 🔍 Tipo de banco:")
    print(f"   Tipo: {type(db)}")
    print(f"   Métodos: {[m for m in dir(db) if not m.startswith('_')]}")
    
    # Testar operações básicas
    print("\n2. 🧪 Testando operações básicas:")
    
    # Criar conversa teste
    if hasattr(db, 'conversations'):
        print("   📝 Banco Mock detectado")
        
        # Adicionar conversa
        conversa_teste = {
            'id': 1,
            'phone': 'test_phone',
            'state': 'inicio',
            'context': {}
        }
        
        db.conversations.append(conversa_teste)
        print(f"   ✅ Conversa adicionada: {conversa_teste}")
        
        # Buscar conversa
        found = next((c for c in db.conversations if c['phone'] == 'test_phone'), None)
        print(f"   🔍 Conversa encontrada: {found}")
        
        # Modificar conversa
        if found:
            found['state'] = 'menu_principal'
            found['context'] = {'teste': True}
            print(f"   🔄 Conversa modificada: {found}")
            
            # Verificar persistência
            found_again = next((c for c in db.conversations if c['phone'] == 'test_phone'), None)
            print(f"   🔍 Verificação: {found_again}")
            
            if found_again and found_again['state'] == 'menu_principal':
                print("   ✅ Modificação persistida!")
                return True
            else:
                print("   ❌ Modificação NÃO persistida!")
                return False
    else:
        print("   📊 Banco real detectado")
        return True

if __name__ == "__main__":
    import asyncio
    
    try:
        resultado1 = asyncio.run(debug_estado_step_by_step())
        resultado2 = asyncio.run(debug_banco_mock())
        
        print("\n" + "=" * 60)
        print("🎯 DIAGNÓSTICO:")
        
        if not resultado1:
            print("❌ PROBLEMA NO PROCESSAMENTO DE ESTADO!")
            print("🔧 O handler não está sendo chamado ou não está funcionando")
        
        if not resultado2:
            print("❌ PROBLEMA NO BANCO MOCK!")
            print("🔧 As mudanças não estão sendo persistidas")
        
        if resultado1 and resultado2:
            print("✅ AMBOS FUNCIONANDO!")
            print("💡 Problema deve estar em outro lugar")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()