"""
Sistema de Personagem RPG

Define a classe Character que representa um jogador no RPG
e o repositório para persistência de dados.
"""

from typing import Dict, Optional, Any
import json
from pathlib import Path
from datetime import datetime
from .attributes import Attributes, AttributeModifiers
from .classes import BaseClass, get_class_by_name, AVAILABLE_CLASSES
from .inventory import Inventory, Item, Equipment


class Character:
    """Representa um personagem jogável no RPG."""
    
    def __init__(
        self,
        user_id: int,
        name: str,
        character_class: BaseClass,
        attributes: Optional[Attributes] = None,
        level: int = 1,
    ):
        self.user_id = user_id
        self.name = name
        self.character_class = character_class
        self.attributes = attributes or Attributes.from_dict(
            character_class.get_starting_stats()
        )
        self.character_class.apply_attribute_bonus(self.attributes)
        
        self.level = level
        self.experience = 0
        self.inventory = Inventory()
        
        # Calcula HP
        self.max_hp = self.character_class.get_hit_points_per_level() + \
                      self.attributes.get_modifiers().constitution_mod
        self.current_hp = self.max_hp
        
        # Recurso de classe (mana, energia, etc)
        self.resource_points = 10 + (self.attributes.intelligence * 2)
        self.max_resource_points = self.resource_points
        
        # Timestamps
        self.created_at = datetime.now().isoformat()
        self.last_action = datetime.now().isoformat()
    
    def get_modifiers(self) -> AttributeModifiers:
        """Retorna os modificadores do personagem."""
        return self.attributes.get_modifiers()
    
    def take_damage(self, damage: int) -> bool:
        """Toma dano. Retorna True se ainda está vivo."""
        self.current_hp = max(0, self.current_hp - damage)
        self.last_action = datetime.now().isoformat()
        return self.current_hp > 0
    
    def heal(self, amount: int) -> None:
        """Recupera HP."""
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        self.last_action = datetime.now().isoformat()
    
    def gain_experience(self, amount: int) -> bool:
        """Ganha experiência. Retorna True se subiu de nível."""
        self.experience += amount
        
        # Experiência necessária para subir: 1000 * nível
        exp_to_level = 1000 * self.level
        if self.experience >= exp_to_level:
            return self.level_up()
        return False
    
    def level_up(self) -> bool:
        """Sobe de nível."""
        if self.level >= 20:  # Nível máximo
            return False
        
        self.level += 1
        self.experience = 0
        
        # Aumenta HP
        hp_gain = self.character_class.get_hit_points_per_level()
        self.max_hp += hp_gain
        self.current_hp = self.max_hp
        
        # Aumenta recursos (mana)
        self.max_resource_points += 5
        self.resource_points = self.max_resource_points
        
        return True
    
    def rest(self) -> None:
        """Descansa: recupera HP e recursos."""
        self.current_hp = self.max_hp
        self.resource_points = self.max_resource_points
        self.last_action = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para persistência."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "class": self.character_class.name,
            "attributes": self.attributes.to_dict(),
            "level": self.level,
            "experience": self.experience,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "max_resource_points": self.max_resource_points,
            "resource_points": self.resource_points,
            "inventory": self.inventory.to_dict(),
            "created_at": self.created_at,
            "last_action": self.last_action,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        """Cria um Character a partir de um dicionário."""
        character_class = get_class_by_name(data["class"])
        if not character_class:
            raise ValueError(f"Classe inválida: {data['class']}")
        
        attributes = Attributes.from_dict(data["attributes"])
        
        character = cls(
            user_id=data["user_id"],
            name=data["name"],
            character_class=character_class,
            attributes=attributes,
            level=data.get("level", 1),
        )
        
        character.experience = data.get("experience", 0)
        character.current_hp = data.get("current_hp", character.max_hp)
        character.resource_points = data.get("resource_points", 
                                             character.max_resource_points)
        
        return character
    
    def __repr__(self) -> str:
        return (f"Character(name={self.name}, class={self.character_class.name}, "
                f"level={self.level}, hp={self.current_hp}/{self.max_hp})")


class CharacterRepository:
    """Gerencia persistência de personagens no disco."""
    
    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.characters_file = self.data_path / "characters.json"
    
    def load_character(self, user_id: int) -> Optional[Character]:
        """Carrega um personagem do usuário."""
        characters = self._load_all_characters()
        
        for char_data in characters:
            if char_data["user_id"] == user_id:
                return Character.from_dict(char_data)
        return None
    
    def save_character(self, character: Character) -> None:
        """Salva um personagem."""
        characters = self._load_all_characters()
        
        # Remove personagem antigo se existir
        characters = [c for c in characters if c["user_id"] != character.user_id]
        
        # Adiciona novo
        characters.append(character.to_dict())
        
        self._save_all_characters(characters)
    
    def delete_character(self, user_id: int) -> bool:
        """Deleta um personagem."""
        characters = self._load_all_characters()
        original_len = len(characters)
        characters = [c for c in characters if c["user_id"] != user_id]
        
        if len(characters) < original_len:
            self._save_all_characters(characters)
            return True
        return False
    
    def get_all_characters(self) -> list[Character]:
        """Retorna todos os personagens."""
        characters_data = self._load_all_characters()
        return [Character.from_dict(data) for data in characters_data]
    
    def _load_all_characters(self) -> list[dict]:
        """Carrega todos os dados de personagens do arquivo."""
        if self.characters_file.exists():
            try:
                with open(self.characters_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_all_characters(self, characters: list[dict]) -> None:
        """Salva todos os dados de personagens no arquivo."""
        try:
            with open(self.characters_file, "w", encoding="utf-8") as f:
                json.dump(characters, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Erro ao salvar personagens: {e}")
