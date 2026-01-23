# Exemplos de Extensão do Sistema RPG

Este arquivo contém exemplos prontos para copiar e colar para expandir o sistema RPG!

## ✨ Novas Classes

### Exemplo 1: Paladino

Copie para `rpg_system/classes.py`:

```python
class Paladin(BaseClass):
    """Guerreiro sagrado que combina força e magia de cura."""
    
    name = "Paladino"
    description = "Guerreiro devotado com poder sagrado"
    hit_die = "1d10"
    attribute_bonuses = {
        "strength": 1,
        "wisdom": 1,
    }
    proficient_weapons = ["espada", "machado", "escudo"]
    proficient_armor = ["leve", "pesada"]
    
    def get_starting_stats(self) -> Dict[str, int]:
        return {
            "strength": 15,
            "dexterity": 10,
            "intelligence": 9,
            "wisdom": 14,
            "charisma": 13,
        }
    
    def get_abilities(self) -> Dict[str, Ability]:
        return {
            "golpe_sagrado": Ability(
                name="Golpe Sagrado",
                description="Golpe abençoado que causa dano extra",
                damage_dice="2d8",
                cost=2,
                level_required=1,
                cooldown=2,
            ),
            "cura_sagrada": Ability(
                name="Cura Sagrada",
                description="Cura você ou um aliado",
                cost=3,
                level_required=1,
                cooldown=2,
            ),
            "aura_protetora": Ability(
                name="Aura Protetora",
                description="Aumenta defesa de todos próximos",
                cost=5,
                level_required=3,
                cooldown=4,
            ),
            "juizo_divino": Ability(
                name="Juízo Divino",
                description="Invoca ira divina sobre inimigos",
                damage_dice="3d10",
                cost=8,
                level_required=6,
                cooldown=5,
            ),
        }
```

Depois adicione em `AVAILABLE_CLASSES`:

```python
AVAILABLE_CLASSES: Dict[str, type[BaseClass]] = {
    "guerreiro": Warrior,
    "arqueiro": Archer,
    "mago": Mage,
    "druida": Druid,
    "paladino": Paladin,  # Adicione aqui
}
```

### Exemplo 2: Bardo

```python
class Bard(BaseClass):
    """Mestre das artes que combina magia, charme e combate versátil."""
    
    name = "Bardo"
    description = "Artista e mágico que inspira aliados"
    hit_die = "1d8"
    attribute_bonuses = {
        "charisma": 2,
        "dexterity": 1,
    }
    proficient_weapons = ["espada", "arco", "adaga"]
    proficient_armor = ["leve"]
    
    def get_starting_stats(self) -> Dict[str, int]:
        return {
            "strength": 10,
            "dexterity": 13,
            "intelligence": 12,
            "wisdom": 11,
            "charisma": 16,
        }
    
    def get_abilities(self) -> Dict[str, Ability]:
        return {
            "canto_inspirador": Ability(
                name="Canto Inspirador",
                description="Aumenta dano dos aliados",
                cost=2,
                level_required=1,
                cooldown=2,
            ),
            "toque_magico": Ability(
                name="Toque Mágico",
                description="Golpe com magia sonora",
                damage_dice="2d6",
                cost=2,
                level_required=1,
                cooldown=1,
            ),
            "cura_por_musica": Ability(
                name="Cura por Música",
                description="Cura através de melodias sagradas",
                cost=3,
                level_required=2,
                cooldown=2,
            ),
            "orquestration_magica": Ability(
                name="Orquestração Mágica",
                description="Cria explosão sônica devastadora",
                damage_dice="4d6",
                cost=10,
                level_required=7,
                cooldown=5,
            ),
        }
```

## 🎪 Novos Eventos

### Exemplo 1: Festival do Vilarejo

Adicione em `rpg_system/events.py` na lista `DEFAULT_EVENTS`:

```python
Event(
    event_id="village_festival",
    name="Festival do Vilarejo",
    description="O vilarejo está em festa! Você precisa participar dos desafios!",
    event_type=EventType.SOCIAL,
    difficulty=1,
    min_exp_reward=75,
    max_exp_reward=125,
    min_gold_reward=15,
    max_gold_reward=35,
    required_checks={"charisma": 9},
),
```

### Exemplo 2: Masmorra Antiga

```python
Event(
    event_id="ancient_dungeon",
    name="Masmorra Antiga",
    description="Uma masmorra escura e perigosa cheia de armadilhas e inimigos!",
    event_type=EventType.TRAP,
    difficulty=4,
    min_exp_reward=300,
    max_exp_reward=500,
    min_gold_reward=100,
    max_gold_reward=250,
    required_checks={"dexterity": 14, "intelligence": 11},
),
```

### Exemplo 3: Negociação com Troll

```python
Event(
    event_id="troll_negotiation",
    name="Negociação com Troll",
    description="Um troll antigo bloqueia a ponte. Você precisa negociar ou lutar!",
    event_type=EventType.SOCIAL,
    difficulty=3,
    min_exp_reward=150,
    max_exp_reward=250,
    min_gold_reward=50,
    max_gold_reward=120,
    required_checks={"charisma": 12, "wisdom": 10},
),
```

### Exemplo 4: Tesouro do Capitão

