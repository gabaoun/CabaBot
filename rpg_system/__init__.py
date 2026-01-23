"""
Sistema RPG para CabaBot - Jogo de RPG de Mesa no Discord

Módulo principal que organiza todo o sistema RPG:
- Atributos e modificadores
- Classes e habilidades
- Inventário e equipamentos
- Perfis de jogador
- Eventos e encontros
- NPCs
"""

from .attributes import Attributes, AttributeModifiers
from .classes import BaseClass, Warrior, Archer, Mage, Druid, AVAILABLE_CLASSES, get_class_by_name, list_available_classes
from .inventory import Item, Equipment, EquipmentSlot, Inventory
from .character import Character, CharacterRepository
from .events import Event, EventRepository, DEFAULT_EVENTS, create_event_repository_with_defaults
from .npcs import NPC, NPCRepository, create_npc_repository_with_defaults

__all__ = [
    "Attributes",
    "AttributeModifiers",
    "BaseClass",
    "Warrior",
    "Archer",
    "Mage",
    "Druid",
    "AVAILABLE_CLASSES",
    "get_class_by_name",
    "list_available_classes",
    "Item",
    "Equipment",
    "EquipmentSlot",
    "Inventory",
    "Character",
    "CharacterRepository",
    "Event",
    "EventRepository",
    "DEFAULT_EVENTS",
    "create_event_repository_with_defaults",
    "NPC",
    "NPCRepository",
    "create_npc_repository_with_defaults",
]
