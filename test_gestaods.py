#!/usr/bin/env python3
"""
Teste de integração com a GestãoDS
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gestaods import GestaoDS
from app.config import settings

async def test_gestaods_integration():
    """Testa a integração com a GestãoDS"""
    print("🧪 Testando integração com GestãoDS...")
    
    # Configurar credenciais de teste
    os.environ['GESTAODS_API_URL'] = 'https://apidev.gestaods.com.br'
    os.environ['GESTAODS_TOKEN'] = '733a8e19a94b65d58390da380ac946b6d603a535'
    
    gestaods = GestaoDS()
    
    try:
        # Teste 1: Buscar paciente por CPF
        print("\n1️⃣ Testando busca de paciente...")
        cpf_teste = "12345678901"  # CPF de teste
        paciente = await gestaods.buscar_paciente_cpf(cpf_teste)
        
        if paciente:
            print(f"✅ Paciente encontrado: {paciente.get('nome', 'N/A')}")
            print(f"   ID: {paciente.get('id', 'N/A')}")
            print(f"   CPF: {paciente.get('cpf', 'N/A')}")
        else:
            print("ℹ️  Paciente não encontrado (esperado para CPF de teste)")
        
        # Teste 2: Listar horários disponíveis
        print("\n2️⃣ Testando busca de horários disponíveis...")
        data_inicio = datetime.now() + timedelta(days=1)
        data_fim = datetime.now() + timedelta(days=7)
        
        horarios = await gestaods.listar_horarios_disponiveis(
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo_consulta="consulta"
        )
        
        if horarios:
            print(f"✅ Encontrados {len(horarios)} horários disponíveis:")
            for i, horario in enumerate(horarios[:5]):  # Mostrar apenas os 5 primeiros
                print(f"   {i+1}. {horario['data']} às {horario['hora']} - {horario['dia_semana']}")
        else:
            print("ℹ️  Nenhum horário disponível encontrado")
        
        # Teste 3: Buscar agendamentos do dia
        print("\n3️⃣ Testando busca de agendamentos do dia...")
        hoje = datetime.now()
        agendamentos = await gestaods.buscar_agendamentos_dia(hoje)
        
        if agendamentos:
            print(f"✅ Encontrados {len(agendamentos)} agendamentos para hoje")
            for i, agendamento in enumerate(agendamentos[:3]):  # Mostrar apenas os 3 primeiros
                print(f"   {i+1}. {agendamento.get('paciente_nome', 'N/A')} - {agendamento.get('data_hora', 'N/A')}")
        else:
            print("ℹ️  Nenhum agendamento encontrado para hoje")
        
        print("\n✅ Todos os testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gestaods_integration()) 