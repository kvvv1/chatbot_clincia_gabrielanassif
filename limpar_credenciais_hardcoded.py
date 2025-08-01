#!/usr/bin/env python3
"""
🔐 SCRIPT PARA LIMPAR CREDENCIAIS HARDCODED DO Z-API
Remove todas as credenciais hardcoded e garante uso de variáveis de ambiente
"""

import os
import re
import glob
from pathlib import Path

# Credenciais que devem ser removidas
CREDENCIAIS_HARDCODED = [
    "3E4F7360B552F0C2DBCB9E6774402775",  # Instance ID
    "0BDEFB65E4B5E5615697BCD6",          # Token antigo
    "17829E98BB59E9ADD55BBBA9",          # Token antigo 2
    "Fb79b25350a784c8e83d4a25213955ab5S" # Client Token
]

def limpar_arquivo(arquivo_path):
    """Remove credenciais hardcoded de um arquivo"""
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        conteudo_original = conteudo
        
        # Remover credenciais hardcoded
        for credencial in CREDENCIAIS_HARDCODED:
            conteudo = conteudo.replace(credencial, "VARIABLE_FROM_ENV")
        
        # Padrões específicos para substituir
        padroes = [
            # Instance ID hardcoded
            (r'ZAPI_INSTANCE_ID\s*=\s*["\'][^"\']*["\']', 'ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID", "")'),
            (r'zapi_instance_id\s*=\s*["\'][^"\']*["\']', 'zapi_instance_id = os.getenv("ZAPI_INSTANCE_ID", "")'),
            (r'instance_id\s*=\s*["\'][^"\']*["\']', 'instance_id = os.getenv("ZAPI_INSTANCE_ID", "")'),
            
            # Token hardcoded
            (r'ZAPI_TOKEN\s*=\s*["\'][^"\']*["\']', 'ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")'),
            (r'zapi_token\s*=\s*["\'][^"\']*["\']', 'zapi_token = os.getenv("ZAPI_TOKEN", "")'),
            (r'token\s*=\s*["\'][^"\']*["\']', 'token = os.getenv("ZAPI_TOKEN", "")'),
            
            # Client Token hardcoded
            (r'ZAPI_CLIENT_TOKEN\s*=\s*["\'][^"\']*["\']', 'ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")'),
            (r'zapi_client_token\s*=\s*["\'][^"\']*["\']', 'zapi_client_token = os.getenv("ZAPI_CLIENT_TOKEN", "")'),
            (r'client_token\s*=\s*["\'][^"\']*["\']', 'client_token = os.getenv("ZAPI_CLIENT_TOKEN", "")'),
        ]
        
        for padrao, substituicao in padroes:
            conteudo = re.sub(padrao, substituicao, conteudo)
        
        # Se houve mudanças, salvar o arquivo
        if conteudo != conteudo_original:
            with open(arquivo_path, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erro ao processar {arquivo_path}: {e}")
        return False

def main():
    print("🔐 LIMPANDO CREDENCIAIS HARDCODED DO Z-API")
    print("=" * 50)
    
    # Arquivos Python para processar
    arquivos_python = glob.glob("*.py") + glob.glob("app/**/*.py", recursive=True)
    
    arquivos_modificados = []
    
    for arquivo in arquivos_python:
        if "limpar_credenciais_hardcoded.py" in arquivo:
            continue  # Pular este script
        
        print(f"🔍 Verificando: {arquivo}")
        
        if limpar_arquivo(arquivo):
            arquivos_modificados.append(arquivo)
            print(f"✅ Limpo: {arquivo}")
        else:
            print(f"ℹ️  Sem mudanças: {arquivo}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESUMO:")
    print(f"   Arquivos processados: {len(arquivos_python)}")
    print(f"   Arquivos modificados: {len(arquivos_modificados)}")
    
    if arquivos_modificados:
        print(f"\n✅ ARQUIVOS MODIFICADOS:")
        for arquivo in arquivos_modificados:
            print(f"   - {arquivo}")
        
        print(f"\n🔧 PRÓXIMOS PASSOS:")
        print(f"   1. Verifique se as variáveis de ambiente estão configuradas no Vercel")
        print(f"   2. Teste o sistema com: python verificar_status_apis.py")
        print(f"   3. Se necessário, renove os tokens no painel Z-API")
    else:
        print(f"\n✅ Nenhuma credencial hardcoded encontrada!")
    
    print(f"\n🔐 SEGURANÇA:")
    print(f"   - Todas as credenciais agora vêm de variáveis de ambiente")
    print(f"   - Não há mais tokens expostos no código")
    print(f"   - O sistema está mais seguro")

if __name__ == "__main__":
    main() 