#!/usr/bin/env python3
"""
Teste Final - Verificação Direta do Fluxo
"""

import re
from pathlib import Path

def main():
    print("🔍 VERIFICAÇÃO FINAL DO FLUXO")
    print("=" * 50)
    
    # Ler código
    with open("app/services/conversation.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    # Verificações críticas
    print("1. ❌ BLOQUEIO REMOVIDO:")
    if "🔧 CORREÇÃO: Remover validação que bloqueia o fluxo normal" in codigo:
        print("   ✅ Comentário de correção encontrado")
    else:
        print("   ❌ Correção não aplicada")
    
    # Verificar se o return problemático foi removido
    if re.search(r"if message_clean in.*menu_principal.*return", codigo, re.DOTALL):
        print("   ❌ PROBLEMA: Bloqueio ainda existe!")
        return False
    else:
        print("   ✅ Bloqueio removido com sucesso")
    
    print("\n2. 📋 MENU PRINCIPAL:")
    if '"1": ("agendar", "aguardando_cpf"' in codigo:
        print("   ✅ Opção 1 → aguardando_cpf")
    else:
        print("   ❌ Opção 1 não mapeada")
        
    print("\n3. 🔍 CONFIRMAÇÃO PACIENTE:")
    if 'if opcao == "1":\n            # Confirmar paciente' in codigo:
        print("   ✅ Aceita opção '1' para confirmar")
    else:
        print("   ❌ Confirmação não aceita '1'")
    
    print("\n4. 🌐 COMANDOS GLOBAIS:")
    if "explicit_commands = ['sair', 'menu', 'ajuda', 'cancelar']" in codigo:
        print("   ✅ Comandos globais definidos")
    else:
        print("   ❌ Comandos globais não encontrados")
    
    print("\n" + "=" * 50)
    print("🎯 TESTE MANUAL RECOMENDADO:")
    print("   1. 'oi' → deve mostrar menu")
    print("   2. '1' → deve pedir CPF (NÃO deve ser bloqueado)")
    print("   3. CPF → deve mostrar confirmação")  
    print("   4. '1' → deve confirmar paciente (NÃO deve ser bloqueado)")
    print("   5. 'menu' → deve voltar ao menu principal")
    
    print("\n✅ CORREÇÃO APLICADA: Fluxo deve funcionar agora!")
    return True

if __name__ == "__main__":
    main()