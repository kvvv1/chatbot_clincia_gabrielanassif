import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NLUProcessor:
    """Processador de Linguagem Natural para entender intenções do usuário"""
    
    def __init__(self):
        # Padrões de intenções
        self.intent_patterns = {
            'agendar': [
                r'\b(agendar|marcar|marcar consulta|agendamento|agenda|consulta|marcar horário)\b',
                r'\b(quero|preciso|gostaria|desejo)\s+(agendar|marcar|fazer)\s+(consulta|agendamento)\b',
                r'\b(consulta|agendamento)\s+(por favor|pfv)\b'
            ],
            'visualizar': [
                r'\b(ver|visualizar|consultar|mostrar|listar)\s+(agendamentos?|consultas?|horários?)\b',
                r'\b(quais|quando)\s+(são|tenho)\s+(minhas?\s+)?(consultas?|agendamentos?)\b',
                r'\b(agenda|horários?)\s+(disponíveis?|livres?)\b'
            ],
            'cancelar': [
                r'\b(cancelar|cancelamento|desmarcar|remover)\s+(consulta|agendamento)\b',
                r'\b(não\s+)?(posso|consigo|quero)\s+(ir|comparecer|fazer)\s+(a\s+)?(consulta|agendamento)\b',
                r'\b(desistir|desistência)\s+(da\s+)?(consulta|agendamento)\b'
            ],
            'lista_espera': [
                r'\b(lista\s+de\s+espera|fila|espera|aguardar)\b',
                r'\b(não\s+)?(tem|há|existe)\s+(horário|vaga|disponibilidade)\b',
                r'\b(quando|quando\s+que)\s+(vai\s+)?(ter|abrir)\s+(vaga|horário)\b'
            ],
            'atendente': [
                r'\b(falar|conversar|atender|atendimento)\s+(com|ao)\s+(atendente|humano|pessoa)\b',
                r'\b(atendente|humano|pessoa)\s+(por favor|pfv)\b',
                r'\b(não\s+)?(consigo|posso)\s+(resolver|fazer)\s+(sozinho|aqui)\b'
            ],
            'ajuda': [
                r'\b(ajuda|socorro|help|auxílio|suporte)\b',
                r'\b(não\s+)?(entendi|compreendi|sei)\s+(como|o\s+que)\b',
                r'\b(menu|opções?|comandos?)\b'
            ],
            'confirmar': [
                r'\b(sim|confirmar|confirmado|ok|beleza|blz|tá|ta|claro|certeza)\b',
                r'\b(quero|aceito|concordo|perfeito|ótimo|excelente)\b'
            ],
            'negar': [
                r'\b(não|n|negativo|cancelar|desistir|voltar)\b',
                r'\b(não\s+quero|não\s+aceito|não\s+concordo)\b'
            ]
        }
        
        # Padrões de entidades
        self.entity_patterns = {
            'cpf': [
                r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
                r'\b\d{11}\b'
            ],
            'data': [
                r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',
                r'\b(hoje|amanhã|depois\s+de\s+amanhã)\b',
                r'\b(segunda|terça|quarta|quinta|sexta|sábado|domingo)\s+(feira)?\b'
            ],
            'hora': [
                r'\b(\d{1,2}):(\d{2})\s*(h|hr|hrs)?\b',
                r'\b(\d{1,2})h(\d{2})?\b'
            ],
            'numero': [
                r'\b(\d+)\b'
            ]
        }
        
        # Mapeamento de sinônimos
        self.synonyms = {
            'agendar': ['marcar', 'agendamento', 'consulta', 'marcação'],
            'visualizar': ['ver', 'consultar', 'mostrar', 'listar'],
            'cancelar': ['desmarcar', 'remover', 'cancelamento'],
            'atendente': ['humano', 'pessoa', 'atendimento'],
            'sim': ['ok', 'beleza', 'blz', 'tá', 'ta', 'claro', 'perfeito'],
            'nao': ['não', 'n', 'negativo', 'cancelar']
        }

    def extract_intent(self, message: str) -> Tuple[str, float]:
        """Extrai a intenção principal da mensagem com score de confiança"""
        message_lower = message.lower().strip()
        
        best_intent = None
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, message_lower, re.IGNORECASE)
                if matches:
                    # Score baseado no número de matches e comprimento
                    score = len(matches) * 0.5 + (len(pattern) / 100)
                    if score > best_score:
                        best_score = score
                        best_intent = intent
        
        # Fallback para mensagens que não correspondem a padrões específicos
        if not best_intent:
            if any(word in message_lower for word in ['oi', 'olá', 'ola', 'hi', 'hello']):
                best_intent = 'saudacao'
                best_score = 0.8
            elif len(message_lower.split()) <= 2:
                best_intent = 'numero_opcao'
                best_score = 0.6
        
        return best_intent or 'desconhecida', best_score

    def extract_entities(self, message: str) -> Dict[str, List[str]]:
        """Extrai entidades da mensagem (CPF, datas, números, etc.)"""
        entities = {}
        message_lower = message.lower().strip()
        
        # Extrair CPF
        cpf_matches = re.findall(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}', message)
        if cpf_matches:
            entities['cpf'] = [cpf.replace('.', '').replace('-', '') for cpf in cpf_matches]
        
        # Extrair números (opções de menu)
        numero_matches = re.findall(r'\b(\d+)\b', message)
        if numero_matches:
            entities['numero'] = numero_matches
        
        # Extrair datas
        data_matches = re.findall(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b', message)
        if data_matches:
            entities['data'] = [f"{d[0]}/{d[1]}/{d[2]}" for d in data_matches]
        
        # Extrair horários
        hora_matches = re.findall(r'\b(\d{1,2}):(\d{2})\s*(h|hr|hrs)?\b', message)
        if hora_matches:
            entities['hora'] = [f"{h[0]}:{h[1]}" for h in hora_matches]
        
        return entities

    def normalize_message(self, message: str) -> str:
        """Normaliza a mensagem removendo acentos e caracteres especiais"""
        import unicodedata
        
        # Remove acentos
        message = unicodedata.normalize('NFD', message)
        message = ''.join(c for c in message if not unicodedata.combining(c))
        
        # Converte para minúsculas e remove espaços extras
        message = message.lower().strip()
        
        # Remove caracteres especiais mantendo números e letras
        message = re.sub(r'[^\w\s\d]', ' ', message)
        message = re.sub(r'\s+', ' ', message)
        
        return message.strip()

    def is_affirmative(self, message: str) -> bool:
        """Verifica se a mensagem é afirmativa"""
        message_lower = message.lower().strip()
        affirmative_words = ['sim', 'ok', 'beleza', 'blz', 'tá', 'ta', 'claro', 'perfeito', 'ótimo', 'excelente', 'quero', 'aceito', 'concordo']
        return any(word in message_lower for word in affirmative_words)

    def is_negative(self, message: str) -> bool:
        """Verifica se a mensagem é negativa"""
        message_lower = message.lower().strip()
        negative_words = ['não', 'nao', 'n', 'negativo', 'cancelar', 'desistir', 'voltar', 'não quero', 'nao quero']
        return any(word in message_lower for word in negative_words)

    def extract_menu_option(self, message: str) -> Optional[int]:
        """Extrai opção de menu da mensagem"""
        message_lower = message.lower().strip()
        
        # Buscar por números
        numero_matches = re.findall(r'\b(\d+)\b', message_lower)
        if numero_matches:
            try:
                return int(numero_matches[0])
            except ValueError:
                pass
        
        # Buscar por palavras que representam números
        numero_words = {
            'um': 1, 'uma': 1, 'primeiro': 1, 'primeira': 1,
            'dois': 2, 'duas': 2, 'segundo': 2, 'segunda': 2,
            'três': 3, 'tres': 3, 'terceiro': 3, 'terceira': 3,
            'quatro': 4, 'quarta': 4,
            'cinco': 5, 'quinta': 5,
            'seis': 6, 'sexta': 6,
            'sete': 7, 'sétimo': 7, 'setimo': 7,
            'oito': 8, 'oitavo': 8,
            'nove': 9, 'nono': 9,
            'dez': 10, 'décimo': 10, 'decimo': 10
        }
        
        for word, numero in numero_words.items():
            if word in message_lower:
                return numero
        
        return None

    def is_greeting(self, message: str) -> bool:
        """Verifica se é uma saudação"""
        message_lower = message.lower().strip()
        greetings = ['oi', 'olá', 'ola', 'hi', 'hello', 'bom dia', 'boa tarde', 'boa noite', 'fala']
        return any(greeting in message_lower for greeting in greetings)

    def is_farewell(self, message: str) -> bool:
        """Verifica se é uma despedida"""
        message_lower = message.lower().strip()
        farewells = ['tchau', 'bye', 'até logo', 'ate logo', 'obrigado', 'obrigada', 'valeu', 'vlw']
        return any(farewell in message_lower for farewell in farewells)

    def process_message(self, message: str) -> Dict:
        """Processa a mensagem completa e retorna análise estruturada"""
        normalized = self.normalize_message(message)
        intent, confidence = self.extract_intent(message)
        entities = self.extract_entities(message)
        
        return {
            'original': message,
            'normalized': normalized,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'is_affirmative': self.is_affirmative(message),
            'is_negative': self.is_negative(message),
            'is_greeting': self.is_greeting(message),
            'is_farewell': self.is_farewell(message),
            'menu_option': self.extract_menu_option(message)
        } 