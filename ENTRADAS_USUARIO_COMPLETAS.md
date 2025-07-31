# 📱 **TODAS AS ENTRADAS POSSÍVEIS DO USUÁRIO**

## 📋 **TABELA COMPLETA DE ENTRADAS POR ESTADO**

---

### 🔵 **ESTADO: `inicio`**
| Entrada do Usuário | Resposta do Sistema | Próximo Estado |
|-------------------|-------------------|----------------|
| Qualquer texto | Menu principal com opções 1-5, 0 | `menu_principal` |

---

### 🔵 **ESTADO: `menu_principal`**
| Entrada do Usuário | Resposta do Sistema | Próximo Estado |
|-------------------|-------------------|----------------|
| `"1"` | "Vamos agendar sua consulta! Digite seu CPF:" | `aguardando_cpf` (ação: agendar) |
| `"2"` | "Para ver agendamentos, digite seu CPF:" | `aguardando_cpf` (ação: visualizar) |
| `"3"` | "Para cancelar consulta, digite seu CPF:" | `aguardando_cpf` (ação: cancelar) |
| `"4"` | "Lista de espera! Digite seu CPF:" | `aguardando_cpf` (ação: lista_espera) |
| `"5"` | Informações de contato do atendente | `menu_principal` |
| `"0"` | Mensagem de despedida | `finalizada` |
| Qualquer outra | "❌ Opção inválida! Digite 1-5" | `menu_principal` |

---

### 🔵 **ESTADO: `aguardando_cpf`**
| Entrada do Usuário | Condição | Resposta do Sistema | Próximo Estado |
|-------------------|----------|-------------------|----------------|
| CPF 11 dígitos | ✅ Válido + Encontrado | "✅ Paciente encontrado! Confirma?" | `confirmando_paciente` |
| CPF 11 dígitos | ✅ Válido + ❌ Não encontrado | "❌ CPF não encontrado. Opções 1-3" | `paciente_nao_encontrado` |
| CPF inválido | ❌ < ou > 11 dígitos | "❌ CPF inválido! Digite 11 dígitos" | `aguardando_cpf` |
| Texto qualquer | ❌ Não numérico | "❌ CPF inválido! Digite 11 dígitos" | `aguardando_cpf` |

---

### 🔵 **ESTADO: `paciente_nao_encontrado`**
| Entrada do Usuário | Resposta do Sistema | Próximo Estado |
|-------------------|-------------------|----------------|
| `"1"` | "Digite o CPF correto:" | `aguardando_cpf` |
| `"2"` | "📋 Para cadastro, entre em contato..." | `menu_principal` |
| `"3"` | "👨‍⚕️ Informações de atendimento humano" | `menu_principal` |
| `"0"` | Menu principal | `menu_principal` |
| Qualquer outra | "❌ Digite: 1-Tentar CPF, 2-Cadastro, 3-Atendente, 0-Menu" | `paciente_nao_encontrado` |

---

### 🔵 **ESTADO: `confirmando_paciente`**
| Entrada do Usuário | Ação no Contexto | Resposta do Sistema | Próximo Estado |
|-------------------|------------------|-------------------|----------------|
| `"1"` | `agendar` | "📅 Vamos agendar! Datas disponíveis:" | `escolhendo_data` |
| `"1"` | `visualizar` | "📅 Seus agendamentos: [lista]" | `visualizando_agendamentos` |
| `"1"` | `cancelar` | "📞 Para cancelar, entre em contato..." | `menu_principal` |
| `"1"` | `lista_espera` | "✅ Adicionado à lista de espera!" | `menu_principal` |
| `"2"` | Qualquer | "Digite o CPF correto:" | `aguardando_cpf` |
| `"0"` | Qualquer | Menu principal | `menu_principal` |
| Qualquer outra | Qualquer | "❌ Digite: 1-Sim, 2-Não, 0-Menu" | `confirmando_paciente` |

---

