#!/usr/bin/env python3
"""
🔍 VERIFICADOR E RENOVADOR DE TOKENS Z-API
Verifica o status dos tokens atuais e gera novos se necessário
"""

import requests
import json
import os
from datetime import datetime

# Configurações atuais do Z-API
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID", "")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")

def test_current_tokens():
    """Testa os tokens atuais do Z-API"""
    print("🔍 TESTANDO TOKENS ATUAIS DO Z-API...")
    print("=" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT_TOKEN
    }
    
    # Teste 1: Verificar status da instância
    print("📱 Testando status da instância...")
    try:
        url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/status"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status da Instância: {data.get('status', 'N/A')}")
            print(f"   Conectado: {data.get('connected', False)}")
            print(f"   Número: {data.get('number', 'N/A')}")
            print(f"   Token válido: ✅ SIM")
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            print(f"   Token válido: ❌ NÃO")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {str(e)}")
        return False

def test_send_message():
    """Testa envio de mensagem com tokens atuais"""
    print("\n📤 Testando envio de mensagem...")
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT_TOKEN
    }
    
    try:
        url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
        test_data = {
            "phone": "553198600366@c.us",
            "message": f"Teste de token - {datetime.now().strftime('%H:%M:%S')}"
        }
        
        response = requests.post(url, headers=headers, json=test_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Mensagem enviada com sucesso!")
            print(f"   Message ID: {data.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {str(e)}")
        return False

def get_new_tokens():
    """Obtém novos tokens do Z-API"""
    print("\n🔄 GERANDO NOVOS TOKENS...")
    print("=" * 50)
    
    print("⚠️  ATENÇÃO: Para gerar novos tokens, você precisa:")
    print("1. Acessar: https://app.z-api.io/")
    print("2. Fazer login na sua conta")
    print("3. Ir para a instância: VARIABLE_FROM_ENV")
    print("4. Na aba 'Segurança', clicar em 'Renovar Token'")
    print("5. Copiar os novos tokens")
    
    print("\n📋 TOKENS ATUAIS:")
    print(f"Instance ID: {ZAPI_INSTANCE_ID}")
    print(f"Token: {ZAPI_TOKEN}")
    print(f"Client Token: {ZAPI_CLIENT_TOKEN}")
    
    print("\n🔧 Para renovar manualmente:")
    print("1. Acesse o painel Z-API")
    print("2. Vá para sua instância")
    print("3. Clique em 'Segurança'")
    print("4. Clique em 'Renovar Token'")
    print("5. Copie os novos valores")
    
    return None

def update_tokens_in_files(new_token, new_client_token):
    """Atualiza os tokens nos arquivos do projeto"""
    print("\n📝 ATUALIZANDO TOKENS NOS ARQUIVOS...")
    
    files_to_update = [
        "configurar_webhooks_zapi_completo.py",
        "verificar_status_apis.py",
        "verificar_renovar_tokens_zapi.py"
    ]
    
    for filename in files_to_update:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Substituir tokens
                content = content.replace(ZAPI_TOKEN, new_token)
                content = content.replace(ZAPI_CLIENT_TOKEN, new_client_token)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ {filename}: Tokens atualizados")
                
            except Exception as e:
                print(f"❌ Erro ao atualizar {filename}: {str(e)}")

def generate_token_update_script():
    """Gera um script para atualizar tokens facilmente"""
    script_content = f'''#!/usr/bin/env python3
"""
🔄 ATUALIZADOR DE TOKENS Z-API
Script para atualizar tokens facilmente
"""

# Tokens atuais
OLD_TOKEN = "{ZAPI_TOKEN}"
OLD_CLIENT_TOKEN = "{ZAPI_CLIENT_TOKEN}"

# Novos tokens (substitua pelos valores reais)
NEW_TOKEN = "SEU_NOVO_TOKEN_AQUI"
NEW_CLIENT_TOKEN = "SEU_NOVO_CLIENT_TOKEN_AQUI"

def update_tokens():
    """Atualiza os tokens nos arquivos"""
    files_to_update = [
        "configurar_webhooks_zapi_completo.py",
        "verificar_status_apis.py",
        "verificar_renovar_tokens_zapi.py"
    ]
    
    for filename in files_to_update:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir tokens
            content = content.replace(OLD_TOKEN, NEW_TOKEN)
            content = content.replace(OLD_CLIENT_TOKEN, NEW_CLIENT_TOKEN)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ {filename}: Tokens atualizados")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar {filename}: {str(e)}")

if __name__ == "__main__":
    print("🔄 ATUALIZADOR DE TOKENS Z-API")
    print("=" * 40)
    print("⚠️  IMPORTANTE: Edite este arquivo e substitua os tokens antes de executar!")
    print("=" * 40)
    
    # Verificar se os tokens foram atualizados
    if NEW_TOKEN == "SEU_NOVO_TOKEN_AQUI":
        print("❌ ERRO: Você precisa editar este arquivo e colocar os novos tokens!")
        print("1. Abra este arquivo em um editor")
        print("2. Substitua 'SEU_NOVO_TOKEN_AQUI' pelo token real")
        print("3. Substitua 'SEU_NOVO_CLIENT_TOKEN_AQUI' pelo client token real")
        print("4. Execute novamente")
    else:
        update_tokens()
        print("\\n🎉 Tokens atualizados com sucesso!")
'''
    
    with open("atualizar_tokens_zapi.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("✅ Script 'atualizar_tokens_zapi.py' criado!")
    print("   Edite o arquivo e coloque os novos tokens antes de executar")

def main():
    """Função principal"""
    print("🔍 VERIFICADOR E RENOVADOR DE TOKENS Z-API")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🏥 Clínica: Gabriela Nassif")
    print(f"📱 Instance ID: {ZAPI_INSTANCE_ID}")
    print("=" * 60)
    
    # Testar tokens atuais
    status_ok = test_current_tokens()
    send_ok = test_send_message()
    
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 40)
    print(f"Status da Instância: {'✅ OK' if status_ok else '❌ ERRO'}")
    print(f"Envio de Mensagem: {'✅ OK' if send_ok else '❌ ERRO'}")
    
    if status_ok and send_ok:
        print("\n🎉 TOKENS FUNCIONANDO PERFEITAMENTE!")
        print("   Não é necessário renovar os tokens.")
    else:
        print("\n⚠️  TOKENS COM PROBLEMAS!")
        print("   É necessário renovar os tokens.")
        
        # Gerar instruções para renovar
        get_new_tokens()
        generate_token_update_script()
        
        print("\n🔧 PRÓXIMOS PASSOS:")
        print("1. Acesse https://app.z-api.io/")
        print("2. Renove os tokens na sua instância")
        print("3. Edite o arquivo 'atualizar_tokens_zapi.py'")
        print("4. Execute: python atualizar_tokens_zapi.py")
        print("5. Teste novamente com: python verificar_renovar_tokens_zapi.py")

if __name__ == "__main__":
    main() 