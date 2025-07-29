import pytest
from app.utils.validators import ValidatorUtils

class TestValidatorUtils:
    
    def test_validar_cpf_valido(self):
        """Testa validação de CPF válido"""
        cpf_valido = "12345678909"
        assert ValidatorUtils.validar_cpf(cpf_valido) == True
    
    def test_validar_cpf_invalido(self):
        """Testa validação de CPF inválido"""
        cpf_invalido = "12345678901"
        assert ValidatorUtils.validar_cpf(cpf_invalido) == False
    
    def test_validar_cpf_com_pontos(self):
        """Testa validação de CPF com formatação"""
        cpf_formatado = "123.456.789-09"
        assert ValidatorUtils.validar_cpf(cpf_formatado) == True
    
    def test_validar_telefone_valido(self):
        """Testa validação de telefone válido"""
        telefone_valido = "31999999999"
        assert ValidatorUtils.validar_telefone(telefone_valido) == True
    
    def test_validar_telefone_invalido(self):
        """Testa validação de telefone inválido"""
        telefone_invalido = "3199999999"
        assert ValidatorUtils.validar_telefone(telefone_invalido) == False
    
    def test_formatar_telefone(self):
        """Testa formatação de telefone"""
        telefone = "31999999999"
        formatado = ValidatorUtils.formatar_telefone(telefone)
        assert formatado == "(31) 99999-9999"
    
    def test_formatar_cpf(self):
        """Testa formatação de CPF"""
        cpf = "12345678909"
        formatado = ValidatorUtils.formatar_cpf(cpf)
        assert formatado == "123.456.789-09" 