#!/usr/bin/env python3
"""
Script de teste para a nova implementação da API do GestãoDS
Baseado na especificação OpenAPI fornecida
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gestaods import GestaoDS
from app.config import settings

async def test_gestaods_api():
    """Testa todos os endpoints da API do GestãoDS"""
    
    print("🧪 TESTANDO NOVA API DO GESTÃODS")
    print("=" * 50)
    
    # Configurar variáveis de ambiente se não estiverem definidas
    if not hasattr(settings, 'gestaods_api_url') or not settings.gestaods_api_url:
        os.environ['GESTAODS_API_URL'] = 'https://apidev.gestaods.com.br'
    
    if not hasattr(settings, 'gestaods_token') or not settings.gestaods_token:
        os.environ['GESTAODS_TOKEN'] = '733a8e19a94b65d58390da380ac946b6d603a535'
    
    gestaods = GestaoDS()
    
    print(f"🔗 URL Base: {gestaods.base_url}")
    print(f"🔑 Token: {gestaods.token[:10]}...")
    print()
    
    # Teste 1: Buscar paciente por CPF
    print("1️⃣ Testando busca de paciente por CPF...")
    cpf_teste = "12345678901"  # CPF de teste
    
    try:
        paciente = await gestaods.buscar_paciente_cpf(cpf_teste)
        if paciente:
            print(f"✅ Paciente encontrado: {paciente}")
        else:
            print("ℹ️ Paciente não encontrado (esperado para CPF de teste)")
    except Exception as e:
        print(f"❌ Erro ao buscar paciente: {str(e)}")
    
    print()
    
    # Teste 2: Buscar dias disponíveis
    print("2️⃣ Testando busca de dias disponíveis...")
    try:
        dias = await gestaods.buscar_dias_disponiveis()
        if dias:
            print(f"✅ Dias disponíveis encontrados: {len(dias)} dias")
            # Mostrar apenas os primeiros 3 dias
            for i in range(min(3, len(dias))):
                try:
                    print(f"   {i+1}. {str(dias[i])}")
                except Exception as e:
                    print(f"   {i+1}. [Erro ao exibir dia: {str(e)}]")
        else:
            print("ℹ️ Nenhum dia disponível encontrado")
    except Exception as e:
        print(f"❌ Erro ao buscar dias disponíveis: {str(e)}")
    
    print()
    
    # Teste 3: Buscar horários disponíveis
    print("3️⃣ Testando busca de horários disponíveis...")
    try:
        # Usar data de hoje formatada
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        horarios = await gestaods.buscar_horarios_disponiveis(data_hoje)
        if horarios:
            print(f"✅ Horários disponíveis encontrados: {len(horarios)} horários")
            # Mostrar apenas os primeiros 3 horários
            for i in range(min(3, len(horarios))):
                try:
                    print(f"   {i+1}. {str(horarios[i])}")
                except Exception as e:
                    print(f"   {i+1}. [Erro ao exibir horário: {str(e)}]")
        else:
            print("ℹ️ Nenhum horário disponível encontrado")
    except Exception as e:
        print(f"❌ Erro ao buscar horários disponíveis: {str(e)}")
    
    print()
    
    # Teste 4: Retornar fuso horário
    print("4️⃣ Testando busca de fuso horário...")
    try:
        fuso = await gestaods.retornar_fuso_horario()
        if fuso:
            print(f"✅ Fuso horário: {fuso}")
        else:
            print("ℹ️ Fuso horário não encontrado")
    except Exception as e:
        print(f"❌ Erro ao buscar fuso horário: {str(e)}")
    
    print()
    
    # Teste 5: Buscar dados do agendamento
    print("5️⃣ Testando busca de dados do agendamento...")
    try:
        dados = await gestaods.buscar_dados_agendamento()
        if dados:
            print(f"✅ Dados do agendamento: {dados}")
        else:
            print("ℹ️ Dados do agendamento não encontrados")
    except Exception as e:
        print(f"❌ Erro ao buscar dados do agendamento: {str(e)}")
    
    print()
    
    # Teste 6: Listar agendamentos por período
    print("6️⃣ Testando listagem de agendamentos por período...")
    try:
        data_inicial = (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y")
        data_final = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
        
        agendamentos = await gestaods.listar_agendamentos_periodo(data_inicial, data_final)
        if agendamentos:
            print(f"✅ Agendamentos encontrados: {len(agendamentos)} agendamentos")
            # Mostrar apenas os primeiros 3 agendamentos
            for i in range(min(3, len(agendamentos))):
                try:
                    print(f"   {i+1}. {str(agendamentos[i])}")
                except Exception as e:
                    print(f"   {i+1}. [Erro ao exibir agendamento: {str(e)}]")
        else:
            print("ℹ️ Nenhum agendamento encontrado no período")
    except Exception as e:
        print(f"❌ Erro ao listar agendamentos: {str(e)}")
    
    print()
    
    # Teste 7: Testar formatação de data/hora
    print("7️⃣ Testando formatação de data/hora...")
    try:
        data_teste = "2024-01-15 14:30:00"
        data_formatada = gestaods.formatar_data_hora(data_teste)
        print(f"✅ Data original: {data_teste}")
        print(f"✅ Data formatada: {data_formatada}")
        
        data_simples = "2024-01-15"
        data_formatada_simples = gestaods.formatar_data(data_simples)
        print(f"✅ Data simples original: {data_simples}")
        print(f"✅ Data simples formatada: {data_formatada_simples}")
    except Exception as e:
        print(f"❌ Erro na formatação: {str(e)}")
    
    print()
    
    # Teste 8: Testar endpoint de desenvolvimento
    print("8️⃣ Testando endpoint de desenvolvimento...")
    try:
        paciente_dev = await gestaods.dev_buscar_paciente_cpf(cpf_teste)
        if paciente_dev:
            print(f"✅ Paciente encontrado (dev): {paciente_dev}")
        else:
            print("ℹ️ Paciente não encontrado (dev) - esperado para CPF de teste")
    except Exception as e:
        print(f"❌ Erro ao buscar paciente (dev): {str(e)}")
    
    print()
    print("=" * 50)
    print("🏁 TESTES CONCLUÍDOS")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_gestaods_api()) 