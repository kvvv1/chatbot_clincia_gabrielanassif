#!/usr/bin/env python3
"""
Teste de integração com Supabase
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.supabase_service import SupabaseService
from app.config import settings

async def test_supabase_integration():
    """Testa a integração com Supabase"""
    print("🧪 Testando integração com Supabase...")
    
    # Verificar se as credenciais estão configuradas
    if not settings.supabase_url or not settings.supabase_anon_key:
        print("❌ Credenciais do Supabase não configuradas!")
        print("💡 Configure as variáveis de ambiente:")
        print("   SUPABASE_URL=https://seu-projeto.supabase.co")
        print("   SUPABASE_ANON_KEY=sua_chave_anonima")
        print("   SUPABASE_SERVICE_ROLE_KEY=sua_chave_service_role")
        return
    
    supabase = SupabaseService()
    
    try:
        # Teste 1: Testar conexão
        print("\n1️⃣ Testando conexão com Supabase...")
        if await supabase.test_connection():
            print("✅ Conexão com Supabase estabelecida!")
        else:
            print("❌ Erro ao conectar com Supabase")
            return
        
        # Teste 2: Criar conversa
        print("\n2️⃣ Testando criação de conversa...")
        phone_test = "5531999999999"
        conversation = await supabase.create_conversation(
            phone=phone_test,
            state="inicio",
            context={"test": True}
        )
        
        if conversation:
            print(f"✅ Conversa criada: {conversation['id']}")
            conversation_id = conversation['id']
        else:
            print("❌ Erro ao criar conversa")
            return
        
        # Teste 3: Buscar conversa
        print("\n3️⃣ Testando busca de conversa...")
        found_conversation = await supabase.get_conversation(phone_test)
        
        if found_conversation:
            print(f"✅ Conversa encontrada: {found_conversation['id']}")
            print(f"   Estado: {found_conversation['state']}")
        else:
            print("❌ Erro ao buscar conversa")
        
        # Teste 4: Criar agendamento
        print("\n4️⃣ Testando criação de agendamento...")
        appointment_data = {
            "patient_id": "test_patient_123",
            "patient_name": "Paciente Teste",
            "patient_phone": phone_test,
            "appointment_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "appointment_type": "consulta",
            "status": "scheduled"
        }
        
        appointment = await supabase.create_appointment(appointment_data)
        
        if appointment:
            print(f"✅ Agendamento criado: {appointment['id']}")
            appointment_id = appointment['id']
        else:
            print("❌ Erro ao criar agendamento")
        
        # Teste 5: Buscar agendamentos por paciente
        print("\n5️⃣ Testando busca de agendamentos...")
        appointments = await supabase.get_appointments_by_patient("test_patient_123")
        
        if appointments:
            print(f"✅ Encontrados {len(appointments)} agendamentos")
            for app in appointments:
                print(f"   - {app['patient_name']} em {app['appointment_date']}")
        else:
            print("ℹ️  Nenhum agendamento encontrado")
        
        # Teste 6: Adicionar à lista de espera
        print("\n6️⃣ Testando lista de espera...")
        waiting_data = {
            "patient_id": "test_patient_456",
            "patient_name": "Paciente Lista Espera",
            "patient_phone": "5531888888888",
            "preferred_dates": ["2024-02-01", "2024-02-02"],
            "priority": 1
        }
        
        waiting_entry = await supabase.add_to_waiting_list(waiting_data)
        
        if waiting_entry:
            print(f"✅ Adicionado à lista de espera: {waiting_entry['id']}")
        else:
            print("❌ Erro ao adicionar à lista de espera")
        
        # Teste 7: Estatísticas do dashboard
        print("\n7️⃣ Testando estatísticas do dashboard...")
        stats = await supabase.get_dashboard_stats()
        
        if stats:
            print("✅ Estatísticas obtidas:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        else:
            print("❌ Erro ao obter estatísticas")
        
        # Teste 8: Limpeza (opcional)
        print("\n8️⃣ Limpando dados de teste...")
        # Aqui você pode adicionar código para limpar os dados de teste
        # Por exemplo, deletar conversas e agendamentos de teste
        
        print("\n✅ Todos os testes concluídos!")
        print("\n💡 Para limpar dados de teste, execute no SQL Editor do Supabase:")
        print("   DELETE FROM conversations WHERE phone = '5531999999999';")
        print("   DELETE FROM appointments WHERE patient_id LIKE '%test%';")
        print("   DELETE FROM waiting_list WHERE patient_id LIKE '%test%';")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_supabase_integration()) 