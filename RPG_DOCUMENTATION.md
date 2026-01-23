"""
DOCUMENTAÇÃO DO SISTEMA RPG DO CABABOT
======================================

Um sistema completo de RPG de Mesa integrado ao Discord!

## COMO USAR

### 1. CRIAR UM PERSONAGEM
Use o comando `/rpg criar` para começar:
- **Nome:** Nome do seu personagem
- **Classe:** Escolha entre Guerreiro, Arqueiro, Mago ou Druida

Exemplo:
```
/rpg criar nome:"Aragorn" classe:"Guerreiro"
```

### 2. ATRIBUIR PONTOS DE ATRIBUTO
Use `/rpg atributos` para alocar seus pontos nos 5 atributos:
- **Força (STR):** Dano físico, arrombar coisas
- **Destreza (DEX):** Esquiva, precisão, movimento
- **Inteligência (INT):** Magia, conhecimento
- **Sabedoria (WIS):** Percepção, resistência mágica
- **Carisma (CHA):** Persuasão, liderança

Valores devem estar entre 3 e 20.

### 3. VER SEU PERFIL
Use `/rpg perfil` para ver seus atributos, HP, mana e inventário.

### 4. DESCANSANDO
Use `/rpg descansar` para recuperar todo HP e Mana.

### 5. COMEÇAR EVENTOS
Um mestre (com cargo definido) ou o próprio sistema pode disparar eventos:
- `/evento aleatorio` - Dispara um evento aleatório
- `/evento encontro` - Encontra um NPC aleatório
- `/evento listar` - Lista todos os eventos disponíveis

### 6. INTERAGINDO COM EVENTOS
Quando um evento acontece, você pode:
- **Participar:** Clique em "Participar" e realize testes de atributo
- **Encontro com NPC:** Escolha entre Atacar, Conversar ou Fugir

## SISTEMA DE CLASSES

### GUERREIRO
- **HP:** Muito alto (d10)
- **Força:** +2 (bônus inicial)
- **Armas:** Espadas, machados, lanças, escudos
- **Habilidades:**
  - Ataque Poderoso (2d8 dano)
  - Defesa Férrea (reduz dano)
  - Vendaval de Ações (3d6 dano múltiplo)

### ARQUEIRO
- **HP:** Alto (d8)
- **Destreza:** +2 (bônus inicial)
- **Armas:** Arcos, bestas, adagas
- **Habilidades:**
  - Tiro Preciso (2d6 dano)
  - Tiro Múltiplo (3d6 dano)
  - Chuva de Flechas (4d6 área)

### MAGO
- **HP:** Baixo (d6)
- **Inteligência:** +2 (bônus inicial)
- **Armas:** Adagas, cajados
- **Habilidades:**
  - Bola de Fogo (3d8 dano)
  - Raio (2d8 dano rápido)
  - Escudo Mágico (proteção)
  - Meteoro (5d10 dano massivo)

### DRUIDA
- **HP:** Alto (d8)
- **Sabedoria:** +2 (bônus inicial)
- **Armas:** Adagas, cajados, arcos, machados
- **Habilidades:**
  - Garras da Natureza (2d6 dano)
  - Cura Natural (recupera HP)
  - Forma Animal (transformação)
  - Tempestade Natural (4d8 dano)

## SISTEMA DE MODIFICADORES

Os modificadores são calculados automaticamente a partir dos atributos:

```
Modificador = (Atributo - 10) / 2 (arredonda para baixo)
```

Exemplos:
- Atributo 20 → Modificador +5
- Atributo 15 → Modificador +2
- Atributo 10 → Modificador +0
- Atributo 8 → Modificador -1

Os modificadores afetam:
- **Força:** Bônus de ataque físico
- **Destreza:** Bônus de esquiva e arco
- **Inteligência:** Bônus de magia
- **Sabedoria:** Resistência a magia
- **Carisma:** Negociações e sociais

## COMO ADICIONAR NOVAS CLASSES

1. Abra o arquivo `rpg_system/classes.py`
2. Crie uma nova classe herdando de `BaseClass`:

```python
class Paladino(BaseClass):
    name = "Paladino"
    description = "Um guerreiro devotado"
    hit_die = "1d10"
    attribute_bonuses = {"strength": 1, "wisdom": 1}
    proficient_weapons = ["espada", "escudo"]
    proficient_armor = ["leve", "pesada"]
    
    def get_starting_stats(self):
        return {
            "strength": 15,
            "dexterity": 10,
            "intelligence": 9,
            "wisdom": 14,
            "charisma": 13,
        }
    
    def get_abilities(self):
        return {
            "golpe_sagrado": Ability(
                name="Golpe Sagrado",
                description="Um golpe abençoado",
                damage_dice="2d8",
                cost=3,
                level_required=1,
                cooldown=2,
            ),
            # Mais habilidades...
        }
```

3. Registre a classe no dicionário `AVAILABLE_CLASSES` em `classes.py`:

```python
AVAILABLE_CLASSES: Dict[str, type[BaseClass]] = {
    "guerreiro": Warrior,
    "arqueiro": Archer,
    "mago": Mage,
    "druida": Druid,
    "paladino": Paladino,  # Adicionar aqui!
}
```

## COMO ADICIONAR NOVOS EVENTOS

1. Abra o arquivo `rpg_system/events.py`
2. Crie um novo Event e adicione à lista `DEFAULT_EVENTS`:

```python
Event(
    event_id="seu_evento_unico",
    name="Nome do Evento",
    description="Descrição do que acontece",
    event_type=EventType.COMBAT,  # Tipo: COMBAT, PUZZLE, ROLEPLAY, TREASURE, TRAP, SOCIAL
    difficulty=3,  # 1-5
    min_exp_reward=100,
    max_exp_reward=200,
    min_gold_reward=20,
    max_gold_reward=60,
    required_checks={"strength": 12, "wisdom": 10},  # Testes opcionais
),
```

Os tipos de evento disponíveis:
- **COMBAT:** Combate direto
- **PUZZLE:** Enigma ou desafio mental
- **ROLEPLAY:** Interação social
- **TREASURE:** Tesouro a encontrar
- **TRAP:** Armadilha a evitar
- **SOCIAL:** Negociação ou persuasão

## COMO ADICIONAR NOVOS NPCs

1. Abra o arquivo `rpg_system/npcs.py`
2. Use a função `create_default_npcs()` para adicionar novos NPCs:

```python
npc = NPC(
    npc_id="seu_npc_id",
    name="Nome do NPC",
    title="Inimigo/PNJ",  # Tipo de NPC
    description="Descrição visual",
    level=2,
    max_hp=25,
    current_hp=25,
)
npc.inventory.add_money(50)
npc.inventory.add_item(Item(
    name="Espada Mágica",
    description="Uma espada brilhante",
    value=100,
    rarity="raro"
))
npcs.append(npc)
```

Raridades: comum, incomum, raro, muito_raro, lendário

## SISTEMA DE EQUIPAMENTOS

Equipamentos podem ser:
- Armas (dano_bonus)
- Armaduras (armor_class)
- Acessórios (bônus de atributos)

Para criar equipamento:

```python
from rpg_system.inventory import Equipment, EquipmentSlot

sword = Equipment(
    name="Espada Lendária",
    description="Uma espada de lendas",
    slot=EquipmentSlot.MAINHAND,
    damage_bonus=3,
    stat_bonuses={"strength": 1},
    value=200,
    rarity="lendário",
)
```

Slots disponíveis:
- MAINHAND (mão principal)
- OFFHAND (mão secundária)
- ARMOR (armadura)
- HEAD (cabeça)
- FEET (pés)
- ACCESSORIES (acessório)

## ARQUIVO DE DADOS

Todos os dados dos personagens são salvos em:
```
CabaBot/rpg_data/characters.json
```

Formato JSON para fácil consulta e edição manual se necessário.

## COMANDOS DISPONÍVEIS

### RPG Básico
- `/rpg criar` - Criar novo personagem
- `/rpg perfil` - Ver seu perfil
- `/rpg atributos` - Alocar pontos em atributos
- `/rpg descansar` - Recuperar HP e Mana
- `/rpg classes` - Listar classes disponíveis
- `/rpg deletar` - Deletar seu personagem

### Eventos
- `/evento aleatorio` - Dispara evento aleatório
- `/evento encontro` - Encontra um NPC
- `/evento listar` - Lista eventos

## SISTEMAS FUTUROS POSSÍVEIS

- [ ] Sistema de loja para comprar equipamentos
- [ ] Quests persistentes e campanhas
- [ ] Sistema de clãs/guildas
- [ ] Leaderboard de XP e nível
- [ ] Sistema de crafting
- [ ] Dungeons instanciados
- [ ] PvP com árbitro
- [ ] NPCs com diálogos complexos
- [ ] Sistema de skills/perícias
- [ ] Magia customizável

## SUPORTE

Para dúvidas ou sugestões sobre o sistema RPG:
1. Confira a documentação dos módulos
2. Verifique os arquivos de exemplo
3. Leia os docstrings das funções

Happy roleplaying! 🎲
