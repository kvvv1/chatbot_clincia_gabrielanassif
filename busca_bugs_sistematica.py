#!/usr/bin/env python3
"""
Busca Sistemática de Bugs - Análise Profunda do Código
"""

import re
from pathlib import Path

def analisar_problemas_cache():
    """Analisa problemas no sistema de cache"""
    print("🔍 ANALISANDO PROBLEMAS DE CACHE")
    print("=" * 50)
    
    with open("app/services/conversation.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    problemas = []
    
    # 1. Cache sem limpeza automática
    if "conversation_cache = {}" in codigo:
        if "del self.conversation_cache[phone]" not in codigo:
            problemas.append("❌ Cache nunca é limpo (memory leak)")
        elif codigo.count("del self.conversation_cache[phone]") == 1:
            problemas.append("⚠️ Cache só é limpo na finalização")
    
    # 2. Cache sem limite de tamanho
    if "conversation_cache" in codigo:
        if "len(self.conversation_cache)" not in codigo:
            problemas.append("❌ Cache sem limite de tamanho")
    
    # 3. Cache sem TTL
    if "conversation_cache" in codigo:
        if "created_at" not in codigo or "expires_at" not in codigo:
            problemas.append("⚠️ Cache sem TTL (Time To Live)")
    
    return problemas

def analisar_problemas_concorrencia():
    """Analisa problemas de concorrência"""
    print("\n🔍 ANALISANDO PROBLEMAS DE CONCORRÊNCIA")
    print("=" * 50)
    
    with open("app/services/conversation.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    problemas = []
    
    # 1. Operações não atômicas
    if "conversa.state =" in codigo and "conversa.context =" in codigo:
        # Contar quantas vezes state e context são modificados sem lock
        state_changes = len(re.findall(r'conversa\.state\s*=', codigo))
        context_changes = len(re.findall(r'conversa\.context\s*=', codigo))
        if state_changes > 10:  # Muitas mudanças de estado
            problemas.append(f"⚠️ {state_changes} mudanças de estado (possível race condition)")
    
    # 2. Cache compartilhado sem lock
    if "self.conversation_cache[phone]" in codigo:
        if "asyncio.Lock" not in codigo and "threading.Lock" not in codigo:
            problemas.append("❌ Cache compartilhado sem sincronização")
    
    return problemas

def analisar_problemas_validacao():
    """Analisa problemas de validação"""
    print("\n🔍 ANALISANDO PROBLEMAS DE VALIDAÇÃO")
    print("=" * 50)
    
    with open("app/services/conversation.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    problemas = []
    
    # 1. Validações que podem falhar silenciosamente
    if "validator.validar_cpf" in codigo:
        if "except:" in codigo.split("validator.validar_cpf")[1].split("\n")[0:5]:
            problemas.append("⚠️ Validação de CPF pode falhar silenciosamente")
    
    # 2. Input não sanitizado
    if "message.strip()" in codigo:
        if "sanitizar_entrada" not in codigo:
            problemas.append("⚠️ Input do usuário não totalmente sanitizado")
    
    # 3. Conversão de tipos perigosa
    if "int(message.strip())" in codigo:
        if "try:" not in codigo or "except ValueError:" not in codigo:
            problemas.append("❌ Conversão int() sem tratamento de erro")
    
    return problemas

def analisar_problemas_estado():
    """Analisa problemas de gerenciamento de estado"""
    print("\n🔍 ANALISANDO PROBLEMAS DE ESTADO")
    print("=" * 50)
    
    with open("app/services/conversation.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    problemas = []
    
    # 1. Estados órfãos
    estados_definidos = re.findall(r'conversa\.state = "([^"]+)"', codigo)
    handlers_definidos = re.findall(r'"([^"]+)": self\._handle_', codigo)
    
    estados_orfaos = set(estados_definidos) - set(handlers_definidos)
    if estados_orfaos:
        problemas.append(f"❌ Estados órfãos sem handler: {list(estados_orfaos)}")
    
    # 2. Contexto inconsistente
    if "conversa.context =" in codigo:
        # Verificar se contexto está sendo preservado adequadamente
        context_resets = len(re.findall(r'conversa\.context\s*=\s*\{\}', codigo))
        if context_resets > 5:
            problemas.append(f"⚠️ Muitos resets de contexto ({context_resets}) - pode perder dados")
    
    return problemas

def analisar_problemas_performance():
    """Analisa problemas de performance"""
    print("\n🔍 ANALISANDO PROBLEMAS DE PERFORMANCE")
    print("=" * 50)
    
    with open("app/services/conversation.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    problemas = []
    
    # 1. Muitos commits de banco
    commits = len(re.findall(r'db\.commit\(\)', codigo))
    if commits > 20:
        problemas.append(f"⚠️ Muitos commits de banco ({commits}) - impacto na performance")
    
    # 2. Operações síncronas em contexto async
    if "await " in codigo:
        # Procurar operações que deveriam ser async mas não são
        sync_operations = re.findall(r'self\.\w+\.\w+\([^)]*\)(?!\s*\.)', codigo)
        if len(sync_operations) > 10:
            problemas.append("⚠️ Possíveis operações síncronas em contexto async")
    
    return problemas

def analisar_problemas_seguranca():
    """Analisa problemas de segurança"""
    print("\n🔍 ANALISANDO PROBLEMAS DE SEGURANÇA")
    print("=" * 50)
    
    with open("app/services/conversation.py", 'r', encoding='utf-8') as f:
        codigo = f.read()
    
    problemas = []
    
    # 1. Logs com dados sensíveis
    if "logger.info" in codigo:
        if "cpf" in codigo.lower():
            problemas.append("⚠️ Possível log de dados sensíveis (CPF)")
    
    # 2. Dados não criptografados no contexto
    if "conversa.context" in codigo and "cpf" in codigo.lower():
        if "encrypt" not in codigo and "hash" not in codigo:
            problemas.append("⚠️ Dados sensíveis podem estar em texto claro")
    
    return problemas

def main():
    """Análise principal de bugs"""
    print("🚀 BUSCA SISTEMÁTICA DE BUGS")
    print("Analisando todas as categorias de problemas...")
    print("")
    
    todos_problemas = []
    
    # Analisar cada categoria
    todos_problemas.extend(analisar_problemas_cache())
    todos_problemas.extend(analisar_problemas_concorrencia())
    todos_problemas.extend(analisar_problemas_validacao())
    todos_problemas.extend(analisar_problemas_estado())
    todos_problemas.extend(analisar_problemas_performance())
    todos_problemas.extend(analisar_problemas_seguranca())
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO DA BUSCA DE BUGS:")
    
    if not todos_problemas:
        print("🎉 NENHUM BUG CRÍTICO ENCONTRADO!")
        print("✅ Código está limpo e robusto")
        return True
    else:
        print(f"🚨 ENCONTRADOS {len(todos_problemas)} PROBLEMAS POTENCIAIS:")
        
        criticos = [p for p in todos_problemas if p.startswith("❌")]
        avisos = [p for p in todos_problemas if p.startswith("⚠️")]
        
        if criticos:
            print(f"\n🚨 CRÍTICOS ({len(criticos)}):")
            for i, problema in enumerate(criticos, 1):
                print(f"   {i}. {problema}")
        
        if avisos:
            print(f"\n⚠️ AVISOS ({len(avisos)}):")
            for i, problema in enumerate(avisos, 1):
                print(f"   {i}. {problema}")
        
        print(f"\n📋 PRIORIDADE:")
        if criticos:
            print("   🔥 CORRIGIR CRÍTICOS PRIMEIRO")
        if avisos:
            print("   📝 Considerar correção dos avisos")
        
        return len(criticos) == 0  # Só considera ok se não tem críticos

if __name__ == "__main__":
    success = main()
    print(f"\n{'✅ STATUS: OK' if success else '❌ STATUS: PRECISA CORREÇÃO'}")