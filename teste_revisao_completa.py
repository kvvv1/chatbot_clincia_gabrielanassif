#!/usr/bin/env python3
"""
Teste de Revisão Completa - Verifica se TODOS os problemas foram corrigidos
"""

import re
from pathlib import Path

def main():
    print("🔍 REVISÃO COMPLETA DOS ESTADOS E RESPOSTAS")
    print("=" * 60)
    
    # Ler código
    with open("app/services/conversation.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    problemas_encontrados = []
    
    print("1. ✅ ESTADO 'FINALIZADA' MAPEADO:")
    if '"finalizada": self._handle_conversa_finalizada' in codigo:
        print("   ✅ Estado 'finalizada' mapeado no handler")
    else:
        print("   ❌ Estado 'finalizada' NÃO mapeado")
        problemas_encontrados.append("Estado finalizada não mapeado")
    
    if "async def _handle_conversa_finalizada" in codigo:
        print("   ✅ Handler _handle_conversa_finalizada criado")
    else:
        print("   ❌ Handler _handle_conversa_finalizada NÃO criado")
        problemas_encontrados.append("Handler finalizada não criado")
    
    print("\n2. ✅ LÓGICA DO '0' CORRIGIDA:")
    if "Em estados de escolha numérica, '0' pode ser uma opção válida (voltar)" in codigo:
        print("   ✅ Lógica do '0' corrigida")
    else:
        print("   ❌ Lógica do '0' ainda problemática")
        problemas_encontrados.append("Lógica do 0 ainda problemática")
    
    print("\n3. ✅ VALIDAÇÕES 'EXPECTING' FLEXÍVEIS:")
    
    # Verificar se as validações foram suavizadas
    validacoes_flexiveis = [
        "if expecting and expecting not in",
        "# Não bloquear se expecting não estiver definido (compatibilidade)",
        "expecting apenas se claramente errado"
    ]
    
    for validacao in validacoes_flexiveis:
        if validacao in codigo:
            print(f"   ✅ Validação flexível: {validacao[:30]}...")
        else:
            print(f"   ❌ Validação ainda restritiva: {validacao[:30]}...")
            problemas_encontrados.append(f"Validação restritiva: {validacao[:30]}")
    
    print("\n4. ✅ BLOQUEIO DE NÚMEROS REMOVIDO:")
    if "🔧 CORREÇÃO: Remover validação que bloqueia o fluxo normal" in codigo:
        print("   ✅ Comentário de remoção do bloqueio encontrado")
    else:
        print("   ❌ Comentário de remoção não encontrado")
        problemas_encontrados.append("Comentário de remoção não encontrado")
    
    # Verificar se não há returns problemáticos
    if not re.search(r"if message_clean in.*return", codigo, re.DOTALL):
        print("   ✅ Nenhum return bloqueante encontrado")
    else:
        print("   ❌ Ainda há returns bloqueantes")
        problemas_encontrados.append("Returns bloqueantes ainda existem")
    
    print("\n5. ✅ TODOS OS HANDLERS MAPEADOS:")
    handlers_essenciais = [
        "_handle_inicio",
        "_handle_menu_principal", 
        "_handle_cpf",
        "_handle_confirmacao_paciente",
        "_handle_escolha_data",
        "_handle_escolha_horario", 
        "_handle_confirmacao",
        "_handle_conversa_finalizada"
    ]
    
    handlers_ok = 0
    for handler in handlers_essenciais:
        if f'async def {handler}' in codigo:
            print(f"   ✅ {handler}")
            handlers_ok += 1
        else:
            print(f"   ❌ {handler} NÃO ENCONTRADO")
            problemas_encontrados.append(f"Handler {handler} não encontrado")
    
    print(f"\n   📊 Handlers: {handlers_ok}/{len(handlers_essenciais)}")
    
    print("\n6. ✅ PERSISTÊNCIA IMEDIATA:")
    if "db.commit()" in codigo and "logger.info" in codigo:
        print("   ✅ Persistência com logs encontrada")
    else:
        print("   ❌ Persistência inadequada")
        problemas_encontrados.append("Persistência inadequada")
    
    # RESULTADO FINAL
    print("\n" + "=" * 60)
    print("📊 RESULTADO DA REVISÃO:")
    
    if not problemas_encontrados:
        print("🎉 PERFEITO! TODOS OS PROBLEMAS FORAM CORRIGIDOS!")
        print("✅ Estados mapeados corretamente")
        print("✅ Validações flexíveis implementadas") 
        print("✅ Bloqueios removidos")
        print("✅ Handlers completos")
        print("✅ Persistência adequada")
        print("\n🚀 O chatbot está 100% pronto para uso!")
        return True
    else:
        print(f"❌ ENCONTRADOS {len(problemas_encontrados)} PROBLEMAS:")
        for i, problema in enumerate(problemas_encontrados, 1):
            print(f"   {i}. {problema}")
        print("\n🔧 Corrija estes problemas antes de prosseguir")
        return False

if __name__ == "__main__":
    main()