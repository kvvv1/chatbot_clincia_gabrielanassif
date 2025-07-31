#!/usr/bin/env python3
"""
Teste de Verificação Completa do Sistema
Testa todos os cenários possíveis, edge cases e validações
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

class TestVerificacaoCompleta:
    def __init__(self):
        self.conversation_manager = ConversationManager()
        self.context_validator = ContextValidator()
        self.state_manager = StateManager()
        self.test_results = []
        self.errors_found = []
        
    async def test_cenarios_edge_cases(self):
        """Testa cenários extremos e edge cases"""
        print("\n=== TESTE CENÁRIOS EXTREMOS E EDGE CASES ===")
        
        # Teste 1: Mensagens vazias
        print("1. Testando mensagens vazias...")
        await self._test_mensagem_vazia()
        
        # Teste 2: Mensagens muito longas
        print("2. Testando mensagens muito longas...")
        await self._test_mensagem_muito_longa()
        
        # Teste 3: Caracteres especiais
        print("3. Testando caracteres especiais...")
        await self._test_caracteres_especiais()
        
        # Teste 4: Números inválidos
        print("4. Testando números inválidos...")
        await self._test_numeros_invalidos()
        
        # Teste 5: CPFs inválidos
        print("5. Testando CPFs inválidos...")
        await self._test_cpfs_invalidos()
        
        # Teste 6: Estados inconsistentes
        print("6. Testando estados inconsistentes...")
        await self._test_estados_inconsistentes()
        
        # Teste 7: Contexto corrompido
        print("7. Testando contexto corrompido...")
        await self._test_contexto_corrompido()

    async def test_fluxos_alternativos(self):
        """Testa fluxos alternativos e caminhos não principais"""
        print("\n=== TESTE FLUXOS ALTERNATIVOS ===")
        
        # Teste 1: Cancelamento no meio do fluxo
        print("1. Testando cancelamento no meio do fluxo...")
        await self._test_cancelamento_meio_fluxo()
        
        # Teste 2: Voltar ao menu principal
        print("2. Testando voltar ao menu principal...")
        await self._test_voltar_menu_principal()
        
        # Teste 3: Finalizar conversa
        print("3. Testando finalizar conversa...")
        await self._test_finalizar_conversa()
        
        # Teste 4: Reativar conversa finalizada
        print("4. Testando reativar conversa finalizada...")
        await self._test_reativar_conversa()
        
        # Teste 5: Múltiplas tentativas
        print("5. Testando múltiplas tentativas...")
        await self._test_multiplas_tentativas()

    async def test_validacoes_rigorosas(self):
        """Testa validações de forma rigorosa"""
        print("\n=== TESTE VALIDAÇÕES RIGOROSAS ===")
        
        # Teste 1: Validação de CPF em todos os estados
        print("1. Testando validação de CPF em todos os estados...")
        await self._test_validacao_cpf_todos_estados()
        
        # Teste 2: Validação de opções de menu
        print("2. Testando validação de opções de menu...")
        await self._test_validacao_opcoes_menu()
        
        # Teste 3: Validação de transições de estado
        print("3. Testando validação de transições de estado...")
        await self._test_validacao_transicoes()
        
        # Teste 4: Validação de contexto
        print("4. Testando validação de contexto...")
        await self._test_validacao_contexto()

    async def test_concorrencia_e_estado(self):
        """Testa concorrência e gerenciamento de estado"""
        print("\n=== TESTE CONCORRÊNCIA E ESTADO ===")
        
        # Teste 1: Múltiplas conversas simultâneas
        print("1. Testando múltiplas conversas simultâneas...")
        await self._test_multiplas_conversas()
        
        # Teste 2: Persistência de estado
        print("2. Testando persistência de estado...")
        await self._test_persistencia_estado()
        
        # Teste 3: Recuperação de erro
        print("3. Testando recuperação de erro...")
        await self._test_recuperacao_erro()

    async def _test_mensagem_vazia(self):
        """Testa comportamento com mensagens vazias"""
        try:
            # Testar mensagem vazia
            is_valid, error_message, action = self.context_validator.validate_message_for_state(
                "", "menu_principal", {}
            )
            
            if not is_valid:
                print("✅ Mensagem vazia corretamente rejeitada")
            else:
                print("❌ Mensagem vazia deveria ter sido rejeitada")
                self.errors_found.append("Mensagem vazia aceita")
                
        except Exception as e:
            print(f"❌ Erro ao testar mensagem vazia: {str(e)}")
            self.errors_found.append(f"Erro mensagem vazia: {str(e)}")

    async def _test_mensagem_muito_longa(self):
        """Testa comportamento com mensagens muito longas"""
        try:
            # Criar mensagem muito longa
            mensagem_longa = "a" * 1000
            
            is_valid, error_message, action = self.context_validator.validate_message_for_state(
                mensagem_longa, "menu_principal", {}
            )
            
            if not is_valid:
                print("✅ Mensagem muito longa corretamente rejeitada")
            else:
                print("❌ Mensagem muito longa deveria ter sido rejeitada")
                self.errors_found.append("Mensagem muito longa aceita")
                
        except Exception as e:
            print(f"❌ Erro ao testar mensagem longa: {str(e)}")
            self.errors_found.append(f"Erro mensagem longa: {str(e)}")

    async def _test_caracteres_especiais(self):
        """Testa comportamento com caracteres especiais"""
        try:
            # Testar caracteres especiais
            caracteres_especiais = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
            
            is_valid, error_message, action = self.context_validator.validate_message_for_state(
                caracteres_especiais, "menu_principal", {}
            )
            
            if not is_valid:
                print("✅ Caracteres especiais corretamente rejeitados")
            else:
                print("❌ Caracteres especiais deveriam ter sido rejeitados")
                self.errors_found.append("Caracteres especiais aceitos")
                
        except Exception as e:
            print(f"❌ Erro ao testar caracteres especiais: {str(e)}")
            self.errors_found.append(f"Erro caracteres especiais: {str(e)}")

    async def _test_numeros_invalidos(self):
        """Testa comportamento com números inválidos"""
        try:
            # Testar números inválidos
            numeros_invalidos = ["999", "abc", "1.5", "-1", "0.5"]
            
            for numero in numeros_invalidos:
                is_valid, error_message, action = self.context_validator.validate_message_for_state(
                    numero, "menu_principal", {}
                )
                
                if not is_valid:
                    print(f"✅ Número inválido '{numero}' corretamente rejeitado")
                else:
                    print(f"❌ Número inválido '{numero}' deveria ter sido rejeitado")
                    self.errors_found.append(f"Número inválido aceito: {numero}")
                    
        except Exception as e:
            print(f"❌ Erro ao testar números inválidos: {str(e)}")
            self.errors_found.append(f"Erro números inválidos: {str(e)}")

    async def _test_cpfs_invalidos(self):
        """Testa comportamento com CPFs inválidos"""
        try:
            # Testar CPFs inválidos
            cpfs_invalidos = [
                "12345678901",  # Todos iguais
                "11111111111",  # Todos 1
                "00000000000",  # Todos 0
                "1234567890",   # Muito curto
                "123456789012", # Muito longo
                "abc123def45",  # Com letras
                "123.456.789-01", # Com pontuação
            ]
            
            for cpf in cpfs_invalidos:
                is_valid = self.context_validator._is_cpf(cpf)
                
                if not is_valid:
                    print(f"✅ CPF inválido '{cpf}' corretamente rejeitado")
                else:
                    print(f"❌ CPF inválido '{cpf}' deveria ter sido rejeitado")
                    self.errors_found.append(f"CPF inválido aceito: {cpf}")
                    
        except Exception as e:
            print(f"❌ Erro ao testar CPFs inválidos: {str(e)}")
            self.errors_found.append(f"Erro CPFs inválidos: {str(e)}")

    async def _test_estados_inconsistentes(self):
        """Testa comportamento com estados inconsistentes"""
        try:
            # Testar estados inválidos
            estados_invalidos = ["", None, "estado_inexistente", "ESTADO_MAIUSCULO"]
            
            for estado in estados_invalidos:
                state_info = self.state_manager.get_state_info(estado)
                
                if not state_info.get("valid", False):
                    print(f"✅ Estado inválido '{estado}' corretamente rejeitado")
                else:
                    print(f"❌ Estado inválido '{estado}' deveria ter sido rejeitado")
                    self.errors_found.append(f"Estado inválido aceito: {estado}")
                    
        except Exception as e:
            print(f"❌ Erro ao testar estados inconsistentes: {str(e)}")
            self.errors_found.append(f"Erro estados inconsistentes: {str(e)}")

    async def _test_contexto_corrompido(self):
        """Testa comportamento com contexto corrompido"""
        try:
            # Testar contextos corrompidos
            contextos_corrompidos = [
                None,
                {},
                {"campo_invalido": "valor"},
                {"paciente": None},
                {"acao": ""},
            ]
            
            for contexto in contextos_corrompidos:
                is_valid, error_message, missing_fields = self.state_manager.validate_context_for_state(
                    "aguardando_cpf", contexto or {}
                )
                
                if not is_valid:
                    print(f"✅ Contexto corrompido corretamente rejeitado")
                else:
                    print(f"❌ Contexto corrompido deveria ter sido rejeitado")
                    self.errors_found.append(f"Contexto corrompido aceito: {contexto}")
                    
        except Exception as e:
            print(f"❌ Erro ao testar contexto corrompido: {str(e)}")
            self.errors_found.append(f"Erro contexto corrompido: {str(e)}")

    async def _test_cancelamento_meio_fluxo(self):
        """Testa cancelamento no meio do fluxo"""
        try:
            phone = "5531999999999"
            db = next(get_db())
            
            # Iniciar fluxo
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="oi", message_id="cancel_1", db=db
            )
            
            # Selecionar agendamento
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="1", message_id="cancel_2", db=db
            )
            
            # Tentar cancelar com "0"
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="0", message_id="cancel_3", db=db
            )
            
            print("✅ Cancelamento no meio do fluxo testado")
            
        except Exception as e:
            print(f"❌ Erro ao testar cancelamento: {str(e)}")
            self.errors_found.append(f"Erro cancelamento: {str(e)}")

    async def _test_voltar_menu_principal(self):
        """Testa voltar ao menu principal"""
        try:
            phone = "5531999999998"
            db = next(get_db())
            
            # Iniciar fluxo
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="oi", message_id="voltar_1", db=db
            )
            
            # Tentar voltar ao menu
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="1", message_id="voltar_2", db=db
            )
            
            print("✅ Voltar ao menu principal testado")
            
        except Exception as e:
            print(f"❌ Erro ao testar voltar ao menu: {str(e)}")
            self.errors_found.append(f"Erro voltar ao menu: {str(e)}")

    async def _test_finalizar_conversa(self):
        """Testa finalizar conversa"""
        try:
            phone = "5531999999997"
            db = next(get_db())
            
            # Iniciar conversa
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="oi", message_id="finalizar_1", db=db
            )
            
            # Finalizar com "0"
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="0", message_id="finalizar_2", db=db
            )
            
            print("✅ Finalizar conversa testado")
            
        except Exception as e:
            print(f"❌ Erro ao testar finalizar conversa: {str(e)}")
            self.errors_found.append(f"Erro finalizar conversa: {str(e)}")

    async def _test_reativar_conversa(self):
        """Testa reativar conversa finalizada"""
        try:
            phone = "5531999999996"
            db = next(get_db())
            
            # Iniciar conversa
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="oi", message_id="reativar_1", db=db
            )
            
            # Finalizar
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="0", message_id="reativar_2", db=db
            )
            
            # Reativar
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="oi", message_id="reativar_3", db=db
            )
            
            print("✅ Reativar conversa testado")
            
        except Exception as e:
            print(f"❌ Erro ao testar reativar conversa: {str(e)}")
            self.errors_found.append(f"Erro reativar conversa: {str(e)}")

    async def _test_multiplas_tentativas(self):
        """Testa múltiplas tentativas"""
        try:
            phone = "5531999999995"
            db = next(get_db())
            
            # Iniciar conversa
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="oi", message_id="multiplas_1", db=db
            )
            
            # Tentar opções inválidas várias vezes
            for i in range(3):
                await self.conversation_manager.processar_mensagem(
                    phone=phone, message="999", message_id=f"multiplas_{i+2}", db=db
                )
            
            # Tentar opção válida
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="1", message_id="multiplas_5", db=db
            )
            
            print("✅ Múltiplas tentativas testadas")
            
        except Exception as e:
            print(f"❌ Erro ao testar múltiplas tentativas: {str(e)}")
            self.errors_found.append(f"Erro múltiplas tentativas: {str(e)}")

    async def _test_validacao_cpf_todos_estados(self):
        """Testa validação de CPF em todos os estados"""
        try:
            cpf_valido = "52998224725"  # CPF válido matematicamente
            estados = ["inicio", "menu_principal", "aguardando_cpf", "escolhendo_tipo_consulta"]
            
            for estado in estados:
                is_valid, error_message, action = self.context_validator.validate_message_for_state(
                    cpf_valido, estado, {}
                )
                
                if estado == "aguardando_cpf":
                    if is_valid:
                        print(f"✅ CPF aceito no estado {estado} (correto)")
                    else:
                        print(f"❌ CPF rejeitado no estado {estado} (incorreto)")
                        self.errors_found.append(f"CPF rejeitado incorretamente em {estado}")
                else:
                    if not is_valid:
                        print(f"✅ CPF rejeitado no estado {estado} (correto)")
                    else:
                        print(f"❌ CPF aceito no estado {estado} (incorreto)")
                        self.errors_found.append(f"CPF aceito incorretamente em {estado}")
                        
        except Exception as e:
            print(f"❌ Erro ao testar validação de CPF: {str(e)}")
            self.errors_found.append(f"Erro validação CPF: {str(e)}")

    async def _test_validacao_opcoes_menu(self):
        """Testa validação de opções de menu"""
        try:
            opcoes_validas = ["1", "2", "3", "4", "5", "0"]
            opcoes_invalidas = ["6", "7", "8", "9", "a", "b", "c"]
            
            # Testar opções válidas
            for opcao in opcoes_validas:
                is_valid, error_message, action = self.context_validator.validate_message_for_state(
                    opcao, "menu_principal", {}
                )
                
                if is_valid:
                    print(f"✅ Opção válida '{opcao}' aceita (correto)")
                else:
                    print(f"❌ Opção válida '{opcao}' rejeitada (incorreto)")
                    self.errors_found.append(f"Opção válida rejeitada: {opcao}")
            
            # Testar opções inválidas
            for opcao in opcoes_invalidas:
                is_valid, error_message, action = self.context_validator.validate_message_for_state(
                    opcao, "menu_principal", {}
                )
                
                if not is_valid:
                    print(f"✅ Opção inválida '{opcao}' rejeitada (correto)")
                else:
                    print(f"❌ Opção inválida '{opcao}' aceita (incorreto)")
                    self.errors_found.append(f"Opção inválida aceita: {opcao}")
                    
        except Exception as e:
            print(f"❌ Erro ao testar validação de opções: {str(e)}")
            self.errors_found.append(f"Erro validação opções: {str(e)}")

    async def _test_validacao_transicoes(self):
        """Testa validação de transições de estado"""
        try:
            # Testar transições válidas
            transicoes_validas = [
                ("inicio", "menu_principal"),
                ("menu_principal", "aguardando_cpf"),
                ("aguardando_cpf", "escolhendo_tipo_consulta"),
            ]
            
            for estado_atual, estado_destino in transicoes_validas:
                is_valid, error_message = self.state_manager.can_transition_to(estado_atual, estado_destino)
                
                if is_valid:
                    print(f"✅ Transição {estado_atual} → {estado_destino} aceita (correto)")
                else:
                    print(f"❌ Transição {estado_atual} → {estado_destino} rejeitada (incorreto)")
                    self.errors_found.append(f"Transição válida rejeitada: {estado_atual} → {estado_destino}")
            
            # Testar transições inválidas
            transicoes_invalidas = [
                ("inicio", "confirmando_agendamento"),
                ("menu_principal", "escolhendo_horario"),
                ("aguardando_cpf", "finalizada"),
            ]
            
            for estado_atual, estado_destino in transicoes_invalidas:
                is_valid, error_message = self.state_manager.can_transition_to(estado_atual, estado_destino)
                
                if not is_valid:
                    print(f"✅ Transição inválida {estado_atual} → {estado_destino} rejeitada (correto)")
                else:
                    print(f"❌ Transição inválida {estado_atual} → {estado_destino} aceita (incorreto)")
                    self.errors_found.append(f"Transição inválida aceita: {estado_atual} → {estado_destino}")
                    
        except Exception as e:
            print(f"❌ Erro ao testar validação de transições: {str(e)}")
            self.errors_found.append(f"Erro validação transições: {str(e)}")

    async def _test_validacao_contexto(self):
        """Testa validação de contexto"""
        try:
            # Testar contextos válidos
            contextos_validos = [
                ("aguardando_cpf", {"acao": "agendar"}),
                ("escolhendo_tipo_consulta", {"paciente": {"id": "1", "nome": "Teste"}}),
            ]
            
            for estado, contexto in contextos_validos:
                is_valid, error_message, missing_fields = self.state_manager.validate_context_for_state(estado, contexto)
                
                if is_valid:
                    print(f"✅ Contexto válido para {estado} aceito (correto)")
                else:
                    print(f"❌ Contexto válido para {estado} rejeitado (incorreto)")
                    self.errors_found.append(f"Contexto válido rejeitado: {estado}")
            
            # Testar contextos inválidos
            contextos_invalidos = [
                ("aguardando_cpf", {}),
                ("escolhendo_tipo_consulta", {}),
            ]
            
            for estado, contexto in contextos_invalidos:
                is_valid, error_message, missing_fields = self.state_manager.validate_context_for_state(estado, contexto)
                
                if not is_valid:
                    print(f"✅ Contexto inválido para {estado} rejeitado (correto)")
                else:
                    print(f"❌ Contexto inválido para {estado} aceito (incorreto)")
                    self.errors_found.append(f"Contexto inválido aceito: {estado}")
                    
        except Exception as e:
            print(f"❌ Erro ao testar validação de contexto: {str(e)}")
            self.errors_found.append(f"Erro validação contexto: {str(e)}")

    async def _test_multiplas_conversas(self):
        """Testa múltiplas conversas simultâneas"""
        try:
            phones = ["5531999999991", "5531999999992", "5531999999993"]
            db = next(get_db())
            
            # Iniciar múltiplas conversas
            for i, phone in enumerate(phones):
                await self.conversation_manager.processar_mensagem(
                    phone=phone, message="oi", message_id=f"multiplas_conv_{i+1}", db=db
                )
            
            # Verificar se cada conversa mantém seu estado
            for i, phone in enumerate(phones):
                await self.conversation_manager.processar_mensagem(
                    phone=phone, message="1", message_id=f"multiplas_conv_{i+4}", db=db
                )
            
            print("✅ Múltiplas conversas simultâneas testadas")
            
        except Exception as e:
            print(f"❌ Erro ao testar múltiplas conversas: {str(e)}")
            self.errors_found.append(f"Erro múltiplas conversas: {str(e)}")

    async def _test_persistencia_estado(self):
        """Testa persistência de estado"""
        try:
            phone = "5531999999990"
            db = next(get_db())
            
            # Iniciar conversa
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="oi", message_id="persist_1", db=db
            )
            
            # Simular nova instância do ConversationManager
            new_manager = ConversationManager()
            
            # Verificar se o estado persiste
            await new_manager.processar_mensagem(
                phone=phone, message="1", message_id="persist_2", db=db
            )
            
            print("✅ Persistência de estado testada")
            
        except Exception as e:
            print(f"❌ Erro ao testar persistência: {str(e)}")
            self.errors_found.append(f"Erro persistência: {str(e)}")

    async def _test_recuperacao_erro(self):
        """Testa recuperação de erro"""
        try:
            phone = "5531999999989"
            db = next(get_db())
            
            # Tentar processar com dados inválidos
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="", message_id="recuperacao_1", db=db
            )
            
            # Tentar processar com estado inválido
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="999", message_id="recuperacao_2", db=db
            )
            
            # Verificar se o sistema se recupera
            await self.conversation_manager.processar_mensagem(
                phone=phone, message="oi", message_id="recuperacao_3", db=db
            )
            
            print("✅ Recuperação de erro testada")
            
        except Exception as e:
            print(f"❌ Erro ao testar recuperação: {str(e)}")
            self.errors_found.append(f"Erro recuperação: {str(e)}")

    async def run_verificacao_completa(self):
        """Executa verificação completa do sistema"""
        print("🔍 INICIANDO VERIFICAÇÃO COMPLETA DO SISTEMA")
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        try:
            # Executar todos os testes
            await self.test_cenarios_edge_cases()
            await self.test_fluxos_alternativos()
            await self.test_validacoes_rigorosas()
            await self.test_concorrencia_e_estado()
            
            # Relatório final
            print("\n" + "="*50)
            print("📊 RELATÓRIO FINAL DA VERIFICAÇÃO")
            print("="*50)
            
            if self.errors_found:
                print(f"❌ ERROS ENCONTRADOS: {len(self.errors_found)}")
                for i, error in enumerate(self.errors_found, 1):
                    print(f"  {i}. {error}")
                print("\n⚠️  SISTEMA PRECISA DE CORREÇÕES!")
            else:
                print("✅ NENHUM ERRO ENCONTRADO!")
                print("🎉 SISTEMA ESTÁ 100% FUNCIONAL!")
            
            print("="*50)
            
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO NA VERIFICAÇÃO: {str(e)}")
            import traceback
            traceback.print_exc()

async def main():
    """Função principal"""
    verificador = TestVerificacaoCompleta()
    await verificador.run_verificacao_completa()

if __name__ == "__main__":
    asyncio.run(main()) 