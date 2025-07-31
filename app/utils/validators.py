import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ValidatorUtils:
    """Utilidades de validação robustas"""
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """
        Valida CPF com algoritmo completo
        Aceita com ou sem formatação
        """
        try:
            # Remove caracteres não numéricos
            cpf_limpo = ''.join(filter(str.isdigit, cpf))
            
            # Verifica se tem 11 dígitos
            if len(cpf_limpo) != 11:
                return False
            
            # Verifica se todos os dígitos são iguais
            if cpf_limpo == cpf_limpo[0] * 11:
                return False
            
            # Validação do primeiro dígito verificador
            soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto
            
            if int(cpf_limpo[9]) != digito1:
                return False
            
            # Validação do segundo dígito verificador
            soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto
            
            if int(cpf_limpo[10]) != digito2:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar CPF: {str(e)}")
            return False
    
    @staticmethod
    def formatar_cpf(cpf: str) -> str:
        """Formata CPF para exibição (XXX.XXX.XXX-XX)"""
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) == 11:
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return cpf
    
    @staticmethod
    def validar_telefone(telefone: str) -> bool:
        """
        Valida número de telefone brasileiro
        Aceita: (11) 98765-4321, 11987654321, 5511987654321
        """
        try:
            # Remove caracteres não numéricos
            tel_limpo = ''.join(filter(str.isdigit, telefone))
            
            # Remove código do país se houver
            if tel_limpo.startswith('55') and len(tel_limpo) > 11:
                tel_limpo = tel_limpo[2:]
            
            # Verifica se tem 10 ou 11 dígitos (com ou sem 9)
            if len(tel_limpo) not in [10, 11]:
                return False
            
            # Verifica se o DDD é válido (11-99)
            ddd = int(tel_limpo[:2])
            if ddd < 11 or ddd > 99:
                return False
            
            # Se tem 11 dígitos, o terceiro deve ser 9
            if len(tel_limpo) == 11 and tel_limpo[2] != '9':
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao validar telefone: {str(e)}")
            return False
    
    @staticmethod
    def formatar_telefone(telefone: str) -> str:
        """Formata telefone para exibição"""
        tel_limpo = ''.join(filter(str.isdigit, telefone))
        
        # Remove código do país se houver
        if tel_limpo.startswith('55') and len(tel_limpo) > 11:
            tel_limpo = tel_limpo[2:]
        
        if len(tel_limpo) == 11:
            return f"({tel_limpo[:2]}) {tel_limpo[2:7]}-{tel_limpo[7:]}"
        elif len(tel_limpo) == 10:
            return f"({tel_limpo[:2]}) {tel_limpo[2:6]}-{tel_limpo[6:]}"
        
        return telefone
    
    @staticmethod
    def validar_data(data_str: str, formato: str = "%d/%m/%Y") -> bool:
        """Valida se string é uma data válida"""
        try:
            datetime.strptime(data_str, formato)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validar_horario(horario_str: str) -> bool:
        """Valida se string é um horário válido (HH:MM)"""
        try:
            # Aceita HH:MM ou HH:MM:SS
            if ':' not in horario_str:
                return False
            
            partes = horario_str.split(':')
            if len(partes) < 2:
                return False
            
            hora = int(partes[0])
            minuto = int(partes[1])
            
            if hora < 0 or hora > 23:
                return False
            if minuto < 0 or minuto > 59:
                return False
            
            return True
            
        except:
            return False
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validar_nome(nome: str) -> Tuple[bool, Optional[str]]:
        """
        Valida nome completo
        Retorna (is_valid, error_message)
        """
        if not nome or not nome.strip():
            return False, "Nome não pode estar vazio"
        
        nome = nome.strip()
        
        # Verifica se tem pelo menos 3 caracteres
        if len(nome) < 3:
            return False, "Nome muito curto"
        
        # Verifica se tem números
        if any(char.isdigit() for char in nome):
            return False, "Nome não pode conter números"
        
        # Verifica se tem pelo menos nome e sobrenome
        partes = nome.split()
        if len(partes) < 2:
            return False, "Por favor, informe nome e sobrenome"
        
        # Verifica se cada parte tem pelo menos 2 caracteres
        for parte in partes:
            if len(parte) < 2:
                return False, "Cada parte do nome deve ter pelo menos 2 caracteres"
        
        return True, None
    
    @staticmethod
    def sanitizar_entrada(texto: str) -> str:
        """
        Sanitiza entrada do usuário removendo caracteres perigosos
        """
        if not texto:
            return ""
        
        # Remove caracteres de controle
        texto = ''.join(char for char in texto if ord(char) >= 32)
        
        # Remove excesso de espaços
        texto = ' '.join(texto.split())
        
        # Limita tamanho
        if len(texto) > 1000:
            texto = texto[:1000]
        
        return texto.strip()
    
    @staticmethod
    def validar_opcao_menu(opcao: str, opcoes_validas: list) -> bool:
        """Valida se opção está entre as válidas"""
        return opcao.strip() in opcoes_validas
    
    @staticmethod
    def extrair_numeros(texto: str) -> str:
        """Extrai apenas números de uma string"""
        return ''.join(filter(str.isdigit, texto))
    
    @staticmethod
    def validar_data_futura(data_str: str, formato: str = "%d/%m/%Y") -> Tuple[bool, Optional[str]]:
        """
        Valida se data é futura
        Retorna (is_valid, error_message)
        """
        try:
            data = datetime.strptime(data_str, formato)
            hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if data.date() < hoje.date():
                return False, "Data não pode ser no passado"
            
            # Verifica se não é muito no futuro (1 ano)
            limite = hoje + timedelta(days=365)
            if data > limite:
                return False, "Data muito distante (máximo 1 ano)"
            
            return True, None
            
        except ValueError:
            return False, "Data inválida"

def validate_cpf(cpf: str) -> bool:
    """Função compatível para validação de CPF"""
    return ValidatorUtils.validar_cpf(cpf)