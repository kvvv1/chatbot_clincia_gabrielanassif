#!/usr/bin/env python3
"""
Script para aplicar correção permanente no problema do menu em loop
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def aplicar_correcao_conversation():
    """Aplica correção no arquivo conversation.py"""
    
    print("🔧 APLICANDO CORREÇÃO NO PROBLEMA DO MENU")
    print("=" * 60)
    
    conversation_file = "app/services/conversation.py"
    
    # Ler arquivo atual
    try:
        with open(conversation_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False
    
    print("1. 📖 Arquivo conversation.py lido com sucesso")
    
    # Correção 1: Comandos globais mais específicos
    old_global_command = '''def _is_global_command(self, message: str) -> bool:
        """Verifica se é um comando global"""
        commands = ['sair', 'menu', 'ajuda', 'cancelar', '0']
        message_clean = message.strip().lower()
        
        # Log para debug
        logger.info(f"🔍 Verificando comando global: '{message_clean}'")
        logger.info(f"   - É comando global? {message_clean in commands}")
        
        return message_clean in commands'''
    
    new_global_command = '''def _is_global_command(self, message: str) -> bool:
        """Verifica se é um comando global - VERSÃO CORRIGIDA"""
        # 🔧 CORREÇÃO: Comandos mais específicos para evitar conflitos
        explicit_commands = ['sair', 'menu', 'ajuda', 'cancelar']
        message_clean = message.strip().lower()
        
        # Log para debug
        logger.info(f"🔍 Verificando comando global: '{message_clean}'")
        
        # ✅ CORREÇÃO: Só aceita "0" se estiver explicitamente no menu principal
        is_explicit_command = message_clean in explicit_commands
        is_zero_in_menu = (message_clean == '0' and 
                          hasattr(self, '_last_state') and 
                          self._last_state == "menu_principal")
        
        is_global = is_explicit_command or is_zero_in_menu
        logger.info(f"   - É comando global? {is_global}")
        logger.info(f"   - Comando explícito: {is_explicit_command}")
        logger.info(f"   - Zero no menu: {is_zero_in_menu}")
        
        return is_global'''
    
    if old_global_command in content:
        content = content.replace(old_global_command, new_global_command)
        print("   ✅ Correção 1: Comandos globais mais específicos")
    else:
        print("   ⚠️ Correção 1: Padrão não encontrado, aplicando versão alternativa")
        # Buscar apenas a assinatura da função
        pattern = r'def _is_global_command\(self, message: str\) -> bool:.*?return message_clean in commands'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_global_command.replace('def _is_global_command(self, message: str) -> bool:', '').strip(), content, flags=re.DOTALL)
            print("   ✅ Correção 1: Aplicada via regex")
    
    # Correção 2: Adicionar rastreamento de estado
    process_message_pattern = r'async def processar_mensagem\(self, phone: str, message: str, message_id: str, db: Session\):'
    if re.search(process_message_pattern, content):
        # Adicionar rastreamento de estado
        old_state_line = "estado = conversa.state or \"inicio\""
        new_state_line = '''estado = conversa.state or "inicio"
        # 🔧 CORREÇÃO: Rastrear último estado para comandos globais
        self._last_state = estado'''
        
        if old_state_line in content and new_state_line not in content:
            content = content.replace(old_state_line, new_state_line)
            print("   ✅ Correção 2: Rastreamento de estado adicionado")
    
    # Correção 3: Handler de erro mais robusto
    old_error_handler = '''async def _handle_error(self, phone: str, conversa: Conversation, db: Session):'''
    
    if old_error_handler in content:
        # Procurar o método completo
        start_idx = content.find(old_error_handler)
        if start_idx != -1:
            # Encontrar o final do método (próximo 'async def' ou final do arquivo)
            next_method = content.find('\n    async def ', start_idx + 1)
            if next_method == -1:
                next_method = len(content)
            
            old_method = content[start_idx:next_method]
            
            new_error_handler_method = '''async def _handle_error(self, phone: str, conversa: Conversation, db: Session):
        """Handler de erro mais robusto - NÃO reseta estado automaticamente"""
        logger.error(f"🚨 ERRO durante processamento para {phone}")
        logger.error(f"   Estado atual: {conversa.state}")
        logger.error(f"   Contexto: {conversa.context}")
        
        # 🔧 CORREÇÃO: Não resetar estado automaticamente!
        # Apenas informar erro ao usuário
        await self.whatsapp.send_text(phone, 
            "😔 Ops! Houve um problema temporário.\\n\\n"
            "💡 Você pode continuar de onde parou ou digitar *menu* para recomeçar.")
        
        # Manter estado atual - NÃO resetar!
        logger.info("   ✅ Estado preservado após erro")

'''
            
            content = content.replace(old_method, new_error_handler_method)
            print("   ✅ Correção 3: Handler de erro mais robusto")
    
    # Salvar arquivo corrigido
    try:
        with open(conversation_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n✅ CORREÇÕES APLICADAS COM SUCESSO!")
        print(f"   📁 Arquivo: {conversation_file}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return False

def main():
    print("🎯 CORREÇÃO PERMANENTE DO PROBLEMA DO MENU\n")
    
    if aplicar_correcao_conversation():
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. ✅ Execute: python resetar_meu_estado.py")
        print("   2. ✅ Reinicie a aplicação:")
        print("      - Se local: Ctrl+C e python run.py")
        print("      - Se Vercel: vercel --prod")
        print("   3. ✅ Teste o chatbot normalmente")
        
        print("\n💡 O QUE FOI CORRIGIDO:")
        print("   ✅ Comandos globais mais específicos")
        print("   ✅ Rastreamento de estado melhorado") 
        print("   ✅ Handler de erro que preserva contexto")
        print("   ✅ Evita loops infinitos no menu")
    else:
        print("\n❌ FALHA NA APLICAÇÃO DAS CORREÇÕES")
        print("   📞 Entre em contato para aplicação manual")

if __name__ == "__main__":
    main()