# Sistema RPG Discord - Quick Start Guide

## 🎮 O que é?

Um sistema completo de RPG de Mesa integrado ao seu bot Discord! Seus amigos podem:
- Criar personagens com classes únicas
- Alocar pontos em atributos (Força, Destreza, Inteligência, Sabedoria, Carisma)
- Participar de eventos e encontros aleatórios
- Lutar contra NPCs e ganhar ouro/XP
- Ganhar equipamentos e subir de nível

## ⚡ Início Rápido

### 1. Criar um personagem

```
/rpg criar nome:"Seu Nome" classe:"Guerreiro"
```

Classes disponíveis:
- **Guerreiro** - Alto HP, forte em combate físico
- **Arqueiro** - Rápido, preciso com arco
- **Mago** - Magia poderosa, frágil
- **Druida** - Equilíbrio entre magia e combate

### 2. Alocar atributos

```
/rpg atributos forca:15 destreza:14 inteligencia:12 sabedoria:13 carisma:11
```

Cada atributo pode ter 3-20 pontos.

### 3. Disparar um evento

```
/evento aleatorio
```

Todos os participantes do servidor podem clicar em "Participar" para tentar interagir com o evento baseado em seus atributos!

### 4. Encontrar um NPC

```
/evento encontro
```

Escolha entre:
- **Atacar** - Combate direto
- **Conversar** - Teste de Carisma
- **Fugir** - Teste de Destreza

## 📊 Atributos e Modificadores

```
Modificador = (Valor do Atributo - 10) / 2
```

| Atributo | Uso |
|----------|-----|
| Força | Dano físico, arrombar coisas |
| Destreza | Esquiva, precisão, arco |
| Inteligência | Magia, conhecimento |
| Sabedoria | Percepção, resistência mágica |
| Carisma | Persuasão, negociação |

## 🛠️ Personalizando

### Adicionar Nova Classe

Edite `rpg_system/classes.py` e crie:

```python
class SuaClasse(BaseClass):
    name = "Sua Classe"
    description = "Descrição"
    hit_die = "1d10"
    
    def get_starting_stats(self):
        return {
            "strength": 15,
            "dexterity": 10,
            "intelligence": 10,
            "wisdom": 11,
            "charisma": 12,
        }
    
    def get_abilities(self):
        return {
            "habilidade_1": Ability(
                name="Habilidade 1",
                description="Descrição",
                damage_dice="2d8",
                cost=3,
                level_required=1,
                cooldown=2,
            ),
        }
```

Depois adicione em `AVAILABLE_CLASSES`:

```python
AVAILABLE_CLASSES = {
    "guerreiro": Warrior,
    "sua_classe": SuaClasse,  # Adicione aqui
}
```

### Adicionar Novo Evento

Edite `rpg_system/events.py` e adicione em `DEFAULT_EVENTS`:

```python
Event(
    event_id="seu_evento",
    name="Nome do Evento",
    description="O que acontece",
    event_type=EventType.COMBAT,
    difficulty=2,  # 1-5
    min_exp_reward=100,
    max_exp_reward=200,
    min_gold_reward=20,
    max_gold_reward=60,
    required_checks={"strength": 12},
),
```

### Adicionar Novo NPC

Edite `rpg_system/npcs.py` em `create_default_npcs()`:

```python
npc = NPC(
    npc_id="seu_npc",
    name="Nome do NPC",
    title="Inimigo",
    description="Descrição",
    level=2,
    max_hp=20,
    current_hp=20,
)
npc.inventory.add_money(50)
npc.inventory.add_item(Item(
    name="Espada",
    description="Uma espada",
    value=50,
    rarity="incomum"
))
npcs.append(npc)
```

## 📁 Estrutura de Arquivos

```
CabaBot/
├── rpg_system/              # Sistema RPG principal
│   ├── __init__.py
│   ├── attributes.py        # Atributos e modificadores
│   ├── classes.py           # Classes de personagem
│   ├── character.py         # Perfil do personagem
│   ├── inventory.py         # Inventário e equipamentos
│   ├── events.py            # Eventos do jogo
│   └── npcs.py              # NPCs
├── rpg_commands.py          # Comandos básicos do RPG
├── rpg_events_commands.py   # Comandos de eventos
├── RPG_DOCUMENTATION.md     # Documentação completa
├── rpg_data/                # Dados dos personagens (criado automaticamente)
│   └── characters.json
└── CabaBot.py              # Bot principal (integrado)
```

## 🎲 Exemplos de Uso

### Criar um Guerreiro

```
/rpg criar nome:"Conan" classe:"Guerreiro"
/rpg atributos forca:18 destreza:12 inteligencia:8 sabedoria:11 carisma:10
```

### Iniciar um Evento de Combate

```
/evento aleatorio
```

Todos participam automaticamente!

### Encontrar um Inimigo

```
/evento encontro
```

Botões aparecem para você interagir!

### Ver seu Status

```
/rpg perfil
```

Mostra todos seus atributos, HP, Mana e itens!

## 💡 Dicas

1. **Teste de Atributos:** Cada evento requer diferentes atributos
2. **Modificadores:** Um modificador +2 é bem significativo!
3. **Nível:** Ganhe XP em eventos para subir de nível
4. **Equipamentos:** NPCs derrotados deixam loot!
5. **Descansar:** Use `/rpg descansar` para recuperar HP/Mana

## 🔄 Sistema de Progressão

- **Nível 1:** 0 XP
- **Nível 2:** 1000 XP
- **Nível 3:** 2000 XP
- Máximo: Nível 20

Cada nível você ganha +5 HP!

## 🚀 Próximas Ideias

- [ ] Sistema de loja
- [ ] Quests persistentes
- [ ] Clãs/Guildas
- [ ] Leaderboard
- [ ] Crafting de itens
- [ ] Dungeons
- [ ] PvP com árbitro

---

**Precisando de ajuda?** Verifique [RPG_DOCUMENTATION.md](RPG_DOCUMENTATION.md) para mais detalhes!

Divirta-se! 🎲✨
