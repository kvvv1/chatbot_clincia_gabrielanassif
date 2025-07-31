"""
Teste do fluxo de confirmação de paciente - verifica se está alinhado com os exemplos
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.conversation import ConversationManager
from app.models.database import get_db, Conversation
from datetime import datetime

async def test_confirmacao_paciente():
    """Testa o fluxo completo de confirmação de paciente"""
    manager = ConversationManager()
    db = next(get_db())
    phone = "5511999888777"
    
    print("🧪 TESTANDO FLUXO DE CONFIRMAÇÃO DE PACIENTE\n")
    print("=" * 60)
    
    # Limpar conversas antigas
    try:
        conv_antiga = db.query(Conversation).filter_by(phone=phone).first()
        if conv_antiga:
            db.delete(conv_antiga)
            db.commit()
    except:
        pass
    
    # Mock da API de paciente para retornar paciente válido
    # Usar CPF válido real: 11144477735
    cpf_valido = "11144477735"
    paciente_mock = {
        "nome": "João Silva",
        "cpf": cpf_valido,
        "id": "123"
    }
    original_buscar_paciente = manager.gestaods.buscar_paciente_cpf
    async def api_paciente_mock(cpf):
        return paciente_mock
    manager.gestaods.buscar_paciente_cpf = api_paciente_mock
    
    # 1. Iniciar conversa
    print("1️⃣ INICIANDO CONVERSA")
    print("-" * 40)
    await manager.processar_mensagem(phone, "oi", "msg1", db)
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado: {conversa.state}")
    assert conversa.state == "menu_principal"
    print("   ✅ Menu mostrado\n")
    
    # 2. Escolher opção 1 (Agendar)
    print("2️⃣ ESCOLHENDO OPÇÃO 1 (Agendar)")
    print("-" * 40)
    await manager.processar_mensagem(phone, "1", "msg2", db)
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado: {conversa.state}")
    print(f"   ✅ Contexto: {conversa.context}")
    assert conversa.state == "aguardando_cpf"
    assert conversa.context.get('acao') == 'agendar'
    print("   ✅ Aguardando CPF\n")
    
    # 3. Enviar CPF válido
    print("3️⃣ ENVIANDO CPF VÁLIDO")
    print("-" * 40)
    print(f"   📝 Debug: Enviando CPF válido: {cpf_valido}")
    await manager.processar_mensagem(phone, cpf_valido, "msg3", db)
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado: {conversa.state}")
    print(f"   ✅ Contexto: {conversa.context}")
    print(f"   📝 Debug: Paciente encontrado: {conversa.context.get('paciente_temp', 'Não encontrado')}")
    
    # Verificar se entrou em confirmação
    assert conversa.state == "confirmando_paciente", f"Estado deveria ser 'confirmando_paciente', mas é '{conversa.state}'"
    assert 'paciente_temp' in conversa.context, "Deve ter paciente_temp no contexto"
    assert conversa.context['paciente_temp']['nome'] == "João Silva", "Nome do paciente deve estar correto"
    
    print("   ✅ Paciente encontrado, aguardando confirmação!\n")
    
    # 4. Confirmar paciente (opção 1)
    print("4️⃣ CONFIRMANDO PACIENTE (Opção 1)")
    print("-" * 40)
    await manager.processar_mensagem(phone, "1", "msg4", db)
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado: {conversa.state}")
    print(f"   ✅ Contexto: {conversa.context}")
    
    # Verificar se o paciente foi confirmado e o fluxo continuou
    assert 'paciente' in conversa.context, "Paciente deve estar confirmado no contexto"
    assert 'paciente_temp' not in conversa.context, "paciente_temp deve ter sido removido"
    assert conversa.context['paciente']['nome'] == "João Silva", "Paciente confirmado deve ter nome correto"
    assert conversa.context.get('acao') == 'agendar', "Ação deve ser mantida"
    
    print("   ✅ Paciente confirmado e fluxo continuou!\n")
    
    print("=" * 60)
    print("✅ TESTE DE CONFIRMAÇÃO DE PACIENTE PASSOU!")
    print("✅ Fluxo agora está alinhado com os exemplos!")

async def test_rejeicao_paciente():
    """Testa quando usuário rejeita o paciente encontrado"""
    manager = ConversationManager()
    db = next(get_db())
    phone = "5511777666555"
    
    print("\n🧪 TESTANDO REJEIÇÃO DE PACIENTE\n")
    print("=" * 60)
    
    # Limpar conversas antigas
    try:
        conv_antiga = db.query(Conversation).filter_by(phone=phone).first()
        if conv_antiga:
            db.delete(conv_antiga)
            db.commit()
    except:
        pass
    
    # Mock da API
    paciente_mock = {
        "nome": "Maria Santos",
        "cpf": "98765432100",
        "id": "456"
    }
    async def api_paciente_mock(cpf):
        return paciente_mock
    manager.gestaods.buscar_paciente_cpf = api_paciente_mock
    
    # Setup inicial
    conversa = Conversation(
        phone=phone,
        state="confirmando_paciente",
        context={
            "acao": "agendar",
            "paciente_temp": paciente_mock
        }
    )
    db.add(conversa)
    db.commit()
    
    print("1️⃣ REJEITANDO PACIENTE (Opção 2)")
    print("-" * 40)
    await manager.processar_mensagem(phone, "2", "msg1", db)
    
    conversa = manager._get_or_create_conversation(phone, db)
    print(f"   ✅ Estado: {conversa.state}")
    print(f"   ✅ Contexto: {conversa.context}")
    
    # Verificar se voltou para aguardar CPF
    assert conversa.state == "aguardando_cpf", f"Estado deveria ser 'aguardando_cpf', mas é '{conversa.state}'"
    assert 'paciente_temp' not in conversa.context, "paciente_temp deve ter sido removido"
    assert conversa.context.get('acao') == 'agendar', "Ação deve ser mantida"
    
    print("   ✅ Voltou para aguardar CPF corretamente!\n")
    
    print("✅ TESTE DE REJEIÇÃO PASSOU!")

async def test_formatacao_cpf():
    """Testa formatação de CPF"""
    manager = ConversationManager()
    
    print("\n🧪 TESTANDO FORMATAÇÃO DE CPF\n")
    print("=" * 60)
    
    # Testar formatação
    cpf_formatado = manager._formatar_cpf_display("12345678901")
    print(f"CPF: 12345678901 → {cpf_formatado}")
    assert cpf_formatado == "123.456.789-01", f"Formatação incorreta: {cpf_formatado}"
    
    # Testar com CPF já formatado
    cpf_formatado2 = manager._formatar_cpf_display("123.456.789-01")
    print(f"CPF: 123.456.789-01 → {cpf_formatado2}")
    assert cpf_formatado2 == "123.456.789-01", f"Formatação incorreta: {cpf_formatado2}"
    
    # Testar CPF inválido
    cpf_formatado3 = manager._formatar_cpf_display("123456")
    print(f"CPF: 123456 → {cpf_formatado3}")
    assert cpf_formatado3 == "123456", f"CPF inválido deve retornar original: {cpf_formatado3}"
    
    print("   ✅ Formatação de CPF funcionando corretamente!\n")
    
    print("✅ TESTE DE FORMATAÇÃO PASSOU!")

if __name__ == "__main__":
    print("\n🚀 INICIANDO TESTES DE CONFIRMAÇÃO DE PACIENTE\n")
    
    try:
        # Teste principal
        asyncio.run(test_confirmacao_paciente())
        
        # Teste de rejeição
        asyncio.run(test_rejeicao_paciente())
        
        # Teste de formatação
        asyncio.run(test_formatacao_cpf())
        
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("📝 O fluxo agora está 100% alinhado com os exemplos!")
        print("✅ Confirmação de paciente implementada com sucesso!")
        
    except AssertionError as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        print("⚠️  Verifique se as correções foram aplicadas corretamente!")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()