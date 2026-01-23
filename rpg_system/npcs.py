"""
Sistema de NPCs RPG

Define NPCs (Non-Player Characters) que podem aparecer aleatoriamente
no servidor com equipamentos e dinheiro.
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from .attributes import Attributes
from .classes import BaseClass, get_class_by_name, list_available_classes
from .inventory import Inventory, Equipment, Item, EquipmentSlot


@dataclass
class NPC:
    """Representa um NPC no jogo."""
    
    npc_id: str
    name: str
    title: str  # ex: "Bardo", "Mercador", "Inimigo"
    description: str
    
    npc_class: Optional[BaseClass] = None
    attributes: Optional[Attributes] = None
    level: int = 1
    
    max_hp: int = 20
    current_hp: int = 20
    
    inventory: Optional[Inventory] = None
    
    def __post_init__(self):
        if self.npc_class is None:
            # Escolhe uma classe aleatória se não especificada
            available = list_available_classes()
            self.npc_class = get_class_by_name(random.choice(available))
        
        if self.attributes is None:
            self.attributes = Attributes.from_dict(
                self.npc_class.get_starting_stats()  # type: ignore
            )
        
        if self.inventory is None:
            self.inventory = Inventory()
    
    def take_damage(self, damage: int) -> bool:
        """Toma dano. Retorna True se ainda está vivo."""
        self.current_hp = max(0, self.current_hp - damage)
        return self.current_hp > 0
    
    def get_loot(self) -> tuple[int, list[Item]]:
        """Retorna (dinheiro, itens) quando derrotado."""
        gold = random.randint(5, 50) * self.level
        items = list(self.inventory.items.values())  # type: ignore
        return gold, items
    
    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            "npc_id": self.npc_id,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "class": self.npc_class.name if self.npc_class else None,
            "attributes": self.attributes.to_dict() if self.attributes else {},
            "level": self.level,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
        }


class NPCRepository:
    """Gerencia todos os NPCs disponíveis."""
    
    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
    
    def register_npc(self, npc: NPC) -> None:
        """Registra um novo NPC."""
        self.npcs[npc.npc_id] = npc
    
    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Obtém um NPC por ID."""
        return self.npcs.get(npc_id)
    
    def get_random_npc(self) -> Optional[NPC]:
        """Obtém um NPC aleatório."""
        if not self.npcs:
            return None
        return random.choice(list(self.npcs.values()))
    
    def list_all_npcs(self) -> Dict[str, NPC]:
        """Lista todos os NPCs registrados."""
        return self.npcs.copy()


# NPCs pré-definidos

def create_default_npcs() -> List[NPC]:
    """Cria NPCs padrão para o jogo."""
    npcs = []
    
    # Goblim básico
    npc = NPC(
        npc_id="goblin_1",
        name="Goblin Primitivo",
        title="Inimigo",
        description="Um pequeno goblin com olhos malignos",
        level=1,
        max_hp=8,
        current_hp=8,
    )
    npc.inventory.add_money(5)  # type: ignore
    npc.inventory.add_item(Item(  # type: ignore
        name="Adaga Enferrujada",
        description="Uma velha adaga de um goblin",
        value=3,
        rarity="comum"
    ))
    npcs.append(npc)
    
    # Orc guerreiro
    npc = NPC(
        npc_id="orc_warrior",
        name="Orc Guerreiro",
        title="Inimigo",
        description="Um orc musculoso com muita cicatriz",
        level=3,
        max_hp=30,
        current_hp=30,
    )
    npc.inventory.add_money(25)  # type: ignore
    npc.inventory.add_item(Item(  # type: ignore
        name="Machado de Orc",
        description="Um machado pesado feito por orcs",
        value=15,
        rarity="incomum"
    ))
    npcs.append(npc)
    
    # Troll
    npc = NPC(
        npc_id="troll",
        name="Troll Antigo",
        title="Inimigo",
        description="Um troll regenerador de aparência assustadora",
        level=4,
        max_hp=50,
        current_hp=50,
    )
    npc.inventory.add_money(50)  # type: ignore
    npc.inventory.add_item(Item(  # type: ignore
        name="Cristal do Troll",
        description="Um cristal brilhante contendo poder arcano",
        value=40,
        rarity="raro"
    ))
    npcs.append(npc)
    
    # Mercador
    npc = NPC(
        npc_id="merchant",
        name="Mercador Errante",
        title="PNJ",
        description="Um mercador que vende equipamentos raros",
        level=2,
        max_hp=15,
        current_hp=15,
    )
    npc.inventory.add_money(200)  # type: ignore
    npc.inventory.add_item(Equipment(  # type: ignore
        name="Espada Afiada",
        description="Uma espada recém-afiada",
        slot=EquipmentSlot.MAINHAND,
        damage_bonus=2,
        value=50,
        rarity="incomum"
    ))
    npcs.append(npc)
    
    # Mago
    npc = NPC(
        npc_id="mage_enemy",
        name="Mago Esquecido",
        title="Inimigo",
        description="Um mago que vaga pela floresta",
        level=3,
        max_hp=15,
        current_hp=15,
    )
    npc.inventory.add_money(30)  # type: ignore
    npc.inventory.add_item(Item(  # type: ignore
        name="Pergaminho de Magia",
        description="Um pergaminho com um feitiço valioso",
        value=25,
        rarity="raro"
    ))
    npcs.append(npc)
    
    # Aventureiro
    npc = NPC(
        npc_id="adventurer",
        name="Aventureiro Mítico",
        title="Inimigo",
        description="Um lendário aventureiro que protege suas terras",
        level=5,
        max_hp=60,
        current_hp=60,
    )
    npc.inventory.add_money(100)  # type: ignore
    npc.inventory.add_item(Item(  # type: ignore
        name="Arma Lendária",
        description="Uma arma que passou por muitas batalhas",
        value=100,
        rarity="muito_raro"
    ))
    npcs.append(npc)
    
    # Bandido
    npc = NPC(
        npc_id="bandit",
        name="Bandido da Estrada",
        title="Inimigo",
        description="Um ladrão que assalta viajantes",
        level=2,
        max_hp=18,
        current_hp=18,
    )
    npc.inventory.add_money(40)  # type: ignore
    npc.inventory.add_item(Item(  # type: ignore
        name="Bolsa de Ouro",
        description="Moedas roubadas de viajantes",
        value=30,
        rarity="comum"
    ))
    npcs.append(npc)
    
    return npcs


def create_npc_repository_with_defaults() -> NPCRepository:
    """Cria um repositório com todos os NPCs padrão."""
    repo = NPCRepository()
    for npc in create_default_npcs():
        repo.register_npc(npc)
    return repo
