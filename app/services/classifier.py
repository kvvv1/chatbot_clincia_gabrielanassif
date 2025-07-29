import re
from typing import List, Dict, Tuple
from datetime import datetime
import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ConversationClassifier:
    def __init__(self):
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict:
        """Carrega padrões para classificação baseada em regras"""
        return {
            'agendamento_sucesso': [
                r'consulta agendada com sucesso',
                r'agendamento confirmado',
                r'confirmou.*agendamento',
                r'ok.*agendado',
                r'perfeito.*agendamento'
            ],
            'agendamento_erro': [
                r'erro ao agendar',
                r'não.*consegui.*agendar',
                r'problema.*agendamento',
                r'não.*funcionou',
                r'erro.*sistema'
            ],
            'cancelamento': [
                r'cancelar.*consulta',
                r'desmarcar',
                r'não.*poder.*comparecer',
                r'cancelamento',
                r'desmarcar.*consulta'
            ],
            'urgente': [
                r'urgente',
                r'emergência',
                r'dor.*forte',
                r'preciso.*hoje',
                r'emergência',
                r'urgente.*consulta'
            ],
            'reclamacao': [
                r'reclamar',
                r'insatisfeito',
                r'péssimo',
                r'horrível',
                r'demora',
                r'mal.*atendimento',
                r'problema.*atendimento'
            ],
            'novo_paciente': [
                r'primeira vez',
                r'novo paciente',
                r'não.*cadastrado',
                r'realizar.*cadastro',
                r'primeira.*consulta',
                r'novo.*paciente'
            ],
            'duvida': [
                r'quanto custa',
                r'qual.*valor',
                r'convênio',
                r'aceita.*plano',
                r'como.*funciona',
                r'horário.*atendimento',
                r'endereço',
                r'telefone'
            ],
            'confirmacao': [
                r'confirmar',
                r'confirmar.*consulta',
                r'confirmar.*agendamento',
                r'confirmar.*horário'
            ],
            'reagendamento': [
                r'reagendar',
                r'mudar.*data',
                r'mudar.*horário',
                r'outro.*dia',
                r'outro.*horário'
            ],
            'lista_espera': [
                r'lista.*espera',
                r'espera',
                r'quando.*vaga',
                r'disponibilidade'
            ]
        }
    
    async def analyze_conversation(self, messages: List[Dict]) -> Dict:
        """Analisa conversa completa e retorna classificação"""
        
        # Juntar todas as mensagens
        full_text = " ".join([msg['message'].lower() for msg in messages])
        
        # Análise baseada em regras
        tags = self._extract_tags(full_text)
        priority = self._calculate_priority(tags, messages)
        sentiment = self._analyze_sentiment(messages)
        
        # Análise com IA (se configurado)
        ai_analysis = await self._ai_analysis(messages) if hasattr(settings, 'use_ai_classifier') and settings.use_ai_classifier else {}
        
        # Resumo e ação sugerida
        summary = ai_analysis.get('summary', self._generate_summary(messages))
        suggested_action = ai_analysis.get('action', self._suggest_action(tags))
        
        return {
            'tags': tags,
            'priority': priority,
            'sentiment_score': sentiment,
            'ai_summary': summary,
            'ai_suggested_action': suggested_action,
            'requires_attention': self._requires_human_attention(tags, sentiment)
        }
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extrai tags baseadas em padrões"""
        tags = []
        
        for tag, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    tags.append(tag)
                    break
        
        return list(set(tags))
    
    def _calculate_priority(self, tags: List[str], messages: List[Dict]) -> int:
        """Calcula prioridade da conversa"""
        
        # Urgente
        if 'urgente' in tags or 'reclamacao' in tags:
            return 3
        
        # Alta - problemas ou novos pacientes
        if 'agendamento_erro' in tags or 'novo_paciente' in tags:
            return 2
        
        # Média - ações pendentes
        if 'cancelamento' in tags or 'reagendamento' in tags:
            return 1
        
        # Baixa - sucesso ou dúvidas simples
        return 0
    
    def _analyze_sentiment(self, messages: List[Dict]) -> int:
        """Analisa sentimento da conversa (-100 a 100)"""
        
        positive_words = ['obrigado', 'obrigada', 'ótimo', 'excelente', 'perfeito', 'maravilhoso', 'obrigado', 'valeu', 'legal']
        negative_words = ['ruim', 'péssimo', 'horrível', 'demora', 'problema', 'erro', 'cancelar', 'insatisfeito', 'reclamar']
        
        score = 0
        for msg in messages:
            if msg['sender'] == 'user':
                text = msg['message'].lower()
                
                for word in positive_words:
                    if word in text:
                        score += 20
                
                for word in negative_words:
                    if word in text:
                        score -= 20
        
        return max(-100, min(100, score))
    
    def _generate_summary(self, messages: List[Dict]) -> str:
        """Gera resumo simples da conversa"""
        if not messages:
            return "Conversa vazia"
        
        user_messages = [m for m in messages if m['sender'] == 'user']
        
        if len(user_messages) == 0:
            return "Sem mensagens do usuário"
        
        first_msg = user_messages[0]['message'][:100]
        return f"Conversa iniciada com: {first_msg}..."
    
    def _suggest_action(self, tags: List[str]) -> str:
        """Sugere ação baseada nas tags"""
        
        if 'agendamento_erro' in tags:
            return "Verificar problema no agendamento e entrar em contato"
        
        if 'reclamacao' in tags:
            return "Priorizar atendimento e resolver insatisfação"
        
        if 'novo_paciente' in tags:
            return "Orientar sobre processo de cadastro"
        
        if 'cancelamento' in tags:
            return "Confirmar cancelamento e liberar horário"
        
        if 'urgente' in tags:
            return "Atendimento imediato necessário"
        
        if 'duvida' in tags:
            return "Responder dúvidas sobre serviços"
        
        if 'confirmacao' in tags:
            return "Confirmar detalhes do agendamento"
        
        return "Monitorar conversa"
    
    def _requires_human_attention(self, tags: List[str], sentiment: int) -> bool:
        """Determina se precisa de atenção humana"""
        
        attention_tags = ['urgente', 'reclamacao', 'agendamento_erro', 'novo_paciente']
        
        # Precisa atenção se tem tags críticas ou sentimento muito negativo
        return any(tag in attention_tags for tag in tags) or sentiment < -50
    
    async def _ai_analysis(self, messages: List[Dict]) -> Dict:
        """Análise usando IA (OpenAI/Local)"""
        try:
            # Preparar contexto
            conversation = "\n".join([
                f"{msg['sender']}: {msg['message']}" 
                for msg in messages[-10:]  # Últimas 10 mensagens
            ])
            
            prompt = f"""
            Analise esta conversa de WhatsApp de uma clínica médica:
            
            {conversation}
            
            Retorne um JSON com:
            1. summary: Resumo em uma linha
            2. action: Ação recomendada para secretaria
            3. category: Categoria principal (agendamento/cancelamento/dúvida/reclamação)
            4. urgency: true/false se é urgente
            """
            
            # Aqui você pode integrar com OpenAI ou outro modelo
            # Por enquanto, retornamos análise baseada em regras
            return {}
            
        except Exception as e:
            logger.error(f"Erro na análise IA: {str(e)}")
            return {} 