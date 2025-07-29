import pytest
from datetime import datetime
from app.utils.formatters import FormatterUtils

class TestFormatterUtils:
    
    def test_formatar_data_brasil(self):
        """Testa formatação de data para padrão brasileiro"""
        data = datetime(2024, 1, 15)
        formatado = FormatterUtils.formatar_data_brasil(data)
        assert formatado == "15/01/2024"
    
    def test_formatar_hora_brasil(self):
        """Testa formatação de hora para padrão brasileiro"""
        data = datetime(2024, 1, 15, 14, 30)
        formatado = FormatterUtils.formatar_hora_brasil(data)
        assert formatado == "14:30"
    
    def test_formatar_data_hora_brasil(self):
        """Testa formatação de data e hora para padrão brasileiro"""
        data = datetime(2024, 1, 15, 14, 30)
        formatado = FormatterUtils.formatar_data_hora_brasil(data)
        assert formatado == "15/01/2024 às 14:30"
    
    def test_get_dia_semana(self):
        """Testa obtenção do dia da semana em português"""
        # Segunda-feira
        data = datetime(2024, 1, 15)  # Segunda-feira
        dia = FormatterUtils.get_dia_semana(data)
        assert dia == "Segunda-feira"
        
        # Terça-feira
        data = datetime(2024, 1, 16)  # Terça-feira
        dia = FormatterUtils.get_dia_semana(data)
        assert dia == "Terça-feira"
    
    def test_formatar_saudacao_manha(self):
        """Testa saudação pela manhã"""
        # Mock para simular manhã
        import time
        original_hour = datetime.now().hour
        
        # Simular manhã (antes do meio-dia)
        with pytest.MonkeyPatch().context() as m:
            m.setattr(datetime, 'now', lambda: datetime(2024, 1, 15, 9, 0))
            saudacao = FormatterUtils.formatar_saudacao()
            assert "Bom dia" in saudacao
    
    def test_formatar_menu_principal(self):
        """Testa formatação do menu principal"""
        menu = FormatterUtils.formatar_menu_principal()
        assert "Clínica Gabriela Nassif" in menu
        assert "1️⃣" in menu
        assert "2️⃣" in menu
        assert "3️⃣" in menu
        assert "4️⃣" in menu
        assert "5️⃣" in menu 