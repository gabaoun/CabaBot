# 👨‍💻 Guia de Desenvolvimento

## Estrutura de Classes

### `DiceRoller`

**Responsabilidade:** Parsing e rolagem de dados

**Métodos principais:**
- `__init__(dado_str)` - Inicializa com formato tipo "3d6"
- `_parse_dado()` - Extrai quantidade e lados
- `rolar()` - Executa a rolagem e armazena resultados
- `format_resultado()` - Formata para exibição

**Exemplo de extensão:**
```python
class DiceRollerComVantagem(DiceRoller):
    """Rola com vantagem (rola 2x, pega o maior)"""
    
    def rolar_com_vantagem(self):
        self.rolar()
        primeiro = self.total
        self.rolar()
        segundo = self.total
        self.total = max(primeiro, segundo)
        self.resultados = [primeiro, segundo, self.total]
```

---

### `TestConfig`

**Responsabilidade:** Armazenar e gerenciar estado do teste

**Atributos:**
- `tipo` - Nome do atributo (ex: "Destreza")
- `cd` - Classe de Dificuldade
- `dado` - Instância de DiceRoller
- `participantes` - Dict com resultados

**Métodos principais:**
- `adicionar_resultado(user_id, nome, resultado)`
- `get_ranking()` - Retorna string formatada do ranking

**Exemplo de extensão:**
```python
class TestConfigComBotoes(TestConfig):
    """Teste que permite repetir rolagem com botão adicional"""
    
    def permitir_rerolagem(self, user_id):
        if user_id in self.participantes:
            # Remove resultado anterior
            del self.participantes[user_id]
```

---

### `RollButton`

**Responsabilidade:** Lógica de interação do botão

**O que faz:**
1. Verifica se usuário já participou
2. Rola os dados
3. Armazena resultado
4. Envia resposta privada
5. Atualiza mensagem pública

**Exemplo de extensão:**
```python
class RollButtonComConseguimento(RollButton):
    """Botão que oferece reroll se falhar"""
    
    async def callback(self, interaction: discord.Interaction):
        # Chama método pai
        await super().callback(interaction)
        
        # Se falhou, oferece reroll
        if resultado < self.test_config.cd:
            # Cria novo botão de reroll
            # ...
```

---

### `RollView`

**Responsabilidade:** Container dos componentes UI

**O que faz:**
- Cria a view com buttons
- Configura timeout
- Gerencia ciclo de vida

**Exemplo de extensão:**
```python
class RollViewComMenuSeleção(RollView):
    """View com menu para escolher tipo de teste"""
    
    def __init__(self, test_config, test_message_id):
        super().__init__(test_config, test_message_id)
        
        # Adiciona select menu
        select = discord.ui.Select(
            placeholder="Escolha seu tipo de teste..."
        )
        self.add_item(select)
```

---

## Como Adicionar Novos Tipos de Testes

### Passo 1: Estenda TestConfig

```python
class TesteDePericia(TestConfig):
    """Teste que permite adicionar bônus de perícia"""
    
    def __init__(self, tipo, cd, pericia_bonus=0):
        super().__init__(
            tipo=tipo,
            cd=cd,
            dado_str="d20"
        )
        self.pericia_bonus = pericia_bonus
    
    def calcular_resultado_final(self, roll):
        return roll + self.pericia_bonus
```

### Passo 2: Estenda RollButton (se necessário)

```python
class RollButtonComPericia(RollButton):
    
    async def callback(self, interaction: discord.Interaction):
        # ... código do pai ...
        
        # Adiciona lógica customizada
        if isinstance(self.test_config, TesteDePericia):
            resultado_final = self.test_config.calcular_resultado_final(resultado)
            # ... atualiza com novo resultado ...
```

### Passo 3: Adicione comando slash

```python
@bot.tree.command(name="teste_pericia", description="Teste com perícia")
@app_commands.describe(
    tipo="Tipo de perícia",
    cd="Classe de dificuldade",
    bonus="Bônus de perícia"
)
async def teste_pericia(interaction, tipo: str, cd: int, bonus: int = 0):
    test = TesteDePericia(tipo, cd, bonus)
    view = RollView(test, 0)
    # ... resto do código ...
```

---

## Padrão de Resposta do Teste

Todos os testes devem seguir este padrão de resposta privada:

```
[Emoji] **[Tipo de Teste]** ([Dado usado])
Seu resultado: **[Número]** [✅ SUCESSO / ❌ FALHA]
CD necessária: **[CD]**
```

Exemplo:
```
🎲 **Destreza** (d20)
Seu resultado: **14** ✅ SUCESSO
CD necessária: **12**
```

---

## Mensagem de Teste Pública

Formato padrão para embeds públicos:

```
🎭 Teste de [Tipo]
[Descrição opcional]

Dado: **[Formato]**
Classe de Dificuldade: **CD [Número]**

📊 Ranking
[Lista de participantes com resultados]
```

---

## Validações Obrigatórias

Sempre valide:

1. **Quantidade de dados**
   ```python
   if quantidade < 1 or quantidade > 100:
       raise ValueError("Máximo 100 dados")
   ```

2. **Lados do dado**
   ```python
   if lados < 2 or lados > 1000:
       raise ValueError("Mínimo 2, máximo 1000 lados")
   ```

3. **Classe de Dificuldade**
   ```python
   if cd < 1:
       raise ValueError("CD deve ser maior que 0")
   ```

4. **Participação única**
   ```python
   if user_id in test.participantes:
       # Erro: já participou
   ```

---

## Testes Unitários Recomendados

```python
# test_dice_roller.py
def test_parse_dado_valido():
    roller = DiceRoller("3d6")
    assert roller.quantidade == 3
    assert roller.lados == 6

def test_rolar_dentro_limites():
    roller = DiceRoller("2d20")
    roller.rolar()
    assert all(1 <= r <= 20 for r in roller.resultados)
    assert 2 <= roller.total <= 40

def test_formato_invalido():
    with pytest.raises(ValueError):
        DiceRoller("xyz")
```

---

## Performance e Escalabilidade

### Otimizações Atuais
- `active_tests` dict evita queries de banco
- Testes expiram após 1 hora (timeout automático)
- Sem persistência - dados limpos na reinicialização

### Para Escalar em Produção
1. Adicione persistência em banco de dados
2. Implemente garbage collection para testes antigos
3. Cache de resultados frequentes
4. Rate limiting por usuário

---

## Debugging

### Verificar estado de um teste

```python
# No arquivo CabaBot.py, adicione um comando debug:
@bot.tree.command(name="debug_teste")
async def debug_teste(interaction: discord.Interaction, message_id: int):
    if message_id in active_tests:
        test = active_tests[message_id]
        await interaction.response.send_message(
            f"**Tipo:** {test.tipo}\n"
            f"**CD:** {test.cd}\n"
            f"**Participantes:** {len(test.participantes)}\n"
            f"**Resultado:** {test.get_ranking()}",
            ephemeral=True
        )
```

### Logs Recomendados

```python
print(f"✅ Teste de {test_config.tipo} iniciado")
print(f"👤 Usuário {user_id} ({nome}) rolou {resultado}")
print(f"🎉 Teste finalizado com {len(test_config.participantes)} participantes")
```

---

## Commits Recomendados

```
feat: adicionar classe DiceRoller modular
refactor: extrair lógica de dados em classe dedicada
feat: adicionar sistema de testes com buttons
test: adicionar testes para DiceRoller
docs: adicionar guia de desenvolvimento
```

---

**Boa sorte desenvolvendo! 🚀**
