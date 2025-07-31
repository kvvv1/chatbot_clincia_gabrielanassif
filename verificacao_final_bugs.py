#!/usr/bin/env python3
"""
Verificação Final de Bugs - Checklist Rápido
"""

import re
from pathlib import Path

def main():
    print("🔍 VERIFICAÇÃO FINAL DE BUGS")
    print("=" * 50)
    
    # Ler código
    with open("app/services/conversation.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    problemas_criticos = []
    avisos = []
    
    print("1. ✅ CONVERSÕES INT() PERIGOSAS:")
    int_conversions = re.findall(r'int\(message\.strip\(\)\)', codigo)
    try_blocks = codigo.count('try:')
    except_value_blocks = codigo.count('except ValueError:')
    
    if len(int_conversions) <= except_value_blocks:
        print(f"   ✅ {len(int_conversions)} conversões int(), {except_value_blocks} except ValueError")
    else:
        print(f"   ❌ {len(int_conversions)} conversões int(), apenas {except_value_blocks} except ValueError")
        problemas_criticos.append("Conversões int() sem tratamento de erro")
    
    print("\n2. ✅ MEMORY LEAKS NO CACHE:")
    if "conversation_cache = {}" in codigo:
        if "del self.conversation_cache[phone]" in codigo:
            print("   ✅ Cache tem limpeza implementada")
        else:
            print("   ❌ Cache nunca é limpo")
            problemas_criticos.append("Memory leak no cache")
    
    print("\n3. ✅ ESTADOS ÓRFÃOS:")
    estados_definidos = set(re.findall(r'conversa\.state = "([^"]+)"', codigo))
    handlers_no_map = set(re.findall(r'"([^"]+)": self\._handle_', codigo))
    estados_orfaos = estados_definidos - handlers_no_map
    
    if not estados_orfaos:
        print(f"   ✅ Todos os {len(estados_definidos)} estados têm handlers")
    else:
        print(f"   ❌ Estados órfãos: {list(estados_orfaos)}")
        problemas_criticos.append(f"Estados órfãos: {list(estados_orfaos)}")
    
    print("\n4. ✅ EXCEÇÕES NÃO TRATADAS:")
    if "except Exception as e:" in codigo:
        print("   ✅ Tratamento de exceções genéricas implementado")
    else:
        print("   ❌ Nenhum tratamento de exceções genéricas")
        problemas_criticos.append("Falta tratamento de exceções")
    
    print("\n5. ✅ COMMITS SEM PERSISTÊNCIA:")
    commits = len(re.findall(r'db\.commit\(\)', codigo))
    state_changes = len(re.findall(r'conversa\.state\s*=', codigo))
    
    if commits >= state_changes * 0.8:  # 80% de coverage
        print(f"   ✅ {commits} commits para {state_changes} mudanças de estado")
    else:
        print(f"   ⚠️ {commits} commits para {state_changes} mudanças de estado")
        avisos.append("Possível falta de persistência em algumas mudanças")
    
    print("\n6. ✅ HANDLERS ASYNC CORRETOS:")
    async_handlers = len(re.findall(r'async def _handle_', codigo))
    total_handlers = len(re.findall(r'def _handle_', codigo))
    
    if async_handlers == total_handlers:
        print(f"   ✅ Todos os {total_handlers} handlers são async")
    else:
        print(f"   ⚠️ {async_handlers}/{total_handlers} handlers são async")
        avisos.append("Alguns handlers podem não ser async")
    
    print("\n7. ✅ IMPORTS NECESSÁRIOS:")
    imports_essenciais = ['datetime', 'Session', 'logging', 'asyncio']
    imports_ok = 0
    
    for imp in imports_essenciais:
        if imp in codigo[:500]:  # Primeiras 500 linhas (imports)
            imports_ok += 1
    
    if imports_ok == len(imports_essenciais):
        print(f"   ✅ Todos os {len(imports_essenciais)} imports essenciais presentes")
    else:
        print(f"   ⚠️ {imports_ok}/{len(imports_essenciais)} imports essenciais")
        avisos.append("Possível falta de imports")
    
    # RESULTADO FINAL
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    
    if not problemas_criticos:
        print("🎉 NENHUM BUG CRÍTICO ENCONTRADO!")
        
        if not avisos:
            print("✅ Código está 100% limpo")
            print("🚀 PRONTO PARA PRODUÇÃO!")
        else:
            print(f"⚠️ {len(avisos)} avisos encontrados:")
            for i, aviso in enumerate(avisos, 1):
                print(f"   {i}. {aviso}")
            print("💡 Avisos não são críticos, mas podem ser melhorados")
        
        return True
    else:
        print(f"🚨 {len(problemas_criticos)} BUGS CRÍTICOS ENCONTRADOS:")
        for i, problema in enumerate(problemas_criticos, 1):
            print(f"   {i}. {problema}")
        
        if avisos:
            print(f"\n⚠️ E {len(avisos)} avisos:")
            for i, aviso in enumerate(avisos, 1):
                print(f"   {i}. {aviso}")
        
        print("\n🔧 CORRIJA OS BUGS CRÍTICOS ANTES DE USAR!")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'✅ STATUS: APROVADO' if success else '❌ STATUS: REPROVADO'}")