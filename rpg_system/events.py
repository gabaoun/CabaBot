"""
Sistema de Eventos e Encontros RPG

Define os eventos que podem acontecer no servidor durante o jogo.
Fácil de expandir com novos encontros.
"""

import random
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    """Tipos de eventos no RPG."""
    
    COMBAT = "combate"
    PUZZLE = "enigma"
    ROLEPLAY = "roleplay"
    TREASURE = "tesouro"
    TRAP = "armadilha"
    SOCIAL = "social"
    DUNGEON = "masmorra"
    AMBUSH = "emboscada"


@dataclass
class Event:
    """Representa um evento que pode ocorrer durante o RPG."""
    
    event_id: str
    name: str
    description: str
    event_type: EventType
    difficulty: int  # 1-5, onde 1 é fácil e 5 é muito difícil
    
    # Função callback para processar interações
    on_event_start: Optional[Callable] = None
    on_event_action: Optional[Callable] = None
    on_event_end: Optional[Callable] = None
    
    # Recompensas
    min_exp_reward: int = 100
    max_exp_reward: int = 200
    min_gold_reward: int = 10
    max_gold_reward: int = 50
    
    # Possíveis atributos necessários
    required_checks: Optional[Dict[str, int]] = None  # ex: {"strength": 12, "intelligence": 10}
    
    def __post_init__(self):
        if self.required_checks is None:
            self.required_checks = {}
    
    def get_random_reward(self) -> tuple[int, int]:
        """Retorna (exp, gold) aleatório."""
        exp = random.randint(self.min_exp_reward, self.max_exp_reward)
        gold = random.randint(self.min_gold_reward, self.max_gold_reward)
        return exp, gold


class EventRepository:
    """Gerencia todos os eventos disponíveis."""
    
    def __init__(self):
        self.events: Dict[str, Event] = {}
    
    def register_event(self, event: Event) -> None:
        """Registra um novo evento."""
        self.events[event.event_id] = event
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """Obtém um evento por ID."""
        return self.events.get(event_id)
    
    def get_random_event(self, difficulty: Optional[int] = None) -> Optional[Event]:
        """Obtém um evento aleatório, opcionalmente filtrado por dificuldade."""
        events = list(self.events.values())
        
        if difficulty is not None:
            events = [e for e in events if e.difficulty == difficulty]
        
        if not events:
            return None
        
        return random.choice(events)
    
    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """Obtém todos os eventos de um tipo."""
        return [e for e in self.events.values() if e.event_type == event_type]
    
    def list_all_events(self) -> Dict[str, Event]:
        """Lista todos os eventos registrados."""
        return self.events.copy()


# Eventos pré-definidos - FÁCIL ADICIONAR MAIS!

