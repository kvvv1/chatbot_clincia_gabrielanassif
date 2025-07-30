#!/usr/bin/env python3
"""
Teste para verificar o fluxo completo da opção 2 (ver agendamentos)
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_fluxo_opcao_2():
    """Testa o fluxo completo da opção 2 - ver agendamentos"""
    
    # URL do webhook
    webhook_url = "https://chatbot-clincia-r4z511cyt-codexys-projects.vercel.app/webhook"
    
    # Simular número de telefone de teste
    test_phone = "5531999999999"
    
    print("🧪 TESTE DO FLUXO COMPLETO - OPÇÃO 2")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Teste 1: Enviar "oi" para iniciar conversa
        print("\n1️⃣ Enviando 'oi' para iniciar conversa...")
        
        payload_oi = {
            "type": "ReceivedCallback",
            "phone": test_phone,
            "text": {"message": "oi"},
            "messageId": "test_oi_001",
            "fromMe": False
        }
        
        response_oi = await client.post(webhook_url, json=payload_oi)
        print(f"Status: {response_oi.status_code}")
        print(f"Resposta: {response_oi.text}")
        
        await asyncio.sleep(3)
        
        # Teste 2: Enviar "2" para escolher ver agendamentos
        print("\n2️⃣ Enviando '2' para ver agendamentos...")
        
        payload_2 = {
            "type": "ReceivedCallback",
            "phone": test_phone,
            "text": {"message": "2"},
            "messageId": "test_2_001",
            "fromMe": False
        }
        
        response_2 = await client.post(webhook_url, json=payload_2)
        print(f"Status: {response_2.status_code}")
        print(f"Resposta: {response_2.text}")
        
        await asyncio.sleep(3)
        
        # Teste 3: Enviar CPF de teste
        print("\n3️⃣ Enviando CPF de teste...")
        
        payload_cpf = {
            "type": "ReceivedCallback",
            "phone": test_phone,
            "text": {"message": "12345678901"},
            "messageId": "test_cpf_001",
            "fromMe": False
        }
        
        response_cpf = await client.post(webhook_url, json=payload_cpf)
        print(f"Status: {response_cpf.status_code}")
        print(f"Resposta: {response_cpf.text}")
        
        await asyncio.sleep(3)
        
        # Teste 4: Enviar "1" para voltar ao menu
        print("\n4️⃣ Enviando '1' para voltar ao menu...")
        
        payload_voltar = {
            "type": "ReceivedCallback",
            "phone": test_phone,
            "text": {"message": "1"},
            "messageId": "test_voltar_001",
            "fromMe": False
        }
        
        response_voltar = await client.post(webhook_url, json=payload_voltar)
        print(f"Status: {response_voltar.status_code}")
        print(f"Resposta: {response_voltar.text}")
        
        print("\n✅ Teste concluído!")
        print("\n📋 Resumo esperado:")
        print("- Teste 1 (oi): Deveria mostrar o menu principal")
        print("- Teste 2 (2): Deveria pedir CPF para ver agendamentos")
        print("- Teste 3 (CPF): Deveria processar o CPF e mostrar agendamentos")
        print("- Teste 4 (1): Deveria voltar ao menu principal")

if __name__ == "__main__":
    asyncio.run(test_fluxo_opcao_2()) 