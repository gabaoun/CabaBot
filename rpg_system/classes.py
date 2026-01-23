"""
Sistema de Classes RPG

Define as classes base e as quatro classes principais.
Sistema modular para facilitar adicionar novas classes.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from .attributes import Attributes


@dataclass
class Ability:
    """Representa uma habilidade de classe."""
    
    name: str
    description: str
    damage_dice: str = "1d6"  # ex: "2d8", "3d6"
    cost: int = 0  # Pontos de mana/energia
    level_required: int = 1  # Nível mínimo para usar
    cooldown: int = 0  # Rodadas/turnos de espera


class BaseClass(ABC):
    """Classe base para todos os personagens RPG."""
    
    name: str
    description: str
    hit_die: str = "1d8"  # Dados de vida (ex: "1d6", "1d8", "1d10", "1d12")
    
    # Bônus de atributo ao criar (classe específica)
    attribute_bonuses: Dict[str, int] = {}
    
    # Habilidades únicas da classe
    abilities: Dict[str, Ability] = {}
    
    # Proficiências em equipamentos
    proficient_weapons: List[str] = field(default_factory=list)
    proficient_armor: List[str] = field(default_factory=list)
    
    def __init__(self):
        """Inicializa a classe."""
        pass
    
    @abstractmethod
    def get_starting_stats(self) -> Dict[str, int]:
        """Retorna atributos iniciais da classe."""
        pass
    
    @abstractmethod
    def get_abilities(self) -> Dict[str, Ability]:
        """Retorna habilidades da classe."""
        pass
    
    def apply_attribute_bonus(self, attributes: Attributes) -> Attributes:
        """Aplica bônus de atributo específico da classe."""
        for attr_name, bonus in self.attribute_bonuses.items():
            current = getattr(attributes, attr_name)
            setattr(attributes, attr_name, min(current + bonus, Attributes.MAX_VALUE))
        return attributes
    
    def get_proficiency_bonus(self, level: int) -> int:
        """Calcula bônus de proficiência por nível."""
        if level < 5:
            return 2
        elif level < 9:
            return 3
        elif level < 13:
            return 4
        elif level < 17:
            return 5
        else:
            return 6
    
    def get_hit_points_per_level(self, level: int = 1) -> int:
        """Calcula pontos de vida baseado no nível."""
        # Simplificado: 1d8 = 4.5 em média, arredonda para 5
        hit_die_value = int(self.hit_die.split('d')[1])
        hp_per_level = (hit_die_value // 2) + 1
        return hp_per_level


class Warrior(BaseClass):
    """Classe Guerreiro - Alto HP, foco em ataque físico."""
    
    name = "Guerreiro"
    description = "Mestre do combate corpo a corpo com força e resistência"
    hit_die = "1d10"
    attribute_bonuses = {
        "strength": 2,
        "constitution": 1,  # Se implementarmos constituição
    }
    proficient_weapons = ["espada", "machado", "lança", "martelo", "adaga"]
    proficient_armor = ["leve", "pesada", "escudo"]
    
    def get_starting_stats(self) -> Dict[str, int]:
        """Guerreiros começam com força alta."""
        return {
            "strength": 15,
            "dexterity": 10,
            "intelligence": 8,
            "wisdom": 12,
            "charisma": 10,
        }
    
    def get_abilities(self) -> Dict[str, Ability]:
        """Habilidades específicas do Guerreiro."""
        return {
            "ataque_poderoso": Ability(
                name="Ataque Poderoso",
                description="Execute um ataque com força aumentada",
                damage_dice="2d8",
                cost=0,
                level_required=1,
                cooldown=2,
            ),
            "defesa_ferrea": Ability(
                name="Defesa Férrea",
                description="Aumente sua defesa temporariamente",
                cost=0,
                level_required=1,
                cooldown=3,
            ),
            "vendaval_de_acoes": Ability(
                name="Vendaval de Ações",
                description="Ataque múltiplas vezes em um turno",
                damage_dice="3d6",
                cost=5,
                level_required=5,
                cooldown=4,
            ),
        }


class Archer(BaseClass):
    """Classe Arqueiro - Velocidade e precisão, ataque à distância."""
    
    name = "Arqueiro"
    description = "Mestre da destreza com arco e flecha"
    hit_die = "1d8"
    attribute_bonuses = {
        "dexterity": 2,
        "wisdom": 1,
    }
    proficient_weapons = ["arco", "besta", "adaga", "faca"]
    proficient_armor = ["leve", "escudo"]
    
    def get_starting_stats(self) -> Dict[str, int]:
        """Arqueiros começam com destreza alta."""
        return {
            "strength": 10,
            "dexterity": 15,
            "intelligence": 10,
            "wisdom": 13,
            "charisma": 10,
        }
    
    def get_abilities(self) -> Dict[str, Ability]:
        """Habilidades específicas do Arqueiro."""
        return {
            "tiro_preciso": Ability(
                name="Tiro Preciso",
                description="Um tiro com precisão aumentada",
                damage_dice="2d6",
                cost=0,
                level_required=1,
                cooldown=1,
            ),
            "tiro_multiplo": Ability(
                name="Tiro Múltiplo",
                description="Dispare múltiplas flechas",
                damage_dice="3d6",
                cost=3,
                level_required=3,
                cooldown=2,
            ),
            "chuva_de_flechas": Ability(
                name="Chuva de Flechas",
                description="Chuva de flechas em uma área",
                damage_dice="4d6",
                cost=8,
                level_required=7,
                cooldown=4,
            ),
        }


class Mage(BaseClass):
    """Classe Mago - Magia poderosa com baixa resistência física."""
    
    name = "Mago"
    description = "Mestre das artes mágicas e conhecimento arcano"
    hit_die = "1d6"
    attribute_bonuses = {
        "intelligence": 2,
        "wisdom": 1,
    }
    proficient_weapons = ["adaga", "cajado"]
    proficient_armor = ["leve"]
    
    def get_starting_stats(self) -> Dict[str, int]:
        """Magos começam com inteligência alta."""
        return {
            "strength": 8,
            "dexterity": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 10,
        }
    
    def get_abilities(self) -> Dict[str, Ability]:
        """Habilidades específicas do Mago."""
        return {
            "bola_de_fogo": Ability(
                name="Bola de Fogo",
                description="Lança uma bola de fogo explosiva",
                damage_dice="3d8",
                cost=5,
                level_required=1,
                cooldown=2,
            ),
            "raio": Ability(
                name="Raio",
                description="Lança um raio de energia",
                damage_dice="2d8",
                cost=3,
                level_required=1,
                cooldown=1,
            ),
            "escudo_magico": Ability(
                name="Escudo Mágico",
                description="Cria um escudo mágico protetor",
                cost=4,
                level_required=2,
                cooldown=3,
            ),
            "meteoro": Ability(
                name="Meteoro",
                description="Invoca um meteoro destruidor",
                damage_dice="5d10",
                cost=15,
                level_required=9,
                cooldown=5,
            ),
        }


class Druid(BaseClass):
    """Classe Druida - Equilíbrio entre magia natural e combate."""
    
    name = "Druida"
    description = "Mestre da natureza e magia primal"
    hit_die = "1d8"
    attribute_bonuses = {
        "wisdom": 2,
        "intelligence": 1,
    }
    proficient_weapons = ["adaga", "cajado", "arco", "machado"]
    proficient_armor = ["leve", "média"]
    
    def get_starting_stats(self) -> Dict[str, int]:
        """Druidas começam com sabedoria alta."""
        return {
            "strength": 10,
            "dexterity": 11,
            "intelligence": 12,
            "wisdom": 15,
            "charisma": 11,
        }
    
    def get_abilities(self) -> Dict[str, Ability]:
        """Habilidades específicas do Druida."""
        return {
            "garras_da_natureza": Ability(
                name="Garras da Natureza",
                description="Invoca garras naturais para atacar",
                damage_dice="2d6",
                cost=2,
                level_required=1,
                cooldown=1,
            ),
            "cura_natural": Ability(
                name="Cura Natural",
                description="Cura você ou um aliado",
                cost=4,
                level_required=2,
                cooldown=2,
            ),
            "forma_animal": Ability(
                name="Forma Animal",
                description="Transforme-se em um animal",
                cost=6,
                level_required=5,
                cooldown=3,
            ),
            "tempestade_natural": Ability(
                name="Tempestade Natural",
                description="Invoca uma tempestade de elementos",
                damage_dice="4d8",
                cost=12,
                level_required=8,
                cooldown=4,
            ),
        }


# Dicionário com todas as classes disponíveis
AVAILABLE_CLASSES: Dict[str, type[BaseClass]] = {
    "guerreiro": Warrior,
    "arqueiro": Archer,
    "mago": Mage,
    "druida": Druid,
}


def get_class_by_name(class_name: str) -> BaseClass | None:
    """Retorna uma instância da classe por nome."""
    class_lower = class_name.lower()
    if class_lower in AVAILABLE_CLASSES:
        return AVAILABLE_CLASSES[class_lower]()
    return None


def list_available_classes() -> List[str]:
    """Lista todas as classes disponíveis."""
    return list(AVAILABLE_CLASSES.keys())
