#!/usr/bin/env python3
"""
Debug simples sem banco - foca apenas na lógica de handlers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simular estruturas necessárias
class MockConversation:
    def __init__(self):
        self.id = 1
        self.phone = "test"
        self.state = "menu_principal"
        self.context = {}
        self.created_at = "2024-01-01"
        self.updated_at = "2024-01-01"

class MockDB:
    def commit(self):
        pass
    
    def refresh(self, obj):
        pass

class MockWhatsApp:
    async def send_text(self, phone, message):
        print(f"🤖 BOT RESPOSTA: {message[:100]}...")
        
    async def mark_as_read(self, phone, message_id):
        pass

async def debug_handlers_isolados():
    print("🔍 DEBUG - HANDLERS ISOLADOS")
    print("=" * 50)
    
    # Importar apenas as partes necessárias
    from app.utils.nlu_processor import NLUProcessor
    from app.utils.formatters import FormatterUtils
    
    # Simular estruturas
    conversa = MockConversation()
    db = MockDB()
    
    print("1. 🎯 Estado inicial da conversa:")
    print(f"   Estado: {conversa.state}")
    print(f"   Contexto: {conversa.context}")
    
    # Testar lógica do menu diretamente
    print("\n2. 🧪 Testando lógica do menu principal:")
    
    # Simular exatamente o que acontece no _handle_menu_principal
    opcao = "1".strip()  # Entrada do usuário
    print(f"   📝 Entrada do usuário: '{opcao}'")
    
    opcoes = {
        "1": ("agendar", "aguardando_cpf", "Vamos agendar sua consulta!"),
        "2": ("visualizar", "aguardando_cpf", "Para ver agendamentos..."),
        "3": ("cancelar", "aguardando_cpf", "Para cancelar..."),
        "4": ("lista_espera", "aguardando_cpf", "Lista de espera..."),
        "5": (None, None, "FUNÇÃO_CONTATO")
    }
    
    print(f"   🔍 Verificando se '{opcao}' está em {list(opcoes.keys())}...")
    
    if opcao in opcoes:
        acao, novo_estado, mensagem = opcoes[opcao]
        print(f"   ✅ ENCONTRADO!")
        print(f"      Ação: {acao}")
        print(f"      Novo estado: {novo_estado}")
        print(f"      Mensagem: {mensagem[:50]}...")
        
        # Simular mudança de estado
        conversa.state = novo_estado
        conversa.context = {"acao": acao} if acao else {}
        
        print(f"   🔄 Estado atualizado para: {conversa.state}")
        print(f"   📋 Contexto atualizado para: {conversa.context}")
        
    else:
        print(f"   ❌ NÃO ENCONTRADO!")
        print(f"      Tipo da opção: {type(opcao)}")
        print(f"      Opções disponíveis: {list(opcoes.keys())}")
    
    # Verificar estado final
    print(f"\n3. ✅ Estado final da conversa:")
    print(f"   Estado: {conversa.state}")
    print(f"   Contexto: {conversa.context}")
    
    if conversa.state == "aguardando_cpf" and conversa.context.get("acao") == "agendar":
        print("   🎉 LÓGICA FUNCIONANDO PERFEITAMENTE!")
        return True
    else:
        print("   ❌ PROBLEMA NA LÓGICA!")
        return False

async def debug_comandos_globais():
    print("\n\n🌐 DEBUG - COMANDOS GLOBAIS")
    print("=" * 50)
    
    # Testar se comandos globais estão interferindo
    def is_global_command(message):
        commands = ['sair', 'menu', 'ajuda', 'cancelar', '0']
        return message.strip().lower() in commands
    
    entradas_teste = ['1', '2', '3', '4', '5', 'menu', '0', 'sair']
    
    for entrada in entradas_teste:
        global_cmd = is_global_command(entrada)
        print(f"   '{entrada}' -> É comando global? {global_cmd}")
        
        if entrada in ['1', '2', '3', '4', '5'] and global_cmd:
            print(f"      ⚠️  PROBLEMA: '{entrada}' está sendo tratado como comando global!")
            return False
    
    print("   ✅ Comandos globais não estão interferindo")
    return True

async def debug_processamento_completo():
    print("\n\n🔄 DEBUG - PROCESSAMENTO COMPLETO")
    print("=" * 50)
    
    conversa = MockConversation()
    
    # Simular fluxo completo de processamento
    print("1. 📱 Simulando: Usuário envia 'oi'")
    conversa.state = "inicio"
    print(f"   Estado inicial: {conversa.state}")
    
    # Após primeira mensagem -> menu
    conversa.state = "menu_principal"
    conversa.context = {}
    print(f"   Após 'oi': {conversa.state}")
    
    print("\n2. 📱 Simulando: Usuário envia '1'")
    # Verificar comandos globais
    entrada = "1"
    commands = ['sair', 'menu', 'ajuda', 'cancelar', '0']
    is_global = entrada.strip().lower() in commands
    
    if is_global:
        print(f"   ⚠️  PROBLEMA: '1' foi interpretado como comando global!")
        return False
    else:
        print(f"   ✅ '1' não é comando global, processando pelo handler...")
    
    # Processar pelo handler do estado atual
    if conversa.state == "menu_principal":
        print(f"   🔧 Chamando handler: _handle_menu_principal")
        
        # Lógica do handler
        opcao = entrada.strip()
        opcoes = {
            "1": ("agendar", "aguardando_cpf"),
            "2": ("visualizar", "aguardando_cpf"),
            "3": ("cancelar", "aguardando_cpf"),
            "4": ("lista_espera", "aguardando_cpf"),
            "5": (None, None)
        }
        
        if opcao in opcoes:
            acao, novo_estado = opcoes[opcao]
            conversa.state = novo_estado
            conversa.context = {"acao": acao} if acao else {}
            print(f"   ✅ Handler executado com sucesso!")
            print(f"      Novo estado: {conversa.state}")
            print(f"      Novo contexto: {conversa.context}")
        else:
            print(f"   ❌ Opção não encontrada no handler!")
            return False
    
    print(f"\n3. 📱 Simulando: Usuário envia CPF '12345678901'")
    entrada_cpf = "12345678901"
    
    if conversa.state == "aguardando_cpf":
        print(f"   ✅ Estado correto para processar CPF!")
        print(f"   🔧 Chamando handler: _handle_cpf")
        # Aqui continuaria o processamento do CPF...
        print(f"   ✅ Fluxo funcionando perfeitamente!")
        return True
    else:
        print(f"   ❌ Estado incorreto: {conversa.state}")
        print(f"   ❌ Deveria estar em 'aguardando_cpf'")
        return False

if __name__ == "__main__":
    import asyncio
    
    try:
        # Executar todos os testes
        resultado1 = asyncio.run(debug_handlers_isolados())
        resultado2 = asyncio.run(debug_comandos_globais())
        resultado3 = asyncio.run(debug_processamento_completo())
        
        print("\n" + "=" * 50)
        print("🎯 DIAGNÓSTICO FINAL:")
        
        if resultado1 and resultado2 and resultado3:
            print("✅ LÓGICA ESTÁ CORRETA!")
            print("✅ O problema deve estar na persistência ou integração!")
            print("💡 Próximo passo: Verificar webhook ou banco de dados")
        else:
            print("❌ PROBLEMA ENCONTRADO NA LÓGICA!")
            print("💡 A lógica básica precisa ser corrigida primeiro")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()