DEFAULT_EVENTS = [
    Event(
        event_id="goblin_ambush",
        name="Emboscada de Goblins",
        description="Um grupo de goblins primitivos sai da floresta!",
        event_type=EventType.AMBUSH,
        difficulty=1,
        min_exp_reward=50,
        max_exp_reward=100,
        min_gold_reward=5,
        max_gold_reward=20,
        required_checks={"dexterity": 8, "constitution": 8},
    ),
    Event(
        event_id="dragon_encounter",
        name="Encontro com um Dragão",
        description="Um dragão majestoso pousa diante de você...",
        event_type=EventType.COMBAT,
        difficulty=5,
        min_exp_reward=500,
        max_exp_reward=1000,
        min_gold_reward=200,
        max_gold_reward=500,
        required_checks={"strength": 15, "wisdom": 12},
    ),
    Event(
        event_id="ancient_treasure",
        name="Tesouro Antigo",
        description="Você encontra um baú cheio de ouro e jóias!",
        event_type=EventType.TREASURE,
        difficulty=2,
        min_exp_reward=100,
        max_exp_reward=200,
        min_gold_reward=100,
        max_gold_reward=300,
    ),
    Event(
        event_id="sphinx_riddle",
        name="Enigma da Esfinge",
        description="Uma esfinge antiga propõe um enigma desafiador...",
        event_type=EventType.PUZZLE,
        difficulty=3,
        min_exp_reward=150,
        max_exp_reward=250,
        min_gold_reward=30,
        max_gold_reward=80,
        required_checks={"intelligence": 12},
    ),
    Event(
        event_id="cursed_temple",
        name="Templo Amaldiçoado",
        description="Você entra em um templo antigo cheio de armadilhas...",
        event_type=EventType.DUNGEON,
        difficulty=4,
        min_exp_reward=200,
        max_exp_reward=400,
        min_gold_reward=50,
        max_gold_reward=150,
        required_checks={"dexterity": 13, "wisdom": 11, "constitution": 12},
    ),
    Event(
        event_id="bandit_negotiation",
        name="Negociação com Bandidos",
        description="Bandidos bloqueiam o caminho e querem dinheiro...",
        event_type=EventType.SOCIAL,
        difficulty=2,
        min_exp_reward=80,
        max_exp_reward=150,
        min_gold_reward=10,
        max_gold_reward=40,
        required_checks={"charisma": 11},
    ),
    Event(
        event_id="forest_beast",
        name="Besta da Floresta",
        description="Uma criatura selvagem emerge das sombras!",
        event_type=EventType.COMBAT,
        difficulty=3,
        min_exp_reward=150,
        max_exp_reward=300,
        min_gold_reward=30,
        max_gold_reward=100,
        required_checks={"dexterity": 11, "wisdom": 10},
    ),
    Event(
        event_id="magical_artifact",
        name="Artefato Mágico",
        description="Você descobre um artefato mágico perdido...",
        event_type=EventType.TREASURE,
        difficulty=3,
        min_exp_reward=200,
        max_exp_reward=350,
        min_gold_reward=100,
        max_gold_reward=250,
        required_checks={"intelligence": 12},
    ),
    Event(
        event_id="tavern_brawl",
        name="Briga de Taberna",
        description="Uma briga irrompe na taberna local!",
        event_type=EventType.COMBAT,
        difficulty=1,
        min_exp_reward=40,
        max_exp_reward=80,
        min_gold_reward=5,
        max_gold_reward=25,
    ),
    Event(
        event_id="cursed_statue",
        name="Estátua Amaldiçoada",
        description="Uma estátua antiga parece estar viva...",
        event_type=EventType.ROLEPLAY,
        difficulty=2,
        min_exp_reward=100,
        max_exp_reward=180,
        min_gold_reward=20,
        max_gold_reward=60,
        required_checks={"wisdom": 13},
    ),
    Event(
        event_id="hydra_battle",
        name="Batalha com a Hidra",
        description="A lendária Hidra de múltiplas cabeças ataca!",
        event_type=EventType.COMBAT,
        difficulty=5,
        min_exp_reward=400,
        max_exp_reward=800,
        min_gold_reward=150,
        max_gold_reward=400,
        required_checks={"strength": 14, "wisdom": 12, "constitution": 14},
    ),
    Event(
        event_id="lost_city",
        name="Cidade Perdida",
        description="Você descobre os ruins de uma cidade esquecida...",
        event_type=EventType.DUNGEON,
        difficulty=4,
        min_exp_reward=250,
        max_exp_reward=450,
        min_gold_reward=100,
        max_gold_reward=300,
        required_checks={"intelligence": 14, "constitution": 12},
    ),
    Event(
        event_id="dark_alley_ambush",
        name="Emboscada no Beco Escuro",
        description="Ladinos saltam das sombras em um beco estreito!",
        event_type=EventType.AMBUSH,
        difficulty=2,
        min_exp_reward=80,
        max_exp_reward=150,
        min_gold_reward=20,
        max_gold_reward=50,
        required_checks={"dexterity": 12, "constitution": 10},
    ),
    Event(
        event_id="crypt_dungeon",
        name="Cripta Esquecida",
        description="Você explora uma cripta antiga cheia de mortos-vivos...",
        event_type=EventType.DUNGEON,
        difficulty=3,
        min_exp_reward=180,
        max_exp_reward=300,
        min_gold_reward=60,
        max_gold_reward=120,
        required_checks={"strength": 12, "constitution": 12},
    ),
]


def create_event_repository_with_defaults() -> EventRepository:
    """Cria um repositório com todos os eventos padrão."""
    repo = EventRepository()
    for event in DEFAULT_EVENTS:
        repo.register_event(event)
    return repo
