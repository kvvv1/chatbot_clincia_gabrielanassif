#!/usr/bin/env python3
"""
🔄 ATUALIZADOR DE TOKENS Z-API
Script para atualizar tokens facilmente
"""

# Tokens atuais
OLD_TOKEN = "VARIABLE_FROM_ENV"
OLD_CLIENT_TOKEN = "VARIABLE_FROM_ENV"

# Novos tokens (substitua pelos valores reais)
NEW_TOKEN = "VARIABLE_FROM_ENV"  # Mesmo token, já atualizado
NEW_CLIENT_TOKEN = "VARIABLE_FROM_ENV"  # NOVO CLIENT TOKEN

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
        print("\n📝 INSTRUÇÕES:")
        print("1. Abra este arquivo em um editor")
        print("2. Substitua 'SEU_NOVO_TOKEN_AQUI' pelo token real")
        print("3. Substitua 'SEU_NOVO_CLIENT_TOKEN_AQUI' pelo client token real")
        print("4. Execute novamente: python atualizar_tokens_zapi.py")
        print("\n🔧 COMO OBTER NOVOS TOKENS:")
        print("1. Acesse: https://app.z-api.io/")
        print("2. Vá para sua instância: VARIABLE_FROM_ENV")
        print("3. Na aba 'Segurança', clique em 'Renovar Token'")
        print("4. Copie os novos tokens")
    else:
        update_tokens()
        print("\n🎉 Tokens atualizados com sucesso!")
        print("\n🧪 PRÓXIMOS PASSOS:")
        print("1. Teste os novos tokens: python verificar_renovar_tokens_zapi.py")
        print("2. Reconfigure webhooks: python configurar_webhooks_zapi_completo.py")
        print("3. Teste sistema completo: python verificar_status_apis.py") 