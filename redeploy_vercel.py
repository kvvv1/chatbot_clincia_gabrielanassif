#!/usr/bin/env python3
"""
Script para fazer redeploy no Vercel com configurações atualizadas
"""

import subprocess
import os
import time

def redeploy_vercel():
    """Faz redeploy no Vercel com configurações atualizadas"""
    print("🚀 Fazendo redeploy no Vercel...")
    
    try:
        # Verificar se o Vercel CLI está instalado
        print("1. Verificando Vercel CLI...")
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Vercel CLI não encontrado!")
            print("🔧 Instale com: npm i -g vercel")
            return False
        
        print(f"✅ Vercel CLI encontrado: {result.stdout.strip()}")
        
        # Fazer login no Vercel (se necessário)
        print("\n2. Verificando login no Vercel...")
        result = subprocess.run(['vercel', 'whoami'], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("⚠️ Não logado no Vercel. Fazendo login...")
            subprocess.run(['vercel', 'login'], check=True)
        else:
            print(f"✅ Logado como: {result.stdout.strip()}")
        
        # Fazer deploy
        print("\n3. Fazendo deploy...")
        print("⏳ Isso pode levar alguns minutos...")
        
        # Usar as configurações do arquivo vercel.env.production
        env_file = "vercel.env.production"
        if os.path.exists(env_file):
            print(f"📝 Usando arquivo de ambiente: {env_file}")
        
        result = subprocess.run([
            'vercel', 
            '--prod',
            '--yes'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Deploy realizado com sucesso!")
            print("📊 Logs do deploy:")
            print(result.stdout)
            
            # Extrair URL do deploy
            for line in result.stdout.split('\n'):
                if 'https://' in line and 'vercel.app' in line:
                    print(f"🌐 URL do deploy: {line.strip()}")
                    break
            
            return True
        else:
            print("❌ Erro no deploy:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro durante deploy: {str(e)}")
        return False

def verificar_deploy():
    """Verifica se o deploy está funcionando"""
    print("\n4. Verificando deploy...")
    
    try:
        import requests
        
        # Aguardar um pouco para o deploy finalizar
        print("⏳ Aguardando deploy finalizar...")
        time.sleep(30)
        
        # Testar endpoint
        response = requests.get("https://chatbot-clincia.vercel.app/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Deploy funcionando!")
            return True
        else:
            print(f"❌ Deploy com problema: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar deploy: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🔄 REDEPLOY NO VERCEL")
    print("=" * 50)
    
    # Fazer redeploy
    success = redeploy_vercel()
    
    if success:
        # Verificar deploy
        verificar_deploy()
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Aguarde alguns minutos para o deploy finalizar")
        print("2. Teste enviando uma mensagem no WhatsApp")
        print("3. Execute: python test_complete_system.py")
        print("4. Verifique os logs no Vercel")
    else:
        print("\n❌ Deploy falhou!")
        print("🔧 Verifique os erros acima")

if __name__ == "__main__":
    main() 