#!/usr/bin/env python3
"""
Teste para verificar o GestaoDS mock
"""

import asyncio
import sys
import os

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gestaods import GestaoDS

async def test_gestaods_mock():
    """Testa o GestaoDS mock"""
    
    print("🧪 TESTE - GESTAODS MOCK")
    print("=" * 30)
    
    # Criar instância do GestaoDS
    gestaods = GestaoDS()
    
    try:
        # Testar busca de paciente
        print("\n1️⃣ Teste busca de paciente")
        print("-" * 25)
        
        cpf = "52998224725"
        paciente = await gestaods.buscar_paciente_cpf(cpf)
        
        print(f"CPF: {cpf}")
        print(f"Paciente encontrado: {paciente is not None}")
        if paciente:
            print(f"Dados do paciente: {paciente}")
        
        # Testar listagem de agendamentos
        print("\n2️⃣ Teste listagem de agendamentos")
        print("-" * 35)
        
        agendamentos = await gestaods.listar_agendamentos_periodo(
            data_inicial="01/01/2024",
            data_final="31/12/2024"
        )
        
        print(f"Agendamentos encontrados: {len(agendamentos)}")
        for i, ag in enumerate(agendamentos, 1):
            print(f"  {i}. {ag}")
        
        print("\n✅ TESTE GESTAODS MOCK CONCLUÍDO!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gestaods_mock()) 