"""
Sistema de Atributos RPG

Define os atributos principais (Força, Destreza, Inteligência, Sabedoria, Carisma)
e como eles geram modificadores.
"""

from typing import Dict
from dataclasses import dataclass, field


@dataclass
class Attributes:
    """Representa os 6 atributos principais de um personagem RPG."""
    
    strength: int = 10  # Força - Ataca fisicamente
    dexterity: int = 10  # Destreza - Esquiva e precisão
    constitution: int = 10 # Constituição - HP e resistência física
    intelligence: int = 10  # Inteligência - Magia e conhecimento
    wisdom: int = 10  # Sabedoria - Percepção e resistência mágica
    charisma: int = 10  # Carisma - Persuasão e liderança
    
    MIN_VALUE = 3
    MAX_VALUE = 20
    
    def validate(self) -> bool:
        """Verifica se todos os atributos estão dentro dos limites válidos."""
        for value in [self.strength, self.dexterity, self.constitution, 
                      self.intelligence, self.wisdom, self.charisma]:
            if value < self.MIN_VALUE or value > self.MAX_VALUE:
                return False
        return True
    
    def get_modifiers(self) -> "AttributeModifiers":
        """Calcula os modificadores baseado nos atributos."""
        return AttributeModifiers(
            strength_mod=self._calculate_modifier(self.strength),
            dexterity_mod=self._calculate_modifier(self.dexterity),
            constitution_mod=self._calculate_modifier(self.constitution),
            intelligence_mod=self._calculate_modifier(self.intelligence),
            wisdom_mod=self._calculate_modifier(self.wisdom),
            charisma_mod=self._calculate_modifier(self.charisma),
        )
    
    @staticmethod
    def _calculate_modifier(attribute_value: int) -> int:
        """Calcula o modificador a partir de um valor de atributo (padrão D&D)."""
        return (attribute_value - 10) // 2
    
    def to_dict(self) -> Dict[str, int]:
        """Converte para dicionário."""
        return {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "Attributes":
        """Cria instância a partir de um dicionário."""
        return cls(
            strength=data.get("strength", 10),
            dexterity=data.get("dexterity", 10),
            constitution=data.get("constitution", 10),
            intelligence=data.get("intelligence", 10),
            wisdom=data.get("wisdom", 10),
            charisma=data.get("charisma", 10),
        )
    
    @classmethod
    def default_distribution(cls) -> "Attributes":
        """Distribui 27 pontos (padrão D&D 4d6 drop)."""
        return cls(strength=15, dexterity=14, constitution=13, intelligence=12, 
                   wisdom=10, charisma=8)


@dataclass
class AttributeModifiers:
    """Representam os modificadores derivados dos atributos."""
    
    strength_mod: int = 0
    dexterity_mod: int = 0
    constitution_mod: int = 0
    intelligence_mod: int = 0
    wisdom_mod: int = 0
    charisma_mod: int = 0
    
    def get_attack_bonus(self) -> int:
        """Bônus para ataques físicos (força)."""
        return self.strength_mod
    
    def get_finesse_bonus(self) -> int:
        """Bônus para ataques de destreza (arco, etc)."""
        return self.dexterity_mod
    
    def get_ac_bonus(self) -> int:
        """Bônus para Classe de Armadura."""
        return self.dexterity_mod
    
    def get_hp_bonus(self) -> int:
        """Bônus para Pontos de Vida (Constituição)."""
        return self.constitution_mod

    def get_spell_bonus(self) -> int:
        """Bônus para magias (inteligência)."""
        return self.intelligence_mod
    
    def get_save_bonus(self) -> int:
        """Bônus para resistir a magias (sabedoria)."""
        return self.wisdom_mod
    
    def get_charisma_bonus(self) -> int:
        """Bônus para interações sociais."""
        return self.charisma_mod
    
    def to_dict(self) -> Dict[str, int]:
        """Converte para dicionário."""
        return {
            "strength_mod": self.strength_mod,
            "dexterity_mod": self.dexterity_mod,
            "constitution_mod": self.constitution_mod,
            "intelligence_mod": self.intelligence_mod,
            "wisdom_mod": self.wisdom_mod,
            "charisma_mod": self.charisma_mod,
        }
