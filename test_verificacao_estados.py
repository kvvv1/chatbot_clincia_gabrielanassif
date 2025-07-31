#!/usr/bin/env python3
"""
Teste Específico para Verificar Estados Inválidos
"""

import asyncio
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.context_validator import ContextValidator
from app.services.state_manager import StateManager

class TestEstadosInvalidos:
    def __init__(self):
        self.context_validator = ContextValidator()
        self.state_manager = StateManager()
        
    def test_estados_invalidos_context_validator(self):
        """Testa estados inválidos no ContextValidator"""
        print("=== TESTE ESTADOS INVÁLIDOS - CONTEXT VALIDATOR ===")
        
        estados_invalidos = [None, "", "   ", "none", "NONE", "estado_inexistente"]
        
        for estado in estados_invalidos:
            print(f"Testando estado: '{estado}'")
            
            is_valid, error_message, action = self.context_validator.validate_message_for_state(
                "teste", estado, {}
            )
            
            if not is_valid:
                print(f"✅ Estado inválido '{estado}' corretamente rejeitado")
                print(f"   Erro: {error_message}")
            else:
                print(f"❌ Estado inválido '{estado}' deveria ter sido rejeitado")
                
            print()

    def test_estados_invalidos_state_manager(self):
        """Testa estados inválidos no StateManager"""
        print("=== TESTE ESTADOS INVÁLIDOS - STATE MANAGER ===")
        
        estados_invalidos = [None, "", "   ", "none", "NONE", "estado_inexistente"]
        
        for estado in estados_invalidos:
            print(f"Testando estado: '{estado}'")
            
            # Testar get_state_info
            state_info = self.state_manager.get_state_info(estado)
            if not state_info.get("valid", False):
                print(f"✅ get_state_info: Estado inválido '{estado}' corretamente rejeitado")
            else:
                print(f"❌ get_state_info: Estado inválido '{estado}' deveria ter sido rejeitado")
            
            # Testar validate_context_for_state
            is_valid, error_message, missing_fields = self.state_manager.validate_context_for_state(estado, {})
            if not is_valid:
                print(f"✅ validate_context: Estado inválido '{estado}' corretamente rejeitado")
                print(f"   Erro: {error_message}")
            else:
                print(f"❌ validate_context: Estado inválido '{estado}' deveria ter sido rejeitado")
            
            # Testar can_transition_to
            is_valid, error_message = self.state_manager.can_transition_to(estado, "inicio")
            if not is_valid:
                print(f"✅ can_transition_to: Estado inválido '{estado}' corretamente rejeitado")
                print(f"   Erro: {error_message}")
            else:
                print(f"❌ can_transition_to: Estado inválido '{estado}' deveria ter sido rejeitado")
                
            print()

    def test_estados_validos(self):
        """Testa estados válidos para garantir que não foram quebrados"""
        print("=== TESTE ESTADOS VÁLIDOS ===")
        
        estados_validos = ["inicio", "menu_principal", "aguardando_cpf", "escolhendo_tipo_consulta"]
        
        for estado in estados_validos:
            print(f"Testando estado válido: '{estado}'")
            
            # Testar ContextValidator
            is_valid, error_message, action = self.context_validator.validate_message_for_state(
                "oi", estado, {}
            )
            if is_valid:
                print(f"✅ ContextValidator: Estado válido '{estado}' aceito")
            else:
                print(f"❌ ContextValidator: Estado válido '{estado}' rejeitado incorretamente")
            
            # Testar StateManager
            state_info = self.state_manager.get_state_info(estado)
            if state_info.get("valid", False):
                print(f"✅ StateManager: Estado válido '{estado}' aceito")
            else:
                print(f"❌ StateManager: Estado válido '{estado}' rejeitado incorretamente")
                
            print()

    def run_all_tests(self):
        """Executa todos os testes"""
        print("🔍 TESTE ESPECÍFICO - ESTADOS INVÁLIDOS")
        print("="*50)
        
        try:
            self.test_estados_invalidos_context_validator()
            self.test_estados_invalidos_state_manager()
            self.test_estados_validos()
            
            print("="*50)
            print("✅ TESTE CONCLUÍDO!")
            
        except Exception as e:
            print(f"❌ ERRO NO TESTE: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Função principal"""
    tester = TestEstadosInvalidos()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 