```python
Event(
    event_id="pirate_treasure",
    name="Tesouro do Capitão Pirata",
    description="Você encontra um mapa de tesouro! Seguindo-o descobre riquezas!",
    event_type=EventType.TREASURE,
    difficulty=2,
    min_exp_reward=120,
    max_exp_reward=220,
    min_gold_reward=200,
    max_gold_reward=500,
),
```

## 👹 Novos NPCs

Adicione em `rpg_system/npcs.py` na função `create_default_npcs()`:

### Exemplo 1: Dragão Vermelho

```python
npc = NPC(
    npc_id="dragon_red",
    name="Dragão Vermelho",
    title="Inimigo",
    description="Um dragão gigantesco com escamas vermelhas como fogo",
    level=8,
    max_hp=100,
    current_hp=100,
)
npc.inventory.add_money(500)
npc.inventory.add_item(Item(
    name="Chama Dracônica",
    description="Uma joia que contém a essência do dragão",
    value=250,
    rarity="lendário"
))
npc.inventory.add_item(Item(
    name="Ouro do Tesouro",
    description="Moedas antigas de um imperio perdido",
    value=200,
    rarity="raro"
))
npcs.append(npc)
```

### Exemplo 2: Vendedor Ambulante

```python
npc = NPC(
    npc_id="wandering_merchant",
    name="Vendedor Ambulante",
    title="PNJ",
    description="Um mercador misterioso que vende itens raros",
    level=1,
    max_hp=10,
    current_hp=10,
)
npc.inventory.add_money(500)
npc.inventory.add_item(Equipment(
    name="Espada de Aço Perfeito",
    description="Uma espada magistralmente forjada",
    slot=EquipmentSlot.MAINHAND,
    damage_bonus=3,
    stat_bonuses={"strength": 1},
    value=150,
    rarity="raro"
))
npc.inventory.add_item(Equipment(
    name="Anel de Inteligência",
    description="Aumenta o poder mágico",
    slot=EquipmentSlot.ACCESSORIES,
    stat_bonuses={"intelligence": 2},
    value=100,
    rarity="raro"
))
npcs.append(npc)
```

### Exemplo 3: Líder de Bandidos

```python
npc = NPC(
    npc_id="bandit_leader",
    name="Capitão de Bandidos",
    title="Inimigo",
    description="Um líder de bandidos brutalmente experiente",
    level=5,
    max_hp=60,
    current_hp=60,
)
npc.inventory.add_money(200)
npc.inventory.add_item(Item(
    name="Sabre Ensanguentado",
    description="Tinta de sangue está nele",
    value=80,
    rarity="raro"
))
npc.inventory.add_item(Item(
    name="Mapa do Tesouro",
    description="Mostra a localização de uma fortuna escondida",
    value=150,
    rarity="muito_raro"
))
npcs.append(npc)
```

## 🏪 Novos Equipamentos

Adicione em `rpg_system/inventory.py`:

```python
# Novas armas poderosas
LEGENDARY_WEAPONS = {
    "excalibur": Equipment(
        name="Excalibur",
        description="A lendária espada dos reis",
        slot=EquipmentSlot.MAINHAND,
        damage_bonus=5,
        stat_bonuses={"strength": 2, "charisma": 1},
        value=500,
        rarity="lendário",
    ),
    "arco_celestial": Equipment(
        name="Arco Celestial",
        description="Um arco feito da luz das estrelas",
        slot=EquipmentSlot.MAINHAND,
        damage_bonus=4,
        stat_bonuses={"dexterity": 2, "wisdom": 1},
        value=400,
        rarity="muito_raro",
    ),
    "cajado_infinito": Equipment(
        name="Cajado do Infinito",
        description="Um cajado que canaliza mana infinita",
        slot=EquipmentSlot.MAINHAND,
        damage_bonus=1,
        stat_bonuses={"intelligence": 3},
        value=450,
        rarity="lendário",
    ),
}

# Novas armaduras
LEGENDARY_ARMOR = {
    "armadura_dragao": Equipment(
        name="Armadura de Escamas de Dragão",
        description="Feita das escamas de um dragão antigo",
        slot=EquipmentSlot.ARMOR,
        armor_class=4,
        stat_bonuses={"strength": 1, "constitution": 2},
        value=300,
        rarity="muito_raro",
    ),
    "veste_maga": Equipment(
        name="Veste da Maga Ancestral",
        description="Roupas que amplificam magia",
        slot=EquipmentSlot.ARMOR,
        armor_class=1,
        stat_bonuses={"intelligence": 2, "wisdom": 1},
        value=250,
        rarity="raro",
    ),
}
```

## 🎯 Dicas de Implementação

1. **Sempre adicione variedade:** Eventos e NPCs com dificuldades diferentes
2. **Balance:** Recompensas devem ser proporcionais à dificuldade
3. **Modificadores:** Lembre que modificadores vão de -5 a +5 geralmente
4. **Cooldown:** Habilidades fortes devem ter cooldown maior
5. **Raridade:** Use raridade para indicar valor (comum < incomum < raro < muito_raro < lendário)

## 🚀 Próximas Expansões Sugeridas

- [ ] Sistema de Quest (missões específicas)
- [ ] Loja de itens (comprar/vender)
- [ ] Sistema de Clãs (guildas/equipes)
- [ ] PvP com árbitro
- [ ] Leaderboard mensal
- [ ] Sistema de Skill/Perícia
- [ ] Magia customizável
- [ ] Crafting e alquimia

---

Divirta-se expandindo o sistema! 🎲✨