### 🔵 **ESTADO: `escolhendo_data`**
| Entrada do Usuário | Condição | Resposta do Sistema | Próximo Estado |
|-------------------|----------|-------------------|----------------|
| `"1"` a `"7"` | ✅ Data válida disponível | "⏰ Horários disponíveis para [data]:" | `escolhendo_horario` |
| `"8"` ou maior | ❌ Número fora do range | "❌ Opção inválida! Escolha 1-7" | `escolhendo_data` |
| Texto não numérico | ❌ Não é número | "❌ Digite apenas o número da opção" | `escolhendo_data` |
| Número negativo | ❌ Inválido | "❌ Opção inválida! Escolha 1-7" | `escolhendo_data` |

---

### 🔵 **ESTADO: `escolhendo_horario`**
| Entrada do Usuário | Condição | Resposta do Sistema | Próximo Estado |
|-------------------|----------|-------------------|----------------|
| `"1"` a `"8"` | ✅ Horário válido disponível | "✅ Confirmar agendamento: [resumo]" | `confirmando_agendamento` |
| `"9"` ou maior | ❌ Número fora do range | "❌ Opção inválida! Escolha 1-8" | `escolhendo_horario` |
| Texto não numérico | ❌ Não é número | "❌ Digite apenas o número da opção" | `escolhendo_horario` |
| Número negativo | ❌ Inválido | "❌ Opção inválida! Escolha 1-8" | `escolhendo_horario` |

---

### 🔵 **ESTADO: `confirmando_agendamento`**
| Entrada do Usuário | Resposta do Sistema | Próximo Estado |
|-------------------|-------------------|----------------|
| `"1"` | "✅ Agendamento confirmado! [detalhes completos]" | `menu_principal` |
| `"2"` | "❌ Agendamento cancelado. Digite 1 para menu" | `menu_principal` |
| Qualquer outra | "Digite: 1-Confirmar, 2-Cancelar" | `confirmando_agendamento` |

---

### 🔵 **ESTADO: `visualizando_agendamentos`**
| Entrada do Usuário | Resposta do Sistema | Próximo Estado |
|-------------------|-------------------|----------------|
| `"0"` | Menu principal | `menu_principal` |
| `"1"` | "Vamos agendar! Digite seu CPF:" | `aguardando_cpf` (ação: agendar) |
| `"3"` | "📞 Para cancelar, entre em contato..." | `menu_principal` |
| Qualquer outra | "❌ Digite: 0-Menu, 1-Agendar, 3-Cancelar" | `visualizando_agendamentos` |

---

### 🔵 **ESTADO: `lista_espera`**
| Entrada do Usuário | Resposta do Sistema | Próximo Estado |
|-------------------|-------------------|----------------|
| `"1"` | Menu principal | `menu_principal` |
| Qualquer outra | "Digite 1 para voltar ao menu" | `lista_espera` |

---

## 🌐 **COMANDOS GLOBAIS (Funcionam em QUALQUER estado)**

| Entrada do Usuário | Resposta do Sistema | Próximo Estado |
|-------------------|-------------------|----------------|
| `"0"` ou `"sair"` | "👋 Obrigado! Para nova conversa, digite oi" | `finalizada` |
| `"menu"` ou `"ajuda"` | Menu principal completo | `menu_principal` |
| `"cancelar"` | "❌ Operação cancelada. Voltando ao menu..." | `menu_principal` |

---

## 🔤 **TIPOS DE ENTRADA RECONHECIDOS**

### **1. 📞 CPF (Estado: `aguardando_cpf`)**
- ✅ **Válidos:** `"12345678901"`, `"123.456.789-01"`, `"123 456 789 01"`
- ❌ **Inválidos:** `"123456789"`, `"abc123"`, `"11111111111"`, `""`

### **2. 🔢 Números de Menu**
- ✅ **Válidos:** `"1"`, `"2"`, `"3"`, `"4"`, `"5"`, `"0"`
- ❌ **Inválidos:** `"6"`, `"10"`, `"a"`, `"1a"`, `" 1 "`

### **3. 📅 Seleção de Data**
- ✅ **Válidos:** `"1"` a `"7"` (dependendo das datas disponíveis)
- ❌ **Inválidos:** `"0"`, `"8"`, `"segunda"`, `"amanhã"`

