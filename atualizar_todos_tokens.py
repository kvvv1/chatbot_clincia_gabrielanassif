#!/usr/bin/env python3
"""
Script para atualizar todos os ZAPI_CLIENT_TOKEN antigos
"""

import os
import re

def atualizar_tokens_em_arquivos():
    """Atualiza todos os tokens antigos nos arquivos"""
    print("🔧 Atualizando todos os ZAPI_CLIENT_TOKEN antigos...")
    
    # Token antigo e novo
    token_antigo = "VARIABLE_FROM_ENV"
    token_novo = "VARIABLE_FROM_ENV"
    
    # Arquivos para atualizar
    arquivos_para_atualizar = [
        "vercel_env_copy.txt",
        "VERCEL_ENV_CONFIG.md",
        "CONFIGURAR_VARIAVEIS_VERCEL.md",
        "CONFIGURACAO_VERCEL_PASSO_A_PASSO.md",
        "RESOLUCAO_ERRO_VERCEL.md",
        "INSTRUCOES_WEBHOOK.md"
    ]
    
    arquivos_atualizados = 0
    
    for arquivo in arquivos_para_atualizar:
        if os.path.exists(arquivo):
            try:
                # Ler arquivo
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Verificar se contém token antigo
                if token_antigo in conteudo:
                    # Substituir token
                    novo_conteudo = conteudo.replace(token_antigo, token_novo)
                    
                    # Salvar arquivo
                    with open(arquivo, 'w', encoding='utf-8') as f:
                        f.write(novo_conteudo)
                    
                    print(f"✅ {arquivo} - Atualizado")
                    arquivos_atualizados += 1
                else:
                    print(f"⏭️  {arquivo} - Sem token antigo")
            except Exception as e:
                print(f"❌ {arquivo} - Erro: {str(e)}")
        else:
            print(f"⚠️  {arquivo} - Arquivo não encontrado")
    
    print(f"\n📊 Total de arquivos atualizados: {arquivos_atualizados}")
    
    # Verificar se ainda há tokens antigos
    print("\n🔍 Verificando se ainda há tokens antigos...")
    tokens_restantes = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.py', '.md', '.txt', '.json', '.yml', '.yaml')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                        if token_antigo in conteudo:
                            print(f"⚠️  {file_path} - Ainda contém token antigo")
                            tokens_restantes += 1
                except:
                    pass
    
    if tokens_restantes == 0:
        print("✅ Todos os tokens foram atualizados!")
    else:
        print(f"⚠️  {tokens_restantes} arquivos ainda contêm tokens antigos")
    
    return arquivos_atualizados

def verificar_configuracao_atual():
    """Verifica a configuração atual"""
    print("\n🔍 Verificando configuração atual...")
    
    # Verificar arquivo .env
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if 'VARIABLE_FROM_ENV' in conteudo:
                print("✅ .env - Token correto")
            else:
                print("❌ .env - Token incorreto")
    
    # Verificar vercel.env.production
    if os.path.exists('vercel.env.production'):
        with open('vercel.env.production', 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if 'VARIABLE_FROM_ENV' in conteudo:
                print("✅ vercel.env.production - Token correto")
            else:
                print("❌ vercel.env.production - Token incorreto")

if __name__ == "__main__":
    print("🔄 ATUALIZAÇÃO EM MASSA DE TOKENS")
    print("=" * 50)
    
    # Atualizar arquivos
    arquivos_atualizados = atualizar_tokens_em_arquivos()
    
    # Verificar configuração
    verificar_configuracao_atual()
    
    print(f"\n🎉 Processo concluído!")
    print(f"📝 {arquivos_atualizados} arquivos atualizados")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Atualize as variáveis no Vercel")
    print("2. Faça redeploy")
    print("3. Teste o sistema") 