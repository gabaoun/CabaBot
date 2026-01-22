# 🎲 Guia Completo de Uso - Sistema de Testes e Dados

## 1️⃣ Rolador de Dados Padrão `/d`

Perfeito para quando você quer escolher de uma lista pré-definida.

### Exemplos

```
/d lados:20
→ Rola 1d20 (resultado único)

/d lados:6 quantidade:3
→ Rola 3d6 (3 dados de 6 lados)

/d lados:100
→ Rola 1d100 (percentual)
```

### Dados Disponíveis
- d2, d4, d6, d8, d10, d12, d20, d100

### O que você vê
```
🎲 Rolagem de 3d6
Dados Individuais: `4, 5, 6`
Total: **15**
```

---

## 2️⃣ Rolador de Dados Customizado `/dado_custom`

Para quando você quer qualquer número de lados ou adicionar modificadores.

### Exemplos

```
/dado_custom dado:d20
→ Rola 1d20

/dado_custom dado:3d6 modificador:2
→ Rola 3d6 + 2 (muito útil para bônus!)

/dado_custom dado:2d10 modificador:-1
→ Rola 2d10 - 1 (útil para penalidades)
```

### Formatos Válidos
- `d20` → 1d20
- `3d6` → 3d6
- `2d10` → 2d10
- `4d4` → 4d4
- Qualquer número entre 1-100 dados e 2-1000 lados

### O que você vê
```
🎲 Rolagem de 3d6
Dados Individuais: `3, 4, 5`
Subtotal: **12**

Modificador: +2
Total com Modificador: **14**
```

---

## 3️⃣ Testes de Atributo `/teste_atributo` ⭐ NOVO

### Para uma pessoa (você testa)

```
/teste_atributo tipo:Destreza cd:12 dado:d20
```

Você recebe um resultado privado:
```
🎲 **Destreza** (d20)
Seu resultado: **16** ✅ SUCESSO
CD necessária: **12**
```

### Para múltiplas pessoas (tipo um RPG)

**Você cria o teste:**
```
/teste_atributo tipo:Força cd:15 dado:d20
```

**Mensagem aparece no chat:**
```
🎭 Teste de Força
Dado: **d20**
Classe de Dificuldade: **CD 15**

📊 Ranking
Nenhum participante ainda.
```
[🎲 Rolar] ← Todos clicam nesse botão!

**Cada pessoa clica no botão:**
- Pedro clica → recebe "Seu resultado: **18** ✅ SUCESSO"
- Maria clica → recebe "Seu resultado: **10** ❌ FALHA"
- João clica → recebe "Seu resultado: **17** ✅ SUCESSO"

**O ranking atualiza automaticamente:**
```
📊 Ranking
🥇 **João**: 17 ✅ SUCESSO
🥈 **Pedro**: 18 ✅ SUCESSO
🥉 **Maria**: 10 ❌ FALHA
```

---

## 🎯 Caso de Uso: RPG com Amigos

### Cenário: Teste de Furtividade

```
Mestre: /teste_atributo tipo:Furtividade cd:14 dado:d20
```

Todos os jogadores (ladrões) clicam em 🎲 Rolar para ver quem consegue passar despercebido.

---

### Cenário: Teste de Resistência a Magia

```
Mestre: /teste_atributo tipo:Resistência cd:16 dado:d20 modificador:2
```

Note: Na versão atual, o modificador é adicionado individualmente se você quiser usar `/dado_custom`, ou você pode instruir todos a adicionar mentalmente o modificador.

---

## 🔧 Parâmetros Detalhados

### `/d`
| Parâmetro | Tipo | Obrigatório? | Limites | Padrão |
|---|---|---|---|---|
| `lados` | Choice (2,4,6,8,10,12,20,100) | ✅ Sim | Fixo | - |
| `quantidade` | Número | ❌ Não | 1-100 | 1 |

### `/dado_custom`
| Parâmetro | Tipo | Obrigatório? | Limites | Padrão |
|---|---|---|---|---|
| `dado` | Texto | ✅ Sim | d2-d1000 | - |
| `modificador` | Número | ❌ Não | -1000 a +1000 | 0 |

**Exemplos válidos de `dado`:** d20, 3d6, 2d10, 10d4

### `/teste_atributo`
| Parâmetro | Tipo | Obrigatório? | Limites | Padrão |
|---|---|---|---|---|
| `tipo` | Texto | ✅ Sim | Qualquer nome | - |
| `cd` | Número | ✅ Sim | 1+ | - |
| `dado` | Texto | ❌ Não | d2-d1000 | d20 |

**Exemplos:**
- `/teste_atributo tipo:Constituição cd:10` → Usa d20 por padrão
- `/teste_atributo tipo:Vontade cd:8 dado:d12` → Usa d12 customizado

---

## 📊 Entendendo os Resultados

### Sucesso vs Falha

```
Seu resultado: **16** ✅ SUCESSO
CD necessária: **12**
```
✅ Se resultado ≥ CD → SUCESSO  
❌ Se resultado < CD → FALHA

### Exemplo
- CD é 12
- Você rola 16 → 16 ≥ 12 → ✅ SUCESSO
- Você rola 10 → 10 < 12 → ❌ FALHA

---

## 🎮 Dicas de Jogo

### Como Mestre (D&D, Pathfinder, etc)

1. **Defina a CD apropriada**
   - Fácil: 8-10
   - Moderado: 12-14
   - Difícil: 15-17
   - Muito Difícil: 18-20

2. **Escolha o dado certo**
   - d20 é padrão (mais incerteza)
   - d12 é um pouco mais fácil
   - d10 é mais fácil ainda

3. **Crie nome descritivo para o teste**
   - ✅ `/teste_atributo tipo:Derrotar a câmera cd:15 dado:d20`
   - ❌ `/teste_atributo tipo:X cd:15 dado:d20`

### Como Jogador

1. **Clique no botão assim que aparecer**
2. **Veja seu resultado em mensagem privada**
3. **Acompanhe o ranking que atualiza em tempo real**
4. **Vibre com os sucessos e falhas dos companheiros!** 🎉

---

## ❓ Perguntas Frequentes

### P: Posso participar do teste mais de uma vez?
**R:** Não! Você só pode rolar uma vez por teste. O bot previne cliques duplicados.

### P: Quanto tempo o teste fica ativo?
**R:** 1 hora (3600 segundos). Após isso, o botão expira.

### P: Posso ver meu resultado e o dos outros?
**R:** Seu resultado é privado (só você vê). O ranking de todos é público.

### P: Como adiciono bônus ao meu resultado?
**R:** Use `/dado_custom dado:d20 modificador:+2` para rolar individual, ou o mestre pode somar mentalmente.

### P: Posso criar um teste com vários dados (ex: 3d6)?
**R:** Sim! `/teste_atributo tipo:MeuTeste cd:10 dado:3d6`

---

## 🔮 Próximas Funcionalidades (Planejadas)

- Vantagem/Desvantagem (rolar 2d20, pegar maior/menor)
- Críticos automáticos (20 = sucesso automático com bônus)
- Testes combinados (múltiplos atributos em sequência)
- Histórico de testes completados
- Sistema de XP/pontos

---

**Divirta-se rolando dados!** 🎲✨
