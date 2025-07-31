#!/usr/bin/env python3
"""
Debug simples do problema de menu - simula lógica sem banco
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simular uma conversa para testar a lógica
class MockConversation:
    def __init__(self):
        self.state = "inicio"
        self.context = {}
        
class MockDB:
    def commit(self):
        pass

class MockWhatsApp:
    async def send_text(self, phone, message):
        print(f"📱 Enviando: {message[:100]}...")
        
    async def mark_as_read(self, phone, message_id):
        pass

# Simular apenas a lógica do handler de menu
async def test_menu_handler():
    print("🔍 TESTE SIMPLES - Lógica do Menu")
    print("=" * 50)
    
    # Simular dados
    conversa = MockConversation()
    db = MockDB()
    phone = "test"
    
    print("\n1. 🎯 Testando lógica do handler de menu")
    
    # Simular a lógica exata do _handle_menu_principal
    def test_opcao(opcao_input, nome_teste):
        print(f"\n   📝 {nome_teste}: '{opcao_input}'")
        
        opcao = opcao_input.strip()
        print(f"   📋 Opção processada: '{opcao}'")
        
        opcoes = {
            "1": ("agendar", "aguardando_cpf", "Vamos agendar sua consulta!"),
            "2": ("visualizar", "aguardando_cpf", "Para ver seus agendamentos, preciso do seu CPF."),
            "3": ("cancelar", "aguardando_cpf", "Para cancelar uma consulta, preciso do seu CPF."),
            "4": ("lista_espera", "aguardando_cpf", "Vou adicionar você na lista de espera!"),
            "5": (None, None, "FUNÇÃO_CONTATO")
        }
        
        if opcao in opcoes:
            acao, novo_estado, mensagem = opcoes[opcao]
            print(f"   ✅ ENCONTRADO em opcoes!")
            print(f"      - Ação: {acao}")
            print(f"      - Novo estado: {novo_estado}")
            print(f"      - Mensagem: {mensagem[:50]}...")
            
            if callable(mensagem):
                print(f"      🔧 Mensagem é função - chamando...")
                conversa.state = "menu_principal"
            else:
                print(f"      📝 Mensagem é texto - enviando...")
                conversa.state = novo_estado
                conversa.context = {"acao": acao} if acao else {}
            
            print(f"      🎯 Estado final: {conversa.state}")
            print(f"      📋 Contexto final: {conversa.context}")
            return True
        else:
            print(f"   ❌ NÃO ENCONTRADO em opcoes!")
            print(f"      Chaves disponíveis: {list(opcoes.keys())}")
            print(f"      Tipo da opção: {type(opcao)}")
            print(f"      Comparação '1': {opcao == '1'}")
            print(f"      Comparação '2': {opcao == '2'}")
            return False
    
    # Testar diferentes entradas
    test_opcao("1", "Opção 1 (agendar)")
    test_opcao("2", "Opção 2 (visualizar)")  
    test_opcao("3", "Opção 3 (cancelar)")
    test_opcao("4", "Opção 4 (lista)")
    test_opcao("5", "Opção 5 (atendente)")
    test_opcao("6", "Opção inválida 6")
    test_opcao(" 1 ", "Opção 1 com espaços")
    test_opcao("abc", "Texto abc")
    
    print("\n" + "=" * 50)
    print("🎯 CONCLUSÃO:")
    print("Se todas as opções 1-5 mostraram ✅ ENCONTRADO,")
    print("então a lógica do handler está correta.")
    print("O problema deve estar em outro lugar!")

# Testar também comandos globais
def test_comandos_globais():
    print("\n\n🌐 TESTE - Comandos Globais")
    print("=" * 50)
    
    def is_global_command(message):
        commands = ['sair', 'menu', 'ajuda', 'cancelar', '0']
        return message.strip().lower() in commands
    
    # Testar diferentes entradas
    entradas = ['1', '2', '3', '4', '5', 'menu', 'ajuda', '0', 'sair']
    
    for entrada in entradas:
        resultado = is_global_command(entrada)
        print(f"   '{entrada}' -> Global: {resultado}")
        
        if resultado:
            print(f"      ⚠️  '{entrada}' será processado como comando global!")
        else:
            print(f"      ✅ '{entrada}' será processado pelo handler do estado")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_menu_handler())
    test_comandos_globais()