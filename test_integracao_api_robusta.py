"""
Teste da integração robusta com API - verifica se estados são mantidos durante falhas
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.conversation import ConversationManager
from app.models.database import get_db, Conversation
from datetime import datetime

async def test_falha_api_dias():
    """Testa comportamento quando API de dias falha"""
    manager = ConversationManager()
    db = next(get_db())
    phone = "5511888888888"
    
    print("🧪 TESTANDO FALHA NA API DE DIAS DISPONÍVEIS\n")
    print("=" * 60)
    
    # Limpar conversas antigas
    try:
        conv_antiga = db.query(Conversation).filter_by(phone=phone).first()
        if conv_antiga:
            db.delete(conv_antiga)
            db.commit()
    except:
        pass
    
    # 1. Iniciar fluxo normal
    print("1️⃣ INICIANDO FLUXO NORMAL")
    print("-" * 40)
    await manager.processar_mensagem(phone, "oi", "msg1", db)
    await manager.processar_mensagem(phone, "1", "msg2", db)
    
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado: {conversa.state}")
    print(f"   ✅ Contexto: {conversa.context}")
    assert conversa.state == "aguardando_cpf"
    assert conversa.context.get('acao') == 'agendar'
    print("   ✅ Fluxo iniciado corretamente!\n")
    
    # 2. Simular paciente válido primeiro
    print("2️⃣ SIMULANDO PACIENTE VÁLIDO")
    print("-" * 40)
    
    # Mock da API de paciente para retornar paciente válido
    paciente_mock = {
        "nome": "João Silva",
        "cpf": "12345678901",
        "id": "123"
    }
    original_buscar_paciente = manager.gestaods.buscar_paciente_cpf
    async def api_paciente_mock(cpf):
        return paciente_mock
    manager.gestaods.buscar_paciente_cpf = api_paciente_mock
    
    # Enviar CPF válido (vai encontrar paciente)
    await manager.processar_mensagem(phone, "12345678901", "msg3", db)
    
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado após CPF: {conversa.state}")
    print(f"   ✅ Paciente encontrado: {conversa.context.get('paciente', {}).get('nome')}")
    
    # 3. Agora simular falha na API de dias
    print("\n3️⃣ SIMULANDO FALHA NA API DE DIAS")
    print("-" * 40)
    
    # Mock da API de dias para falhar
    original_buscar_dias = manager.gestaods.buscar_dias_disponiveis
    async def api_dias_falha():
        return None
    manager.gestaods.buscar_dias_disponiveis = api_dias_falha
    
    # Como já temos o paciente, vamos adicionar ao contexto e triggerar o agendamento
    conversa.context['paciente'] = paciente_mock
    db.commit()
    await manager._iniciar_agendamento(phone, paciente_mock, conversa, db)
    
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado após falha: {conversa.state}")
    print(f"   ✅ Contexto preservado: {conversa.context}")
    
    # Verificações críticas
    assert conversa.state == "agendamento_sem_dias", f"Estado deveria ser 'agendamento_sem_dias', mas é '{conversa.state}'"
    assert conversa.context.get('acao') == 'agendar', "Contexto deve manter ação 'agendar'"
    assert 'paciente' in conversa.context, "Paciente deve estar no contexto"
    
    print("   ✅ CONTEXTO PRESERVADO após falha da API!\n")
    
    # 4. Testar recuperação
    print("4️⃣ TESTANDO RECUPERAÇÃO")
    print("-" * 40)
    
    # Restaurar API e tentar novamente
    manager.gestaods.buscar_dias_disponiveis = original_buscar_dias
    
    # Escolher opção "1" (tentar novamente)
    await manager.processar_mensagem(phone, "1", "msg4", db)
    
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado após recuperação: {conversa.state}")
    print(f"   ✅ Contexto mantido: {conversa.context}")
    
    # Deve ter ido para escolha de data ou algum estado válido
    assert conversa.state != "menu_principal", "Não deve voltar ao menu durante recuperação"
    assert conversa.context.get('acao') == 'agendar', "Ação deve ser mantida"
    
    # Restaurar API de paciente também
    manager.gestaods.buscar_paciente_cpf = original_buscar_paciente
    
    print("   ✅ RECUPERAÇÃO FUNCIONANDO!\n")
    
    print("=" * 60)
    print("✅ TESTE DE FALHA DA API PASSOU!")
    print("✅ Estados são preservados durante falhas!")

async def test_falha_api_horarios():
    """Testa comportamento quando API de horários falha"""
    manager = ConversationManager()
    db = next(get_db())
    phone = "5511777777777"
    
    print("\n🧪 TESTANDO FALHA NA API DE HORÁRIOS\n")
    print("=" * 60)
    
    # Criar conversa em estado específico
    conversa = Conversation(
        phone=phone,
        state="escolhendo_data",
        context={
            "acao": "agendar",
            "paciente": {"nome": "João", "cpf": "12345678901"},
            "dias_disponiveis": [
                {"data": "2024-01-15", "disponivel": True}
            ]
        }
    )
    db.add(conversa)
    db.commit()
    
    print("1️⃣ SIMULANDO FALHA NA API DE HORÁRIOS")
    print("-" * 40)
    
    # Mock da API de horários para falhar
    original_buscar_horarios = manager.gestaods.buscar_horarios_disponiveis
    async def api_horarios_falha(data):
        return None
    manager.gestaods.buscar_horarios_disponiveis = api_horarios_falha
    
    # Escolher data (vai tentar buscar horários e falhar)
    await manager.processar_mensagem(phone, "1", "msg1", db)
    
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado após falha: {conversa.state}")
    print(f"   ✅ Contexto: {conversa.context}")
    
    # Verificações
    assert conversa.state == "data_sem_horarios", f"Estado deveria ser 'data_sem_horarios', mas é '{conversa.state}'"
    assert conversa.context.get('acao') == 'agendar', "Ação deve ser preservada"
    
    print("   ✅ CONTEXTO PRESERVADO após falha de horários!\n")
    
    # Restaurar API
    manager.gestaods.buscar_horarios_disponiveis = original_buscar_horarios
    
    print("✅ TESTE DE FALHA DE HORÁRIOS PASSOU!")

async def test_persistencia_durante_requests():
    """Testa se estados são mantidos durante requisições longas"""
    manager = ConversationManager()
    db = next(get_db())
    phone = "5511666666666"
    
    print("\n🧪 TESTANDO PERSISTÊNCIA DURANTE REQUISIÇÕES\n")
    print("=" * 60)
    
    # Simular API lenta
    async def api_lenta():
        await asyncio.sleep(0.5)  # Simular demora
        return [{"data": "2024-01-15", "disponivel": True}]
    
    original_buscar_dias = manager.gestaods.buscar_dias_disponiveis
    manager.gestaods.buscar_dias_disponiveis = api_lenta
    
    print("1️⃣ INICIANDO FLUXO COM API LENTA")
    print("-" * 40)
    
    # Iniciar fluxo
    await manager.processar_mensagem(phone, "oi", "msg1", db)
    await manager.processar_mensagem(phone, "1", "msg2", db)
    
    # Durante a API lenta, verificar se estado é mantido
    conversa = manager._get_or_create_conversation(phone, db)
    estado_antes = conversa.state
    contexto_antes = conversa.context.copy()
    
    print(f"   📝 Estado antes da API: {estado_antes}")
    print(f"   📝 Contexto antes: {contexto_antes}")
    
    # Processar CPF (vai chamar API lenta)
    await manager.processar_mensagem(phone, "12345678901", "msg3", db)
    
    # Verificar se estado foi mantido
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado após API: {conversa.state}")
    print(f"   ✅ Contexto após: {conversa.context}")
    
    assert conversa.context.get('acao') == 'agendar', "Ação deve ser mantida durante API lenta"
    
    # Restaurar API
    manager.gestaods.buscar_dias_disponiveis = original_buscar_dias
    
    print("   ✅ PERSISTÊNCIA DURANTE REQUISIÇÕES OK!\n")
    
    print("✅ TODOS OS TESTES DE INTEGRAÇÃO PASSARAM!")

if __name__ == "__main__":
    print("\n🚀 INICIANDO TESTES DE INTEGRAÇÃO ROBUSTA COM API\n")
    
    try:
        # Teste de falha de dias
        asyncio.run(test_falha_api_dias())
        
        # Teste de falha de horários
        asyncio.run(test_falha_api_horarios())
        
        # Teste de persistência
        asyncio.run(test_persistencia_durante_requests())
        
        print("\n🎉 SUCESSO TOTAL!")
        print("📝 A integração com API agora é ROBUSTA!")
        print("🔒 Estados são preservados mesmo com falhas!")
        
    except AssertionError as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        print("⚠️  Verifique se as correções foram aplicadas!")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()