### **4. ⏰ Seleção de Horário**
- ✅ **Válidos:** `"1"` a `"8"` (dependendo dos horários disponíveis)
- ❌ **Inválidos:** `"0"`, `"9"`, `"8:00"`, `"manhã"`

### **5. ✅❌ Confirmações**
- ✅ **Válidos:** `"1"` (Sim), `"2"` (Não), `"0"` (Menu)
- ❌ **Inválidos:** `"sim"`, `"não"`, `"ok"`, `"s"`, `"n"`

---

## 🎯 **RESUMO ESTATÍSTICO**

### **📊 Total de Entradas Possíveis: 80+**

| Categoria | Quantidade |
|-----------|------------|
| **Comandos de Menu** | 6 opções (0-5) |
| **CPFs Válidos** | ∞ (infinitos CPFs válidos) |
| **CPFs Inválidos** | ∞ (infinitas possibilidades) |
| **Seleções de Data** | 7 opções (1-7) |
| **Seleções de Horário** | 8 opções (1-8) |
| **Confirmações** | 3 opções (0-2) |
| **Comandos Globais** | 6 comandos |
| **Textos Inválidos** | ∞ (infinitas possibilidades) |

### **🔄 Estados que Aceitam Mais Entradas:**
1. **`aguardando_cpf`** - Aceita qualquer texto (valida CPF)
2. **`menu_principal`** - 7 opções diferentes
3. **`escolhendo_data`** - 8+ opções (7 válidas + inválidas)
4. **`confirmando_paciente`** - 4 opções (0,1,2 + inválidas)

### **🎯 Estados Mais Restritivos:**
1. **`lista_espera`** - Apenas "1" é útil
2. **`confirmando_agendamento`** - Apenas "1" ou "2"
3. **`finalizada`** - Não aceita entradas (conversa encerrada)

---

## 🧠 **SISTEMA DE PROCESSAMENTO NLU**

### **🔍 Análise Automática de Intenção:**
O sistema analisa automaticamente:
- **Saudações:** "oi", "olá", "bom dia", etc.
- **Números:** Identifica automaticamente se é opção de menu
- **CPF:** Detecta padrões de 11 dígitos
- **Comandos:** "menu", "ajuda", "sair", etc.
- **Confirmações:** "sim", "não", "ok" → Convertidos para números

### **📝 Exemplos de Conversão Automática:**
- `"oi"` → Mostra menu principal
- `"sim"` → Convertido para `"1"` (quando apropriado)
- `"não"` → Convertido para `"2"` (quando apropriado)
- `"123.456.789-01"` → Convertido para `"12345678901"`
- `"menu principal"` → Comando global "menu"

---

## 🚀 **SISTEMA ROBUSTO DE VALIDAÇÃO**

### **✅ Validações Automáticas:**
1. **Sanitização:** Remove caracteres especiais perigosos
2. **Limite de tamanho:** Máximo 1000 caracteres por mensagem
3. **Formato:** Valida formatos esperados (CPF, números, etc.)
4. **Estado:** Verifica se entrada é válida para o estado atual
5. **Contexto:** Valida se há contexto necessário
6. **API:** Verifica disponibilidade antes de enviar

### **🛡️ Recuperação de Erros:**
- **Input inválido:** Orienta o usuário sobre formato correto
- **Estado inconsistente:** Volta ao menu principal
- **Erro de API:** Usa dados mock ou escalona para humano
- **Timeout:** Recovery automático com retry
- **Spam:** Rate limiting e bloqueio temporário

---

## 📱 **CONCLUSÃO**

**O chatbot aceita TODAS as possibilidades de entrada do usuário:**

✅ **Entradas válidas:** Processadas corretamente
✅ **Entradas inválidas:** Orientação para correção  
✅ **Comandos globais:** Funcionam em qualquer momento
✅ **Estados inconsistentes:** Recovery automático
✅ **Erros de sistema:** Fallback gracioso
✅ **Auditoria completa:** Log de todas as interações

**Resultado:** Sistema robusto que nunca "quebra" e sempre orienta o usuário! 🎉