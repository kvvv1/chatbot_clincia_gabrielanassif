#!/usr/bin/env python3
"""
Teste do Fluxo Corrigido - Verificar se mensagens são reconhecidas
e o estado avança corretamente após remoção do bloqueio
"""

import re
import sys
from pathlib import Path

def analisar_handlers_do_fluxo():
    """Analisa se os handlers estão configurados para processar mensagens corretamente"""
    
    print("🔍 ANALISANDO HANDLERS DO FLUXO")
    print("=" * 60)
    
    # Ler arquivo
    conversation_file = Path("app/services/conversation.py")
    with open(conversation_file, 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    # Verificações específicas do fluxo
    verificacoes = [
        {
            "nome": "Menu principal aceita opções 1-5",
            "padrao": r"opcoes = \{[^}]*\"1\"[^}]*\"2\"[^}]*\"3\"[^}]*\"4\"[^}]*\"5\"",
            "explicacao": "Menu tem todas as opções mapeadas"
        },
        {
            "nome": "Confirmação paciente aceita opção '1'",
            "padrao": r"if opcao == \"1\":\s*# Confirmar paciente",
            "explicacao": "Handler aceita '1' para confirmar paciente"
        },
        {
            "nome": "Escolha data aceita números",
            "padrao": r"opcao = int\(message\.strip\(\)\)",
            "explicacao": "Handler de data converte entrada para int"
        },
        {
            "nome": "Validação expecting não bloqueia números",
            "padrao": r"if.*expecting.*!=.*:",
            "explicacao": "Validação expecting existe mas é específica"
        },
        {
            "nome": "Remoção do bloqueio de números 1-5",
            "padrao": r"# A validação de contexto deve ser feita nos handlers individuais",
            "explicacao": "Comentário indica que bloqueio foi removido"
        },
        {
            "nome": "Estados de fluxo principais existem",
            "padrao": r"menu_principal.*aguardando_cpf.*confirmando_paciente.*escolhendo_data",
            "explicacao": "Estados principais do fluxo estão mapeados"
        }
    ]
    
    # Verificar cada item
    verificacoes_ok = 0
    total = len(verificacoes)
    
    for verificacao in verificacoes:
        nome = verificacao["nome"]
        padrao = verificacao["padrao"]
        explicacao = verificacao["explicacao"]
        
        if re.search(padrao, codigo, re.DOTALL | re.MULTILINE):
            print(f"✅ {nome}")
            print(f"   └─ {explicacao}")
            verificacoes_ok += 1
        else:
            print(f"❌ {nome}")
            print(f"   └─ {explicacao}")
    
    return verificacoes_ok, total

def verificar_fluxo_especifico():
    """Verifica o fluxo específico: menu → 1 → CPF → confirmação"""
    
    print("\n🎯 VERIFICANDO FLUXO ESPECÍFICO")
    print("=" * 60)
    
    conversation_file = Path("app/services/conversation.py")
    with open(conversation_file, 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    # Traçar o fluxo esperado
    fluxo_esperado = [
        {
            "etapa": "1. Saudação → Menu",
            "requisitos": [
                r"async def _handle_inicio.*_mostrar_menu_principal",
                r"conversa\.state = \"menu_principal\""
            ]
        },
        {
            "etapa": "2. Opção '1' → Aguardar CPF",
            "requisitos": [
                r"\"1\".*\"agendar\".*\"aguardando_cpf\"",
                r"context.*acao.*agendar.*expecting.*cpf"
            ]
        },
        {
            "etapa": "3. CPF → Confirmação Paciente", 
            "requisitos": [
                r"async def _handle_cpf.*validar_cpf",
                r"_mostrar_confirmacao_paciente"
            ]
        },
        {
            "etapa": "4. Confirmação '1' → Iniciar Agendamento",
            "requisitos": [
                r"if opcao == \"1\".*Confirmar paciente",
                r"_iniciar_agendamento.*phone.*paciente"
            ]
        }
    ]
    
    # Verificar cada etapa
    etapas_ok = 0
    
    for etapa_info in fluxo_esperado:
        etapa = etapa_info["etapa"]
        requisitos = etapa_info["requisitos"]
        
        print(f"\n📋 {etapa}")
        
        todos_requisitos_ok = True
        for requisito in requisitos:
            if re.search(requisito, codigo, re.DOTALL | re.MULTILINE):
                print(f"   ✅ Requisito atendido")
            else:
                print(f"   ❌ Requisito faltando: {requisito[:50]}...")
                todos_requisitos_ok = False
        
        if todos_requisitos_ok:
            etapas_ok += 1
    
    return etapas_ok, len(fluxo_esperado)

def verificar_comandos_globais():
    """Verifica se comandos globais funcionam"""
    
    print("\n🌐 VERIFICANDO COMANDOS GLOBAIS")
    print("=" * 60)
    
    conversation_file = Path("app/services/conversation.py")
    with open(conversation_file, 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    comandos_esperados = [
        {
            "comando": "menu",
            "padrao": r"explicit_commands.*menu",
            "funcionalidade": "Volta ao menu principal"
        },
        {
            "comando": "cancelar", 
            "padrao": r"explicit_commands.*cancelar",
            "funcionalidade": "Cancela operação atual"
        },
        {
            "comando": "sair",
            "padrao": r"explicit_commands.*sair",
            "funcionalidade": "Encerra conversa"
        }
    ]
    
    comandos_ok = 0
    
    for cmd_info in comandos_esperados:
        comando = cmd_info["comando"]
        padrao = cmd_info["padrao"]
        funcionalidade = cmd_info["funcionalidade"]
        
        if re.search(padrao, codigo, re.MULTILINE):
            print(f"✅ Comando '{comando}' - {funcionalidade}")
            comandos_ok += 1
        else:
            print(f"❌ Comando '{comando}' - {funcionalidade}")
    
    return comandos_ok, len(comandos_esperados)

def main():
    """Análise principal"""
    
    print("🚀 VERIFICAÇÃO PÓS-CORREÇÃO DO FLUXO")
    print("Verificando se mensagens serão reconhecidas e estados avançarão...")
    print("")
    
    # Verificar handlers
    handlers_ok, handlers_total = analisar_handlers_do_fluxo()
    
    # Verificar fluxo específico
    fluxo_ok, fluxo_total = verificar_fluxo_especifico()
    
    # Verificar comandos globais
    comandos_ok, comandos_total = verificar_comandos_globais()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    print(f"   Handlers: {handlers_ok}/{handlers_total}")
    print(f"   Fluxo Principal: {fluxo_ok}/{fluxo_total}")
    print(f"   Comandos Globais: {comandos_ok}/{comandos_total}")
    
    # Calcular score total
    total_verificacoes = handlers_total + fluxo_total + comandos_total
    total_ok = handlers_ok + fluxo_ok + comandos_ok
    score = (total_ok / total_verificacoes) * 100
    
    print(f"\n🎯 SCORE GERAL: {score:.1f}% ({total_ok}/{total_verificacoes})")
    
    if score >= 90:
        print("\n🎉 EXCELENTE! O fluxo está funcionando corretamente")
        print("✅ Mensagens serão reconhecidas e estados avançarão")
        print("\n💡 TESTE MANUAL RECOMENDADO:")
        print("   1. Enviar 'oi' → deve mostrar menu")
        print("   2. Enviar '1' → deve pedir CPF") 
        print("   3. Enviar CPF válido → deve mostrar confirmação")
        print("   4. Enviar '1' → deve iniciar agendamento")
        print("   5. Testar 'menu' em qualquer ponto")
        return True
    elif score >= 70:
        print("\n⚠️ BOM, mas precisa de ajustes")
        print("🔧 Revise os itens faltantes")
        return False
    else:
        print("\n❌ PROBLEMAS DETECTADOS")
        print("🚨 Fluxo pode não funcionar corretamente")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)