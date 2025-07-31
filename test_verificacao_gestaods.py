#!/usr/bin/env python3
"""
Teste Específico para Verificar API do GestaoDS
"""

import asyncio
import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gestaods import GestaoDS
from app.config import settings

class TestGestaoDS:
    def __init__(self):
        self.gestaods = GestaoDS()
        
    def test_configuracao(self):
        """Testa se a configuração está correta"""
        print("=== TESTE CONFIGURAÇÃO GESTAODS ===")
        
        print(f"🔗 URL Base: {self.gestaods.base_url}")
        print(f"🔑 Token: {self.gestaods.token[:10]}..." if self.gestaods.token else "❌ Token não configurado")
        print(f"📋 Headers: {self.gestaods.headers}")
        
        if not self.gestaods.base_url:
            print("❌ URL da API não configurada")
            return False
            
        if not self.gestaods.token:
            print("❌ Token da API não configurado")
            return False
            
        print("✅ Configuração OK")
        return True

    async def test_buscar_paciente(self):
        """Testa busca de paciente"""
        print("\n=== TESTE BUSCA PACIENTE ===")
        
        cpf_teste = "52998224725"  # CPF válido para teste
        
        print(f"🔍 Buscando paciente com CPF: {cpf_teste}")
        
        try:
            paciente = await self.gestaods.buscar_paciente_cpf(cpf_teste)
            
            if paciente:
                print("✅ Paciente encontrado:")
                print(f"   ID: {paciente.get('id')}")
                print(f"   Nome: {paciente.get('nome')}")
                print(f"   CPF: {paciente.get('cpf')}")
                print(f"   Telefone: {paciente.get('telefone')}")
                print(f"   Email: {paciente.get('email')}")
                return True
            else:
                print("❌ Paciente não encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao buscar paciente: {str(e)}")
            return False

    async def test_buscar_dias_disponiveis(self):
        """Testa busca de dias disponíveis"""
        print("\n=== TESTE DIAS DISPONÍVEIS ===")
        
        try:
            dias = await self.gestaods.buscar_dias_disponiveis()
            
            if dias:
                print(f"✅ Dias disponíveis encontrados: {len(dias)}")
                # Verificar se dias é uma lista
                if isinstance(dias, list) and len(dias) > 0:
                    for i, dia in enumerate(dias[:3]):  # Mostrar apenas os 3 primeiros
                        print(f"   {i+1}. {dia}")
                else:
                    print(f"   Dados: {dias}")
                return True
            else:
                print("❌ Nenhum dia disponível encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao buscar dias disponíveis: {str(e)}")
            return False

    async def test_buscar_horarios_disponiveis(self):
        """Testa busca de horários disponíveis"""
        print("\n=== TESTE HORÁRIOS DISPONÍVEIS ===")
        
        # Usar data de hoje
        from datetime import datetime
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        
        print(f"🔍 Buscando horários para: {data_hoje}")
        
        try:
            horarios = await self.gestaods.buscar_horarios_disponiveis(data_hoje)
            
            if horarios:
                print(f"✅ Horários disponíveis encontrados: {len(horarios)}")
                for i, horario in enumerate(horarios[:5]):  # Mostrar apenas os 5 primeiros
                    print(f"   {i+1}. {horario}")
                return True
            else:
                print("❌ Nenhum horário disponível encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao buscar horários disponíveis: {str(e)}")
            return False

    async def test_criar_agendamento(self):
        """Testa criação de agendamento"""
        print("\n=== TESTE CRIAR AGENDAMENTO ===")
        
        cpf_teste = "52998224725"
        data_agendamento = "15/01/2024 14:00:00"
        data_fim_agendamento = "15/01/2024 14:30:00"
        
        print(f"🔍 Criando agendamento para CPF: {cpf_teste}")
        print(f"   Data início: {data_agendamento}")
        print(f"   Data fim: {data_fim_agendamento}")
        
        try:
            agendamento = await self.gestaods.criar_agendamento(
                cpf=cpf_teste,
                data_agendamento=data_agendamento,
                data_fim_agendamento=data_fim_agendamento,
                primeiro_atendimento=True
            )
            
            if agendamento:
                print("✅ Agendamento criado com sucesso:")
                print(f"   ID: {agendamento.get('id')}")
                print(f"   Status: {agendamento.get('status')}")
                return True
            else:
                print("❌ Falha ao criar agendamento")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao criar agendamento: {str(e)}")
            return False

    async def test_fuso_horario(self):
        """Testa busca de fuso horário"""
        print("\n=== TESTE FUSO HORÁRIO ===")
        
        try:
            fuso = await self.gestaods.retornar_fuso_horario()
            
            if fuso:
                print("✅ Fuso horário encontrado:")
                print(f"   Fuso: {fuso}")
                return True
            else:
                print("❌ Fuso horário não encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao buscar fuso horário: {str(e)}")
            return False

    async def test_dados_agendamento(self):
        """Testa busca de dados do agendamento"""
        print("\n=== TESTE DADOS AGENDAMENTO ===")
        
        try:
            dados = await self.gestaods.buscar_dados_agendamento()
            
            if dados:
                print("✅ Dados do agendamento encontrados:")
                print(f"   Dados: {dados}")
                return True
            else:
                print("❌ Dados do agendamento não encontrados")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao buscar dados do agendamento: {str(e)}")
            return False

    async def test_listar_agendamentos(self):
        """Testa listagem de agendamentos"""
        print("\n=== TESTE LISTAR AGENDAMENTOS ===")
        
        from datetime import datetime, timedelta
        
        data_inicial = datetime.now().strftime("%Y-%m-%d")
        data_final = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        print(f"🔍 Listando agendamentos de {data_inicial} até {data_final}")
        
        try:
            agendamentos = await self.gestaods.listar_agendamentos_periodo(
                data_inicial, data_final
            )
            
            if agendamentos:
                print(f"✅ Agendamentos encontrados: {len(agendamentos)}")
                for i, agendamento in enumerate(agendamentos[:3]):  # Mostrar apenas os 3 primeiros
                    print(f"   {i+1}. ID: {agendamento.get('id')}")
                    print(f"      Data: {agendamento.get('data_hora')}")
                    print(f"      Tipo: {agendamento.get('tipo_consulta')}")
                    print(f"      Status: {agendamento.get('status')}")
                return True
            else:
                print("❌ Nenhum agendamento encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao listar agendamentos: {str(e)}")
            return False

    async def test_formatacao_datas(self):
        """Testa formatação de datas"""
        print("\n=== TESTE FORMATAÇÃO DE DATAS ===")
        
        # Teste formatação data/hora
        data_hora_teste = "2024-01-15T14:00:00"
        data_formatada = self.gestaods.formatar_data_hora(data_hora_teste)
        print(f"📅 Data/hora original: {data_hora_teste}")
        print(f"📅 Data/hora formatada: {data_formatada}")
        
        # Teste formatação data simples
        data_simples = "2024-01-15"
        data_formatada_simples = self.gestaods.formatar_data(data_simples)
        print(f"📅 Data original: {data_simples}")
        print(f"📅 Data formatada: {data_formatada_simples}")
        
        return True

    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🔍 TESTE ESPECÍFICO - API GESTAODS")
        print("="*50)
        
        resultados = {}
        
        try:
            # Teste de configuração
            resultados['configuracao'] = self.test_configuracao()
            
            if not resultados['configuracao']:
                print("❌ Configuração inválida - parando testes")
                return
            
            # Testes da API
            resultados['buscar_paciente'] = await self.test_buscar_paciente()
            resultados['dias_disponiveis'] = await self.test_buscar_dias_disponiveis()
            resultados['horarios_disponiveis'] = await self.test_buscar_horarios_disponiveis()
            resultados['fuso_horario'] = await self.test_fuso_horario()
            resultados['dados_agendamento'] = await self.test_dados_agendamento()
            resultados['listar_agendamentos'] = await self.test_listar_agendamentos()
            resultados['criar_agendamento'] = await self.test_criar_agendamento()
            resultados['formatacao_datas'] = await self.test_formatacao_datas()
            
            # Resumo
            print("\n" + "="*50)
            print("📊 RESUMO DOS TESTES")
            print("="*50)
            
            total_tests = len(resultados)
            tests_passando = sum(resultados.values())
            
            for teste, resultado in resultados.items():
                status = "✅ PASSOU" if resultado else "❌ FALHOU"
                print(f"{status} - {teste}")
            
            print(f"\n📈 Resultado: {tests_passando}/{total_tests} testes passando")
            
            if tests_passando == total_tests:
                print("🎉 TODOS OS TESTES PASSARAM!")
            else:
                print("⚠️  ALGUNS TESTES FALHARAM")
                
        except Exception as e:
            print(f"❌ ERRO GERAL NO TESTE: {str(e)}")
            import traceback
            traceback.print_exc()

def main():
    """Função principal"""
    tester = TestGestaoDS()
    asyncio.run(tester.run_all_tests())

if __name__ == "__main__":
    main() 