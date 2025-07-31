#!/usr/bin/env python3
"""
Verificar e orientar configuração de variáveis no Vercel
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verificar_variaveis_locais():
    print("🔍 VERIFICANDO VARIÁVEIS LOCAIS (para comparar)")
    print("=" * 60)
    
    try:
        from app.config import settings
        
        variaveis_necessarias = {
            "ZAPI_INSTANCE_ID": settings.zapi_instance_id,
            "ZAPI_TOKEN": settings.zapi_token,
            "ZAPI_CLIENT_TOKEN": settings.zapi_client_token,
            "SUPABASE_URL": settings.supabase_url,
            "SUPABASE_ANON_KEY": settings.supabase_anon_key,
            "SUPABASE_SERVICE_ROLE_KEY": settings.supabase_service_role_key,
        }
        
        print("📋 Variáveis encontradas localmente:")
        
        for nome, valor in variaveis_necessarias.items():
            if valor:
                if "TOKEN" in nome or "KEY" in nome:
                    print(f"   ✅ {nome}: {valor[:20]}...")
                else:
                    print(f"   ✅ {nome}: {valor}")
            else:
                print(f"   ❌ {nome}: VAZIO")
        
        # Verificar se todas estão preenchidas
        vazias = [nome for nome, valor in variaveis_necessarias.items() if not valor]
        
        if vazias:
            print(f"\n⚠️ Variáveis vazias: {vazias}")
            return False, variaveis_necessarias
        else:
            print(f"\n✅ Todas as variáveis estão preenchidas localmente!")
            return True, variaveis_necessarias
            
    except Exception as e:
        print(f"❌ Erro ao verificar: {str(e)}")
        return False, {}

def gerar_comandos_vercel(variaveis):
    print("\n\n🔧 COMANDOS PARA CONFIGURAR VERCEL")
    print("=" * 60)
    
    print("1. 📱 Via Vercel CLI (Recomendado):")
    print("   # Instalar Vercel CLI se não tiver:")
    print("   npm install -g vercel")
    print()
    print("   # Configurar cada variável:")
    
    for nome, valor in variaveis.items():
        if valor:
            print(f'   vercel env add {nome} production')
            print(f'   # Cole o valor: {valor}')
            print()
    
    print("2. 🌐 Via Dashboard Vercel:")
    print("   • Acesse: https://vercel.com/dashboard")
    print("   • Vá em seu projeto")
    print("   • Settings → Environment Variables")
    print("   • Add New para cada variável:")
    print()
    
    for nome, valor in variaveis.items():
        if valor:
            if "TOKEN" in nome or "KEY" in nome:
                valor_display = f"{valor[:20]}..."
            else:
                valor_display = valor
            print(f"     {nome} = {valor_display}")
    
    print("\n3. 🚀 Redeploy após configurar:")
    print("   vercel --prod")

def mostrar_instrucoes_teste():
    print("\n\n📱 APÓS CONFIGURAR NO VERCEL")
    print("=" * 60)
    
    print("1. ⏳ Aguardar redeploy completar")
    print("2. 🔧 Executar novamente:")
    print("   python configurar_webhook_final.py")
    print("3. ✅ Se der sucesso, testar WhatsApp:")
    print("   • Envie: 'oi' → Menu")
    print("   • Envie: '1' → 'Digite seu CPF'")

def verificar_arquivo_env():
    print("\n\n📄 VERIFICANDO ARQUIVO .env")
    print("=" * 60)
    
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado")
        
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            print("📋 Conteúdo do .env:")
            for linha in linhas:
                linha = linha.strip()
                if linha and not linha.startswith('#'):
                    if '=' in linha:
                        nome, valor = linha.split('=', 1)
                        if "TOKEN" in nome or "KEY" in nome:
                            print(f"   {nome}={valor[:20]}...")
                        else:
                            print(f"   {nome}={valor}")
            
            print("\n💡 Use estes valores para configurar no Vercel!")
            
        except Exception as e:
            print(f"❌ Erro ao ler .env: {str(e)}")
    
    else:
        print("❌ Arquivo .env não encontrado")
        print("💡 Crie um arquivo .env com suas credenciais")

if __name__ == "__main__":
    print("🔧 CONFIGURAÇÃO DE VARIÁVEIS NO VERCEL")
    print("=" * 70)
    
    # Verificar variáveis locais
    todas_ok, variaveis = verificar_variaveis_locais()
    
    if not todas_ok:
        print("\n❌ Algumas variáveis estão vazias localmente!")
        print("🔧 Configure primeiro localmente, depois no Vercel")
    else:
        # Gerar comandos para Vercel
        gerar_comandos_vercel(variaveis)
    
    # Verificar arquivo .env
    verificar_arquivo_env()
    
    # Instruções finais
    mostrar_instrucoes_teste()
    
    print("\n" + "=" * 70)
    print("🎯 RESUMO:")
    print("1. 📋 Copie as variáveis locais para o Vercel")
    print("2. 🚀 Faça redeploy: vercel --prod")
    print("3. 🔧 Execute: python configurar_webhook_final.py")
    print("4. 📱 Teste no WhatsApp")