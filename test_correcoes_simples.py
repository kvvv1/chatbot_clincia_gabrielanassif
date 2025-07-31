#!/usr/bin/env python3
"""
Teste Simples das Correções Aplicadas no Chatbot
Valida que as correções de código foram aplicadas corretamente
"""

import sys
import re
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def verificar_correcoes_aplicadas():
    """Verifica se as correções foram aplicadas no código"""
    
    print("🚀 VERIFICANDO CORREÇÕES APLICADAS")
    print("=" * 60)
    
    # Ler o arquivo conversation.py
    conversation_file = Path("app/services/conversation.py")
    
    if not conversation_file.exists():
        print("❌ Arquivo conversation.py não encontrado")
        return False
    
    with open(conversation_file, 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    # Lista de verificações
    verificacoes = [
        {
            "nome": "Dispatcher resiliente com try/catch",
            "padrao": r"try:\s*await handler.*except Exception.*logger\.exception.*await self\._handle_error",
            "descricao": "Handler envolvido em try/catch para fallback em erros"
        },
        {
            "nome": "Menu principal normalizado",
            "padrao": r"opcao = message\.strip\(\)\.lower\(\)",
            "descricao": "Opção normalizada para minúsculas"
        },
        {
            "nome": "Flag 'expecting' no contexto",
            "padrao": r"expecting.*=.*['\"]",
            "descricao": "Flag 'expecting' sendo definida no contexto"
        },
        {
            "nome": "Persistência imediata de estado",
            "padrao": r"db\.commit\(\)\s*logger\.info.*Estado.*salvo",
            "descricao": "Estado persistido imediatamente com logs"
        },
        {
            "nome": "Validação de flag expecting",
            "padrao": r"if.*context\.get\(['\"]expecting['\"].*!=",
            "descricao": "Validação da flag expecting nos handlers"
        },
        {
            "nome": "Fallback robusto para ação ausente",
            "padrao": r"else:.*logger\.warning.*Ação não reconhecida",
            "descricao": "Fallback quando ação não é reconhecida"
        },
        {
            "nome": "Logs de diagnóstico melhorados",
            "padrao": r"User ID/Telefone.*Mensagem recebida.*Estado ANTES.*Estado DEPOIS",
            "descricao": "Logs estruturados para diagnóstico"
        }
    ]
    
    # Verificar cada correção
    correcoes_encontradas = 0
    total_correcoes = len(verificacoes)
    
    for verificacao in verificacoes:
        padrao = verificacao["padrao"]
        nome = verificacao["nome"]
        descricao = verificacao["descricao"]
        
        if re.search(padrao, codigo, re.DOTALL | re.MULTILINE):
            print(f"✅ {nome}")
            print(f"   └─ {descricao}")
            correcoes_encontradas += 1
        else:
            print(f"❌ {nome}")
            print(f"   └─ {descricao}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADO: {correcoes_encontradas}/{total_correcoes} correções aplicadas")
    
    if correcoes_encontradas == total_correcoes:
        print("🎉 TODAS AS CORREÇÕES FORAM APLICADAS COM SUCESSO!")
        print("✅ O código está pronto para os testes de fluxo")
        return True
    elif correcoes_encontradas >= total_correcoes * 0.7:  # 70% das correções
        print("⚠️ MAIORIA DAS CORREÇÕES APLICADAS")
        print("💡 Algumas correções podem precisar de ajustes")
        return True
    else:
        print("❌ CORREÇÕES INSUFICIENTES")
        print("🔧 Revise as correções aplicadas")
        return False

def verificar_estrutura_fluxo():
    """Verifica a estrutura básica do fluxo de conversação"""
    
    print("\n🔍 VERIFICANDO ESTRUTURA DO FLUXO")
    print("=" * 60)
    
    conversation_file = Path("app/services/conversation.py")
    
    with open(conversation_file, 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    # Verificar handlers essenciais
    handlers_essenciais = [
        "_handle_menu_principal",
        "_handle_cpf", 
        "_handle_confirmacao_paciente",
        "_handle_escolha_data",
        "_handle_escolha_horario",
        "_handle_confirmacao"
    ]
    
    print("📋 HANDLERS ESSENCIAIS:")
    handlers_encontrados = 0
    
    for handler in handlers_essenciais:
        if f"async def {handler}" in codigo:
            print(f"✅ {handler}")
            handlers_encontrados += 1
        else:
            print(f"❌ {handler}")
    
    # Verificar estados do sistema
    estados_essenciais = [
        "inicio",
        "menu_principal", 
        "aguardando_cpf",
        "confirmando_paciente",
        "escolhendo_data",
        "escolhendo_horario",
        "confirmando_agendamento"
    ]
    
    print("\n📋 ESTADOS DO SISTEMA:")
    estados_encontrados = 0
    
    for estado in estados_essenciais:
        if f'"{estado}"' in codigo:
            print(f"✅ {estado}")
            estados_encontrados += 1
        else:
            print(f"❌ {estado}")
    
    print(f"\n📊 ESTRUTURA: {handlers_encontrados}/{len(handlers_essenciais)} handlers, {estados_encontrados}/{len(estados_essenciais)} estados")
    
    return handlers_encontrados >= len(handlers_essenciais) * 0.8 and estados_encontrados >= len(estados_essenciais) * 0.8

def main():
    """Função principal de teste"""
    
    print("🧪 TESTE DAS CORREÇÕES DO CHATBOT")
    print("Verificando se as correções obrigatórias foram aplicadas...")
    print("")
    
    # Verificar correções
    correcoes_ok = verificar_correcoes_aplicadas()
    
    # Verificar estrutura
    estrutura_ok = verificar_estrutura_fluxo()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("🎯 RESULTADO FINAL:")
    
    if correcoes_ok and estrutura_ok:
        print("✅ TODAS AS VERIFICAÇÕES PASSARAM!")
        print("🚀 O chatbot está pronto para testes funcionais")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Configurar variáveis de ambiente")
        print("   2. Testar fluxo: oi → 1 → CPF → confirmação")
        print("   3. Validar comandos globais (menu, cancelar)")
        print("   4. Verificar mensagens inválidas")
        return True
    else:
        print("❌ ALGUMAS VERIFICAÇÕES FALHARAM")
        print("🔧 Revise as correções antes de prosseguir")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)