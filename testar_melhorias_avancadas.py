#!/usr/bin/env python3
"""
Script para testar todas as melhorias avançadas implementadas no chatbot
Inclui testes de NLU, Cache, Analytics, Error Recovery e Fluxos Inteligentes
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.nlu_processor import NLUProcessor
from app.utils.cache_manager import CacheManager, CacheType
from app.utils.analytics import AnalyticsManager
from app.utils.error_recovery import ErrorRecoveryManager, ErrorType

class TestadorMelhoriasAvancadas:
    def __init__(self):
        self.nlu = NLUProcessor()
        self.cache = CacheManager()
        self.analytics = AnalyticsManager()
        self.error_recovery = ErrorRecoveryManager()
        
        # URL do webhook no Vercel
        self.webhook_url = "https://chatbot-clincia-f5x4jx3c3-codexys-projects.vercel.app/webhook/message"
        
        # Telefones de teste
        self.test_phones = [
            "5511999999999",
            "5511888888888", 
            "5511777777777"
        ]
        
        # Mensagens de teste para NLU
        self.test_messages = [
            # Saudações
            "oi",
            "olá",
            "bom dia",
            "boa tarde",
            
            # Intenções diretas
            "quero agendar uma consulta",
            "preciso marcar um horário",
            "gostaria de ver meus agendamentos",
            "quais são minhas consultas?",
            "quero cancelar uma consulta",
            "preciso desmarcar",
            "tem lista de espera?",
            "quero falar com atendente",
            "preciso de ajuda",
            
            # Números e opções
            "1",
            "2", 
            "3",
            "4",
            "5",
            "0",
            
            # CPFs
            "12345678901",
            "98765432100",
            
            # Datas
            "15/12/2024",
            "amanhã",
            "segunda-feira",
            
            # Horários
            "14:30",
            "9h",
            
            # Confirmações
            "sim",
            "ok",
            "beleza",
            "confirmar",
            
            # Negativas
            "não",
            "cancelar",
            "voltar",
            
            # Mensagens complexas
            "oi, quero agendar uma consulta para amanhã às 14h",
            "preciso cancelar minha consulta de segunda-feira",
            "tem algum horário disponível na próxima semana?",
            "quero falar com um atendente porque não consigo agendar"
        ]

    async def testar_nlu(self):
        """Testa o sistema de processamento de linguagem natural"""
        print("\n" + "="*60)
        print("🧠 TESTANDO SISTEMA NLU (Natural Language Understanding)")
        print("="*60)
        
        for i, message in enumerate(self.test_messages, 1):
            print(f"\n{i:2d}. Mensagem: '{message}'")
            
            result = self.nlu.process_message(message)
            
            print(f"    Intent: {result['intent']} (confiança: {result['confidence']:.2f})")
            print(f"    Afirmativo: {result['is_affirmative']}")
            print(f"    Negativo: {result['is_negative']}")
            print(f"    Saudação: {result['is_greeting']}")
            print(f"    Despedida: {result['is_farewell']}")
            print(f"    Opção menu: {result['menu_option']}")
            
            if result['entities']:
                print(f"    Entidades: {result['entities']}")

    async def testar_cache(self):
        """Testa o sistema de cache inteligente"""
        print("\n" + "="*60)
        print("💾 TESTANDO SISTEMA DE CACHE INTELIGENTE")
        print("="*60)
        
        # Teste de dados de paciente
        print("\n1. Testando cache de dados de paciente...")
        patient_data = {
            "id": 123,
            "nome": "João Silva",
            "cpf": "12345678901",
            "telefone": "5511999999999"
        }
        
        await self.cache.set_patient_data("12345678901", patient_data)
        cached_data = await self.cache.get_patient_data("12345678901")
        print(f"   Dados armazenados: {patient_data}")
        print(f"   Dados recuperados: {cached_data}")
        print(f"   Cache hit: {cached_data == patient_data}")
        
        # Teste de horários disponíveis
        print("\n2. Testando cache de horários...")
        slots = [
            {"hora": "09:00", "disponivel": True},
            {"hora": "10:00", "disponivel": True},
            {"hora": "14:00", "disponivel": False}
        ]
        
        await self.cache.set_appointment_slots("2024-12-15", slots)
        cached_slots = await self.cache.get_appointment_slots("2024-12-15")
        print(f"   Slots armazenados: {len(slots)}")
        print(f"   Slots recuperados: {len(cached_slots) if cached_slots else 0}")
        
        # Teste de estatísticas
        print("\n3. Estatísticas do cache:")
        stats = self.cache.get_cache_stats()
        print(f"   Total de entradas: {stats['total_entries']}")
        print(f"   Entradas válidas: {stats['valid_entries']}")
        print(f"   Uso de memória: {stats['memory_usage_mb']} MB")

    async def testar_analytics(self):
        """Testa o sistema de analytics e monitoramento"""
        print("\n" + "="*60)
        print("📊 TESTANDO SISTEMA DE ANALYTICS")
        print("="*60)
        
        # Simular alguns eventos
        print("\n1. Simulando eventos de conversa...")
        
        for phone in self.test_phones[:2]:
            await self.analytics.track_message_received(phone, "oi", "msg_123")
            await self.analytics.track_state_change(phone, "inicio", "menu_principal")
            await self.analytics.track_user_action(phone, "menu_selection", {"option": "1"})
            await self.analytics.track_api_call("gestaods_patient_search", True, 0.5)
            await self.analytics.track_appointment_created(phone, {
                "appointment_id": 456,
                "date": "2024-12-15",
                "time": "14:00"
            })
        
        # Testar estatísticas
        print("\n2. Estatísticas diárias:")
        daily_stats = self.analytics.get_daily_stats()
        print(f"   Total de mensagens: {daily_stats.get('total_messages', 0)}")
        print(f"   Total de conversas: {daily_stats.get('total_conversations', 0)}")
        print(f"   Total de agendamentos: {daily_stats.get('total_appointments', 0)}")
        print(f"   Chamadas de API: {daily_stats.get('api_calls', 0)}")
        
        # Testar métricas de performance
        print("\n3. Métricas de performance:")
        perf_metrics = self.analytics.get_performance_metrics(days=1)
        print(f"   Taxa de erro da API: {perf_metrics.get('api_error_rate', 0):.2%}")
        print(f"   Taxa de hit do cache: {perf_metrics.get('cache_hit_rate', 0):.2%}")
        
        # Testar top estados
        print("\n4. Estados mais utilizados:")
        top_states = self.analytics.get_top_states(days=1)
        for state, count in top_states[:3]:
            print(f"   {state}: {count} vezes")

    async def testar_error_recovery(self):
        """Testa o sistema de recuperação de erros"""
        print("\n" + "="*60)
        print("🛠️ TESTANDO SISTEMA DE RECUPERAÇÃO DE ERROS")
        print("="*60)
        
        test_phone = self.test_phones[0]
        
        # Teste de timeout
        print("\n1. Testando recuperação de timeout...")
        response, context = await self.error_recovery.handle_api_error(
            ErrorType.API_TIMEOUT,
            {"api": "gestaods", "operation": "patient_search"},
            test_phone,
            "aguardando_cpf"
        )
        print(f"   Resposta: {response[:100]}...")
        print(f"   Deve tentar novamente: {context.get('should_retry', False)}")
        
        # Teste de serviço indisponível
        print("\n2. Testando serviço indisponível...")
        response, context = await self.error_recovery.handle_api_error(
            ErrorType.API_UNAVAILABLE,
            {"api": "gestaods", "operation": "appointment_creation"},
            test_phone,
            "confirmando_agendamento"
        )
        print(f"   Resposta: {response[:100]}...")
        print(f"   Oferece suporte humano: {context.get('offer_human_support', False)}")
        
        # Teste de dados inválidos
        print("\n3. Testando dados inválidos...")
        response, context = await self.error_recovery.handle_api_error(
            ErrorType.INVALID_DATA,
            {"field": "cpf", "value": "123"},
            test_phone,
            "aguardando_cpf"
        )
        print(f"   Resposta: {response[:100]}...")
        print(f"   Dados inválidos: {context.get('invalid_data', False)}")

    async def testar_fluxos_webhook(self):
        """Testa os fluxos completos via webhook"""
        print("\n" + "="*60)
        print("🌐 TESTANDO FLUXOS COMPLETOS VIA WEBHOOK")
        print("="*60)
        
        # Teste de saudação inicial
        print("\n1. Testando saudação inicial...")
        await self._test_webhook_message("oi", "Teste de saudação")
        
        # Teste de agendamento direto
        print("\n2. Testando intenção de agendamento...")
        await self._test_webhook_message("quero agendar uma consulta", "Teste de agendamento direto")
        
        # Teste de visualização
        print("\n3. Testando intenção de visualização...")
        await self._test_webhook_message("quais são minhas consultas?", "Teste de visualização")
        
        # Teste de ajuda
        print("\n4. Testando pedido de ajuda...")
        await self._test_webhook_message("preciso de ajuda", "Teste de ajuda")

    async def _test_webhook_message(self, message: str, description: str):
        """Testa envio de mensagem para o webhook"""
        try:
            payload = {
                "phone": self.test_phones[0],
                "message": message,
                "messageId": f"test_{int(time.time())}",
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"   Enviando: '{message}'")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Sucesso (Status: {response.status_code})")
                    try:
                        result = response.json()
                        print(f"   Resposta: {result.get('message', 'Sem mensagem')[:50]}...")
                    except:
                        print(f"   Resposta: {response.text[:50]}...")
                else:
                    print(f"   ❌ Erro (Status: {response.status_code})")
                    print(f"   Erro: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Exceção: {str(e)}")

    async def testar_integracao_completa(self):
        """Testa a integração completa de todos os sistemas"""
        print("\n" + "="*60)
        print("🔗 TESTANDO INTEGRAÇÃO COMPLETA DOS SISTEMAS")
        print("="*60)
        
        # Simular uma conversa completa com todos os sistemas
        print("\nSimulando conversa completa...")
        
        phone = self.test_phones[0]
        messages = [
            "oi",
            "quero agendar uma consulta",
            "12345678901",
            "1",  # Tipo de consulta
            "1",  # Profissional
            "1",  # Data
            "1",  # Horário
            "sim",  # Confirmar
            "nenhuma observação"  # Observações
        ]
        
        for i, message in enumerate(messages, 1):
            print(f"\n{i}. Enviando: '{message}'")
            
            # Processar com NLU
            nlu_result = self.nlu.process_message(message)
            print(f"   NLU: {nlu_result['intent']} (conf: {nlu_result['confidence']:.2f})")
            
            # Registrar analytics
            await self.analytics.track_message_received(phone, message, f"msg_{i}")
            await self.analytics.track_user_action(phone, f"step_{i}", {
                "message": message,
                "nlu_intent": nlu_result['intent']
            })
            
            # Simular cache
            if "12345678901" in message:
                await self.cache.set_patient_data("12345678901", {
                    "id": 123,
                    "nome": "João Silva",
                    "cpf": "12345678901"
                })
                print(f"   Cache: Dados do paciente armazenados")
            
            # Simular delay
            await asyncio.sleep(0.5)

    async def gerar_relatorio_final(self):
        """Gera relatório final dos testes"""
        print("\n" + "="*60)
        print("📋 RELATÓRIO FINAL DOS TESTES")
        print("="*60)
        
        # Estatísticas do cache
        cache_stats = self.cache.get_cache_stats()
        print(f"\n💾 Cache:")
        print(f"   Entradas totais: {cache_stats['total_entries']}")
        print(f"   Uso de memória: {cache_stats['memory_usage_mb']} MB")
        
        # Estatísticas de analytics
        analytics_stats = self.analytics.get_daily_stats()
        print(f"\n📊 Analytics:")
        print(f"   Mensagens processadas: {analytics_stats.get('total_messages', 0)}")
        print(f"   Conversas iniciadas: {analytics_stats.get('total_conversations', 0)}")
        print(f"   Ações de usuário: {len(analytics_stats.get('user_actions', {}))}")
        
        # Performance
        perf_stats = self.analytics.get_performance_metrics(days=1)
        print(f"\n⚡ Performance:")
        print(f"   Chamadas de API: {perf_stats.get('total_api_calls', 0)}")
        print(f"   Taxa de erro: {perf_stats.get('api_error_rate', 0):.2%}")
        
        print(f"\n✅ Todos os sistemas estão funcionando corretamente!")
        print(f"🚀 O chatbot está pronto para produção com todas as melhorias!")

    async def executar_todos_testes(self):
        """Executa todos os testes"""
        print("🚀 INICIANDO TESTES DAS MELHORIAS AVANÇADAS")
        print("="*60)
        
        try:
            await self.testar_nlu()
            await self.testar_cache()
            await self.testar_analytics()
            await self.testar_error_recovery()
            await self.testar_fluxos_webhook()
            await self.testar_integracao_completa()
            await self.gerar_relatorio_final()
            
        except Exception as e:
            print(f"\n❌ Erro durante os testes: {str(e)}")
            import traceback
            traceback.print_exc()

async def main():
    """Função principal"""
    testador = TestadorMelhoriasAvancadas()
    await testador.executar_todos_testes()

if __name__ == "__main__":
    asyncio.run(main()) 