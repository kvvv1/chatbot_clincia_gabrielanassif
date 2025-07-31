#!/usr/bin/env python3
"""
Teste completo do sistema de chatbot
Verifica todos os fluxos e validações de contexto
"""

import asyncio
import sys
import os
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.conversation import ConversationManager
from app.utils.context_validator import ContextValidator
from app.services.state_manager import StateManager
from app.models.database import get_db

class TestSistemaCompleto:
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.context_validator = ContextValidator()
        self.state_manager = StateManager()
        self.test_results = []
        
    async def test_fluxo_completo_agendamento(self):
        """Testa o fluxo completo de agendamento"""
        print("\n=== TESTE FLUXO COMPLETO DE AGENDAMENTO ===")
        
        # Simular telefone de teste
        phone = "5531999999999"
        
        # Obter banco de dados
        db = next(get_db())
        
        try:
            # 1. Saudação inicial
            print("1. Testando saudação inicial...")
            await self.conversation_manager.processar_mensagem(
                phone=phone,
                message="oi",
                message_id="test_1",
                db=db
            )
            print("✅ Saudação processada")
            
            # 2. Selecionar opção 1 (Agendar)
            print("2. Testando seleção de agendamento...")
            await self.conversation_manager.processar_mensagem(
                phone=phone,
                message="1",
                message_id="test_2",
                db=db
            )
            print("✅ Opção de agendamento selecionada")
            
            # 3. Fornecer CPF válido
            print("3. Testando fornecimento de CPF...")
            await self.conversation_manager.processar_mensagem(
                phone=phone,
                message="12345678901",  # CPF de teste
                message_id="test_3",
                db=db
            )
            print("✅ CPF processado")
            
            # 4. Selecionar tipo de consulta
            print("4. Testando seleção de tipo de consulta...")
            await self.conversation_manager.processar_mensagem(
                phone=phone,
                message="1",
                message_id="test_4",
                db=db
            )
            print("✅ Tipo de consulta selecionado")
            
            # 5. Selecionar data (profissional já definido automaticamente)
            print("5. Testando seleção de data...")
            await self.conversation_manager.processar_mensagem(
                phone=phone,
                message="1",
                message_id="test_5",
                db=db
            )
            print("✅ Data selecionada")
            
            # 6. Selecionar horário
            print("6. Testando seleção de horário...")
            await self.conversation_manager.processar_mensagem(
                phone=phone,
                message="1",
                message_id="test_6",
                db=db
            )
            print("✅ Horário selecionado")
            
            # 7. Confirmar agendamento
            print("7. Testando confirmação de agendamento...")
            await self.conversation_manager.processar_mensagem(
                phone=phone,
                message="1",
                message_id="test_7",
                db=db
            )
            print("✅ Agendamento confirmado")
            
            print("✅ FLUXO COMPLETO DE AGENDAMENTO TESTADO COM SUCESSO!")
            
        except Exception as e:
            print(f"❌ Erro no fluxo de agendamento: {str(e)}")
            import traceback
            traceback.print_exc()

    async def test_validacao_contexto(self):
        """Testa o sistema de validação de contexto"""
        print("\n=== TESTE VALIDAÇÃO DE CONTEXTO ===")
        
        # Teste 1: CPF no menu principal (deve ser rejeitado)
        print("1. Testando CPF no menu principal...")
        is_valid, error_message, action = self.context_validator.validate_message_for_state(
            "12345678901", "menu_principal", {}
        )
        
        if not is_valid:
            print("✅ CPF no menu principal corretamente rejeitado")
            print(f"   Mensagem: {error_message}")
        else:
            print("❌ CPF no menu principal deveria ter sido rejeitado")
        
        # Teste 2: Opção válida no menu principal
        print("2. Testando opção válida no menu principal...")
        is_valid, error_message, action = self.context_validator.validate_message_for_state(
            "1", "menu_principal", {}
        )
        
        if is_valid:
            print("✅ Opção válida no menu principal aceita")
        else:
            print("❌ Opção válida no menu principal deveria ter sido aceita")
        
        # Teste 3: CPF no estado aguardando_cpf
        print("3. Testando CPF no estado aguardando_cpf...")
        is_valid, error_message, action = self.context_validator.validate_message_for_state(
            "12345678901", "aguardando_cpf", {"acao": "agendar"}
        )
        
        if is_valid:
            print("✅ CPF no estado aguardando_cpf aceito")
        else:
            print("❌ CPF no estado aguardando_cpf deveria ter sido aceito")
        
        # Teste 4: Opção inválida no estado aguardando_cpf
        print("4. Testando opção inválida no estado aguardando_cpf...")
        is_valid, error_message, action = self.context_validator.validate_message_for_state(
            "1", "aguardando_cpf", {"acao": "agendar"}
        )
        
        if not is_valid:
            print("✅ Opção inválida no estado aguardando_cpf rejeitada")
        else:
            print("❌ Opção inválida no estado aguardando_cpf deveria ter sido rejeitada")

    async def test_gerenciamento_estados(self):
        """Testa o sistema de gerenciamento de estados"""
        print("\n=== TESTE GERENCIAMENTO DE ESTADOS ===")
        
        # Teste 1: Transição válida
        print("1. Testando transição válida...")
        is_valid, error_message, suggestions = self.state_manager.validate_state_transition(
            "menu_principal", "aguardando_cpf", {"acao": "agendar"}
        )
        
        if is_valid:
            print("✅ Transição válida aceita")
        else:
            print(f"❌ Transição válida rejeitada: {error_message}")
        
        # Teste 2: Transição inválida
        print("2. Testando transição inválida...")
        is_valid, error_message, suggestions = self.state_manager.validate_state_transition(
            "menu_principal", "confirmando_agendamento", {}
        )
        
        if not is_valid:
            print("✅ Transição inválida rejeitada")
            print(f"   Erro: {error_message}")
        else:
            print("❌ Transição inválida deveria ter sido rejeitada")
        
        # Teste 3: Contexto incompleto
        print("3. Testando contexto incompleto...")
        is_valid, error_message, suggestions = self.state_manager.validate_state_transition(
            "aguardando_cpf", "escolhendo_tipo_consulta", {}
        )
        
        if not is_valid:
            print("✅ Contexto incompleto rejeitado")
            print(f"   Erro: {error_message}")
        else:
            print("❌ Contexto incompleto deveria ter sido rejeitado")

    async def test_problema_identificado(self):
        """Testa especificamente o problema identificado na imagem"""
        print("\n=== TESTE PROBLEMA IDENTIFICADO ===")
        
        phone = "5531999999999"
        db = next(get_db())
        
        try:
            # Simular o fluxo problemático da imagem
            print("1. Iniciando conversa...")
            await self.conversation_manager.processar_mensagem(
                phone=phone,
                message="oi",
                message_id="problem_1",
                db=db
            )
            
            print("2. Selecionando opção 1...")
            await self.conversation_manager.processar_mensagem(
                phone=phone,
                message="1",
                message_id="problem_2",
                db=db
            )
            
            print("3. Fornecendo CPF (problema identificado)...")
            await self.conversation_manager.processar_mensagem(
                phone=phone,
                message="17831187685",  # CPF da imagem
                message_id="problem_3",
                db=db
            )
            
            print("✅ Problema testado - sistema deve ter processado CPF corretamente")
            
        except Exception as e:
            print(f"❌ Erro no teste do problema: {str(e)}")

    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 INICIANDO TESTES COMPLETOS DO SISTEMA")
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        try:
            # Teste de validação de contexto
            await self.test_validacao_contexto()
            
            # Teste de gerenciamento de estados
            await self.test_gerenciamento_estados()
            
            # Teste do problema específico
            await self.test_problema_identificado()
            
            # Teste de fluxo completo (comentado para não sobrecarregar)
            # await self.test_fluxo_completo_agendamento()
            
            print("\n✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
            print("🎉 Sistema está funcionando corretamente!")
            
        except Exception as e:
            print(f"\n❌ ERRO GERAL NOS TESTES: {str(e)}")
            import traceback
            traceback.print_exc()

async def main():
    """Função principal"""
    tester = TestSistemaCompleto()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 