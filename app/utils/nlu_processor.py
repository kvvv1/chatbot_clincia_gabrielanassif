import re
from typing import Dict, List, Optional, Tuple
import unicodedata
import logging

logger = logging.getLogger(__name__)

class NLUProcessor:
    """Processador de Linguagem Natural para entender intenções do usuário"""
    
    def __init__(self):
        self.intents = self._load_intents()
        self.entities = self._load_entities()
    
    def _load_intents(self) -> Dict[str, List[str]]:
        """Carrega padrões de intenções"""
        return {
            'saudacao': [
                r'\b(oi|ola|olá|bom\s*dia|boa\s*tarde|boa\s*noite|hey|hello|e\s*ai|eai)\b',
                r'^(oi|olá|ola)$'
            ],
            'agendar': [
                r'\b(agendar|marcar|marca|agenda|consulta|horario|horário|atendimento)\b',
                r'\b(quero|preciso|gostaria)\s+(de\s+)?(agendar|marcar|uma\s+consulta)\b',
                r'\b(tem\s+vaga|tem\s+horario|tem\s+horário)\b'
            ],
            'visualizar': [
                r'\b(ver|visualizar|olhar|conferir|checar)\s+(meus?\s+)?(agendamentos?|consultas?|horarios?|horários?)\b',
                r'\b(tenho|tem)\s+(consulta|agendamento|horario|horário)\b',
                r'\b(quando|qual)\s+(é\s+)?(minha|meu)\s+(consulta|agendamento)\b'
            ],
            'cancelar': [
                r'\b(cancelar|desmarcar|desistir|cancela)\s*(consulta|agendamento|horario|horário)?\b',
                r'\b(não\s+vou|nao\s+vou)\s+(poder|conseguir)\s+(ir|comparecer)\b',
                r'\b(quero|preciso|gostaria)\s+(de\s+)?cancelar\b'
            ],
            'reagendar': [
                r'\b(reagendar|remarcar|mudar|alterar|trocar)\s*(data|horario|horário|consulta|agendamento)?\b',
                r'\b(pode\s+ser|poderia\s+ser)\s+(outro|outra)\s+(dia|data|horario|horário)\b'
            ],
            'lista_espera': [
                r'\b(lista\s+de?\s*espera|fila\s+de?\s*espera|espera|aguardar)\b',
                r'\b(me\s+)?avisa(r)?\s+(quando|se)\s+(tiver|houver|surgir)\s+(vaga|horario|horário)\b',
                r'\b(entrar|colocar|adicionar)\s+(na\s+)?(lista|fila)\b'
            ],
            'ajuda': [
                r'\b(ajuda|ajudar|help|duvida|dúvida|como\s+funciona|o\s+que\s+fazer)\b',
                r'\b(não\s+sei|nao\s+sei|não\s+entendi|nao\s+entendi)\b',
                r'\b(pode\s+me\s+ajudar|preciso\s+de\s+ajuda)\b'
            ],
            'confirmacao': [
                r'\b(sim|s|confirmo|confirmar|ok|okay|certo|certeza|pode\s+ser|isso|exato)\b',
                r'^(sim|s|ok|1)$'
            ],
            'negacao': [
                r'\b(não|nao|n|negativo|cancelar|errado|incorreto)\b',
                r'^(não|nao|n|2)$'
            ],
            'despedida': [
                r'\b(tchau|tchauzinho|adeus|até\s+logo|ate\s+logo|sair|encerrar|finalizar)\b',
                r'^(tchau|sair|0)$'
            ],
            'atendente': [
                r'\b(atendente|humano|pessoa|alguem|alguém|falar\s+com)\b',
                r'\b(quero|preciso)\s+(falar|conversar)\s+com\s+(uma\s+)?(pessoa|atendente|humano)\b'
            ]
        }
    
    def _load_entities(self) -> Dict[str, List[str]]:
        """Carrega padrões de entidades"""
        return {
            'tempo': [
                r'\b(hoje|amanhã|amanha|depois\s+de\s+amanhã|semana\s+que\s+vem)\b',
                r'\b(segunda|terça|terca|quarta|quinta|sexta|sabado|sábado|domingo)\b',
                r'\b(manhã|manha|tarde|noite)\b',
                r'\b(\d{1,2})\s*(hora|h|:\d{2})\b'
            ],
            'urgencia': [
                r'\b(urgente|urgência|urgencia|emergencia|emergência|rapido|rápido|agora|já|ja)\b',
                r'\b(dor|doendo|mal\s+estar|febre|sangramento)\b'
            ],
            'cpf': [
                r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
                r'\b\d{11}\b'
            ],
            'telefone': [
                r'\b\(?\d{2}\)?\s*\d{4,5}-?\d{4}\b',
                r'\b\d{10,11}\b'
            ],
            'email': [
                r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
            ]
        }
    
    def process_message(self, message: str) -> Dict:
        """
        Processa mensagem e extrai intenções e entidades
        
        Returns:
            Dict com intent, entities, is_greeting, is_farewell, confidence
        """
        # Normalizar mensagem
        normalized = self._normalize_text(message)
        
        # Detectar intenção principal
        intent, confidence = self._detect_intent(normalized)
        
        # Extrair entidades
        entities = self._extract_entities(normalized)
        
        # Análise adicional
        sentiment = self._analyze_sentiment(normalized)
        is_question = self._is_question(normalized)
        
        result = {
            'original_message': message,
            'normalized_message': normalized,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'sentiment': sentiment,
            'is_question': is_question,
            'is_greeting': intent == 'saudacao',
            'is_farewell': intent == 'despedida'
        }
        
        logger.info(f"NLU Result: {result}")
        return result
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto removendo acentos e padronizando"""
        if not text:
            return ""
        
        # Converter para minúsculas
        text = text.lower().strip()
        
        # Remover acentos
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Remover múltiplos espaços
        text = ' '.join(text.split())
        
        return text
    
    def _detect_intent(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detecta a intenção principal da mensagem
        
        Returns:
            Tuple[intent, confidence]
        """
        best_intent = None
        best_confidence = 0.0
        
        # Verificar cada intenção
        for intent, patterns in self.intents.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Calcular confiança baseada no match
                    match = re.search(pattern, text, re.IGNORECASE)
                    match_ratio = len(match.group()) / len(text)
                    confidence = min(match_ratio * 1.5, 1.0)  # Max 100%
                    
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence
        
        # Se não encontrou intenção clara, tentar classificar por contexto
        if not best_intent:
            best_intent, best_confidence = self._classify_by_context(text)
        
        return best_intent, best_confidence
    
    def _classify_by_context(self, text: str) -> Tuple[Optional[str], float]:
        """Classifica por contexto quando não há match direto"""
        # Se é só um número, pode ser opção de menu
        if text.strip().isdigit():
            return 'menu_selection', 0.8
        
        # Se tem interrogação, provavelmente é pergunta/ajuda
        if '?' in text:
            return 'ajuda', 0.6
        
        # Se é muito curto, pode ser confirmação/negação
        if len(text.split()) <= 2:
            if any(word in text for word in ['sim', 's', 'ok', 'certo']):
                return 'confirmacao', 0.7
            elif any(word in text for word in ['nao', 'não', 'n']):
                return 'negacao', 0.7
        
        return None, 0.0
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrai entidades da mensagem"""
        extracted = {}
        
        for entity_type, patterns in self.entities.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                extracted[entity_type] = list(set(matches))  # Remove duplicatas
        
        return extracted
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analisa sentimento básico da mensagem"""
        positive_words = [
            'obrigado', 'obrigada', 'otimo', 'ótimo', 'excelente', 
            'maravilhoso', 'perfeito', 'agradeço', 'agradeco'
        ]
        
        negative_words = [
            'ruim', 'pessimo', 'péssimo', 'horrivel', 'horrível',
            'problema', 'erro', 'não funciona', 'nao funciona',
            'demora', 'lento', 'travado'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _is_question(self, text: str) -> bool:
        """Verifica se é uma pergunta"""
        question_patterns = [
            r'\?$',
            r'^(qual|quais|quando|onde|como|por\s*que|porque|quem|quanto)\b',
            r'\b(pode|posso|consigo|tem|têm|tem|existe|há|ha)\b.*\?'
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in question_patterns)
    
    def extract_time_references(self, text: str) -> List[Dict[str, str]]:
        """Extrai referências temporais da mensagem"""
        references = []
        
        # Dias da semana
        dias = {
            'segunda': 0, 'terça': 1, 'terca': 1, 'quarta': 2,
            'quinta': 3, 'sexta': 4, 'sabado': 5, 'sábado': 5, 'domingo': 6
        }
        
        for dia, num in dias.items():
            if dia in text:
                references.append({
                    'type': 'weekday',
                    'value': dia,
                    'weekday_num': num
                })
        
        # Períodos do dia
        if 'manhã' in text or 'manha' in text:
            references.append({'type': 'period', 'value': 'morning'})
        elif 'tarde' in text:
            references.append({'type': 'period', 'value': 'afternoon'})
        elif 'noite' in text:
            references.append({'type': 'period', 'value': 'evening'})
        
        # Referências relativas
        if 'hoje' in text:
            references.append({'type': 'relative', 'value': 'today'})
        elif 'amanhã' in text or 'amanha' in text:
            references.append({'type': 'relative', 'value': 'tomorrow'})
        
        return references