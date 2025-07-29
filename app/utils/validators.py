import re
from datetime import datetime
from typing import Optional

class ValidatorUtils:

    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida CPF brasileiro"""
        # Remove caracteres não numéricos
        cpf = re.sub(r'[^0-9]', '', cpf)

        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False

        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False

        # Validação dos dígitos verificadores
        def calcular_digito(cpf_parcial):
            soma = 0
            for i, digito in enumerate(cpf_parcial):
                soma += int(digito) * (len(cpf_parcial) + 1 - i)
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)

        # Primeiro dígito
        if calcular_digito(cpf[:9]) != cpf[9]:
            return False

        # Segundo dígito
        if calcular_digito(cpf[:10]) != cpf[10]:
            return False

        return True

    @staticmethod
    def validar_telefone(telefone: str) -> bool:
        """Valida número de telefone brasileiro"""
        # Remove caracteres não numéricos
        telefone = re.sub(r'[^0-9]', '', telefone)

        # Verifica comprimento (com ou sem código do país)
        if len(telefone) == 11:  # Sem código do país
            return telefone[2] == '9'
        elif len(telefone) == 13:  # Com código do país (55)
            return telefone[:2] == '55' and telefone[4] == '9'

        return False

    @staticmethod
    def validar_data(data_str: str, formato: str = "%d/%m/%Y") -> Optional[datetime]:
        """Valida e converte string para data"""
        try:
            return datetime.strptime(data_str, formato)
        except ValueError:
            return None

    @staticmethod
    def validar_horario(horario_str: str) -> Optional[str]:
        """Valida formato de horário HH:MM"""
        pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
        if re.match(pattern, horario_str):
            return horario_str
        return None

    @staticmethod
    def formatar_telefone(telefone: str) -> str:
        """Formata número de telefone para exibição"""
        telefone = re.sub(r'[^0-9]', '', telefone)

        if len(telefone) == 11:
            return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
        elif len(telefone) == 13:
            return f"+{telefone[:2]} ({telefone[2:4]}) {telefone[4:9]}-{telefone[9:]}"

        return telefone

    @staticmethod
    def formatar_cpf(cpf: str) -> str:
        """Formata CPF para exibição"""
        cpf = re.sub(r'[^0-9]', '', cpf)

        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

        return cpf 