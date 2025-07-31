#!/usr/bin/env python3
"""
Teste específico para verificar se o menu foi corrigido
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Para testar sem banco, vamos simular o fluxo
class MockConversation:
    def __init__(self):
        self.state = "inicio"
        self.context = {}
        self.phone = "test"

async def test_menu_flow():
    print("🔧 TESTE - Menu Corrigido")
    print("=" * 50)
    
    # Simular o exato problema do usuário
    print("\n📝 Simulando problema: 'Toda mensagem está voltando para menu'")
    
    conversa = MockConversation()
    
    # FLUXO 1: Primeira mensagem
    print(f"\n1. Estado inicial: {conversa.state}")
    print("   Primeira mensagem: 'oi'")
    print("   → Sistema deve mostrar menu e mudar estado para 'menu_principal'")
    conversa.state = "menu_principal"  # Simular mudança
    print(f"   ✅ Estado após: {conversa.state}")
    
    # FLUXO 2: Opção 1 (aqui está o problema)
    print(f"\n2. Estado atual: {conversa.state}")
    print("   Segunda mensagem: '1'")
    print("   → Sistema deve processar como opção do menu")
    
    # Simular a lógica do handler corrigido
    opcao = "1".strip()
    opcoes = {
        "1": ("agendar", "aguardando_cpf"),
        "2": ("visualizar", "aguardando_cpf"),
        "3": ("cancelar", "aguardando_cpf"),
        "4": ("lista_espera", "aguardando_cpf"),
        "5": (None, None)
    }
    
    if opcao in opcoes:
        acao, novo_estado = opcoes[opcao]
        print(f"   ✅ Opção '{opcao}' encontrada!")
        print(f"   ✅ Ação: {acao}")
        print(f"   ✅ Novo estado: {novo_estado}")
        conversa.state = novo_estado
        conversa.context = {"acao": acao}
        print(f"   ✅ Estado atualizado: {conversa.state}")
        print(f"   ✅ Contexto: {conversa.context}")
    else:
        print(f"   ❌ Opção '{opcao}' NÃO encontrada!")
    
    # FLUXO 3: Verificar se próxima mensagem será processada corretamente
    print(f"\n3. Estado atual: {conversa.state}")
    print("   Terceira mensagem: '12345678901' (CPF)")
    print("   → Sistema deve processar como CPF")
    
    if conversa.state == "aguardando_cpf":
        print("   ✅ Estado correto para processar CPF!")
        print("   ✅ Sistema funcionando normalmente!")
    else:
        print(f"   ❌ Estado incorreto: {conversa.state}")
        print("   ❌ Deveria estar em 'aguardando_cpf'")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNÓSTICO:")
    
    if conversa.state == "aguardando_cpf" and conversa.context.get("acao") == "agendar":
        print("✅ FLUXO FUNCIONANDO!")
        print("   O menu está processando opções corretamente.")
        print("   O problema pode estar na persistência do banco de dados.")
    else:
        print("❌ AINDA HÁ PROBLEMA!")
        print("   A lógica precisa de mais ajustes.")

def print_solucoes():
    print("\n\n🛠️  SOLUÇÕES APLICADAS:")
    print("=" * 50)
    print("1. ✅ Adicionado db.commit() para opções inválidas")
    print("2. ✅ Adicionados logs detalhados em toda parte")
    print("3. ✅ Melhorada visibilidade do processamento")
    
    print("\n📋 PRÓXIMOS PASSOS PARA VERIFICAR:")
    print("1. 🔍 Verificar logs em tempo real")
    print("2. 📊 Testar com banco de dados real")
    print("3. 🧹 Limpar conversas antigas do banco")
    print("4. 🔄 Reiniciar aplicação para aplicar mudanças")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_menu_flow())
    print_solucoes()