"""
Sistema de Inventário e Equipamentos RPG

Define itens, equipamentos, slots de equipamento e inventário.
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field


class EquipmentSlot(Enum):
    """Slots de equipamento disponíveis."""
    
    MAINHAND = "mão_principal"
    OFFHAND = "mão_secundária"
    ARMOR = "armadura"
    HEAD = "cabeça"
    FEET = "pés"
    ACCESSORIES = "acessório"


@dataclass
class Item:
    """Representa um item genérico no inventário."""
    
    name: str
    description: str
    quantity: int = 1
    value: int = 0  # Preço em moedas
    rarity: str = "comum"  # comum, incomum, raro, muito raro, lendário
    
    def __hash__(self):
        return hash(self.name)


@dataclass
class Equipment(Item):
    """Representa um equipamento que pode ser equipado."""
    
    slot: EquipmentSlot = EquipmentSlot.MAINHAND
    armor_class: int = 0  # Bônus de CA
    damage_bonus: int = 0  # Bônus de dano
    stat_bonuses: Dict[str, int] = field(default_factory=dict)  # ex: {"strength": 1}
    requires_proficiency: bool = False
    
    def __hash__(self):
        return hash((self.name, self.slot.value))


@dataclass
class Inventory:
    """Gerencia o inventário do personagem."""
    
    max_capacity: int = 20
    items: Dict[str, Item] = field(default_factory=dict)
    equipped: Dict[EquipmentSlot, Equipment] = field(default_factory=dict)
    money: int = 0  # Moedas de ouro
    
    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """Adiciona um item ao inventário."""
        if len(self.items) >= self.max_capacity and item.name not in self.items:
            return False
        
        if item.name in self.items:
            self.items[item.name].quantity += quantity
        else:
            item_copy = Item(
                name=item.name,
                description=item.description,
                quantity=quantity,
                value=item.value,
                rarity=item.rarity,
            )
            self.items[item.name] = item_copy
        return True
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """Remove um item do inventário."""
        if item_name not in self.items:
            return False
        
        self.items[item_name].quantity -= quantity
        if self.items[item_name].quantity <= 0:
            del self.items[item_name]
        return True
    
    def get_item(self, item_name: str) -> Optional[Item]:
        """Obtém um item do inventário."""
        return self.items.get(item_name)
    
    def equip_item(self, equipment: Equipment) -> bool:
        """Equipa um item no slot apropriado."""
        # Remove equipamento anterior se existir
        if equipment.slot in self.equipped:
            old_equipment = self.equipped[equipment.slot]
            self.add_item(old_equipment)
        
        self.equipped[equipment.slot] = equipment
        self.remove_item(equipment.name)
        return True
    
    def unequip_item(self, slot: EquipmentSlot) -> bool:
        """Remove equipamento de um slot."""
        if slot not in self.equipped:
            return False
        
        equipment = self.equipped[slot]
        self.add_item(equipment)
        del self.equipped[slot]
        return True
    
    def get_equipped_items(self) -> List[Equipment]:
        """Retorna todos os itens equipados."""
        return list(self.equipped.values())
    
    def get_total_stat_bonuses(self) -> Dict[str, int]:
        """Calcula bônus de atributos de todos os equipamentos."""
        bonuses: Dict[str, int] = {}
        for equipment in self.get_equipped_items():
            for stat, bonus in equipment.stat_bonuses.items():
                bonuses[stat] = bonuses.get(stat, 0) + bonus
        return bonuses
    
    def add_money(self, amount: int) -> None:
        """Adiciona dinheiro ao inventário."""
        self.money = max(0, self.money + amount)
    
    def spend_money(self, amount: int) -> bool:
        """Gasta dinheiro se houver o suficiente."""
        if self.money >= amount:
            self.money -= amount
            return True
        return False
    
    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            "max_capacity": self.max_capacity,
            "items": {
                name: {
                    "name": item.name,
                    "description": item.description,
                    "quantity": item.quantity,
                    "value": item.value,
                    "rarity": item.rarity,
                }
                for name, item in self.items.items()
            },
            "equipped": {
                slot.value: {
                    "name": eq.name,
                    "description": eq.description,
                    "slot": eq.slot.value,
                    "armor_class": eq.armor_class,
                    "damage_bonus": eq.damage_bonus,
                    "stat_bonuses": eq.stat_bonuses,
                    "value": eq.value,
                    "rarity": eq.rarity,
                }
                for slot, eq in self.equipped.items()
            },
            "money": self.money,
        }


# Equipamentos pré-definidos para fácil criação
COMMON_WEAPONS = {
    "adaga": Equipment(
        name="Adaga",
        description="Uma pequena faca afiada",
        slot=EquipmentSlot.MAINHAND,
        damage_bonus=1,
        value=5,
        rarity="comum",
    ),
    "espada": Equipment(
        name="Espada Longa",
        description="Uma espada versátil de aço",
        slot=EquipmentSlot.MAINHAND,
        damage_bonus=2,
        value=20,
        rarity="comum",
    ),
    "arco": Equipment(
        name="Arco Longo",
        description="Um arco de madeira com corda resistente",
        slot=EquipmentSlot.MAINHAND,
        damage_bonus=1,
        value=15,
        rarity="comum",
    ),
    "cajado": Equipment(
        name="Cajado Arcano",
        description="Um cajado usado para canalizar magia",
        slot=EquipmentSlot.MAINHAND,
        damage_bonus=0,
        stat_bonuses={"intelligence": 1},
        value=25,
        rarity="incomum",
    ),
}

COMMON_ARMOR = {
    "armadura_leve": Equipment(
        name="Armadura Leve",
        description="Roupas reforçadas",
        slot=EquipmentSlot.ARMOR,
        armor_class=1,
        value=10,
        rarity="comum",
    ),
    "armadura_media": Equipment(
        name="Armadura Média",
        description="Armadura de couro com perneiras",
        slot=EquipmentSlot.ARMOR,
        armor_class=2,
        value=30,
        rarity="incomum",
    ),
    "armadura_pesada": Equipment(
        name="Armadura Pesada",
        description="Armadura de placas de aço",
        slot=EquipmentSlot.ARMOR,
        armor_class=3,
        value=50,
        rarity="incomum",
    ),
}

COMMON_ACCESSORIES = {
    "anel_resistencia": Equipment(
        name="Anel de Resistência",
        description="Um anel brilhante que aumenta resistência",
        slot=EquipmentSlot.ACCESSORIES,
        armor_class=1,
        stat_bonuses={"constitution": 1},
        value=40,
        rarity="raro",
    ),
    "amuleto_sabedoria": Equipment(
        name="Amuleto de Sabedoria",
        description="Um amuleto que aumenta a sabedoria",
        slot=EquipmentSlot.ACCESSORIES,
        stat_bonuses={"wisdom": 1},
        value=35,
        rarity="raro",
    ),
}
