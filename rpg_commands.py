"""
Comandos Discord para o Sistema RPG

Define todos os slash commands para interagir com o RPG.
"""

import discord
from discord.ext import commands
from discord import app_commands
import random
from typing import Optional
from pathlib import Path

from rpg_system import (
    Character, CharacterRepository, 
    get_class_by_name, list_available_classes,  # noqa: F401
    EventRepository, create_event_repository_with_defaults,  # noqa: F401
    NPCRepository, create_npc_repository_with_defaults,  # noqa: F401
    Attributes
)


class RPGCog(commands.Cog):
    """Cog para todos os comandos do RPG."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        # Inicializa repositórios
        self.data_path = Path(__file__).parent / "rpg_data"
        self.character_repo = CharacterRepository(self.data_path)
        self.event_repo = create_event_repository_with_defaults()
        self.npc_repo = create_npc_repository_with_defaults()
        
        # Controle de eventos em andamento
        self.active_events: dict = {}
    
    rpg_group = app_commands.Group(name="rpg", description="Comandos do RPG de Mesa")
    
    # ==================== CRIAÇÃO DE PERSONAGEM ====================
    
    @rpg_group.command(name="criar", description="Cria um novo personagem RPG")
    async def create_character(
        self,
        interaction: discord.Interaction,
        nome: str,
        classe: str
    ):
        """Cria um novo personagem para o usuário."""
        
        # Verifica se já tem personagem
        existing = self.character_repo.load_character(interaction.user.id)
        if existing:
            await interaction.response.send_message(
                f"❌ Você já tem um personagem: **{existing.name}**\n"
                f"Use `/rpg deletar` para criar um novo.",
                ephemeral=True
            )
            return
        
        # Obtém a classe
        character_class = get_class_by_name(classe)
        if not character_class:
            await interaction.response.send_message(
                "❌ Classe inválida!",
                ephemeral=True
            )
            return
        
        # Cria o personagem
        character = Character(
            user_id=interaction.user.id,
            name=nome,
            character_class=character_class
        )
        
        # Salva no repositório
        self.character_repo.save_character(character)
        
        # Cria embed de confirmação
        embed = discord.Embed(
            title=f"✅ Personagem Criado!",
            description=f"Bem-vindo, {nome}!",
            color=discord.Color.green()
        )
        embed.add_field(name="Classe", value=character_class.name, inline=False)
        embed.add_field(name="Descrição", value=character_class.description, inline=False)
        embed.add_field(name="HP", value=f"{character.current_hp}/{character.max_hp}")
        embed.add_field(name="Nível", value=str(character.level))
        embed.add_field(name="Experiência", value=f"{character.experience} XP")
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== VISUALIZAR PERSONAGEM ====================
    
    @rpg_group.command(name="perfil", description="Visualiza seu perfil RPG")
    async def view_profile(self, interaction: discord.Interaction):
        """Mostra o perfil completo do personagem."""
        
        character = self.character_repo.load_character(interaction.user.id)
        if not character:
            await interaction.response.send_message(
                "❌ Você não tem um personagem! Use `/rpg criar` para criar um.",
                ephemeral=True
            )
            return
        
        mods = character.get_modifiers()
        
        embed = discord.Embed(
            title=f"📋 {character.name}",
            color=discord.Color.blue()
        )
        
        # Info básica
        embed.add_field(name="Classe", value=character.character_class.name, inline=True)
        embed.add_field(name="Nível", value=str(character.level), inline=True)
        embed.add_field(name="EXP", value=f"{character.experience} / {1000 * character.level}", inline=True)
        
        # Atributos
        attrs = character.attributes
        embed.add_field(
            name="📊 Atributos",
            value=(
                f"**Força:** {attrs.strength} ({mods.strength_mod:+d})\n"
                f"**Destreza:** {attrs.dexterity} ({mods.dexterity_mod:+d})\n"
                f"**Inteligência:** {attrs.intelligence} ({mods.intelligence_mod:+d})\n"
                f"**Sabedoria:** {attrs.wisdom} ({mods.wisdom_mod:+d})\n"
                f"**Carisma:** {attrs.charisma} ({mods.charisma_mod:+d})"
            ),
            inline=False
        )
        
        # Saúde e Recursos
        hp_percent = int((character.current_hp / character.max_hp) * 100)
        hp_bar = "🟩" * (hp_percent // 20) + "⬜" * (5 - (hp_percent // 20))
        
        resource_percent = int((character.resource_points / character.max_resource_points) * 100)
        resource_bar = "🟦" * (resource_percent // 20) + "⬜" * (5 - (resource_percent // 20))
        
        embed.add_field(
            name="❤️ Saúde",
            value=f"{hp_bar} {character.current_hp}/{character.max_hp}",
            inline=False
        )
        embed.add_field(
            name="✨ Mana/Energia",
            value=f"{resource_bar} {character.resource_points}/{character.max_resource_points}",
            inline=False
        )
        
        embed.add_field(
            name="💰 Ouro",
            value=str(character.inventory.money),
            inline=True
        )
        embed.add_field(
            name="🎒 Itens",
            value=str(len(character.inventory.items)),
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== ATRIBUTOS ====================
    
    @rpg_group.command(name="atributos", description="Aloca pontos em atributos")
    @app_commands.describe(
        forca="Força (1-20)",
        destreza="Destreza (1-20)",
        inteligencia="Inteligência (1-20)",
        sabedoria="Sabedoria (1-20)",
        carisma="Carisma (1-20)"
    )
    async def allocate_attributes(
        self,
        interaction: discord.Interaction,
        forca: int,
        destreza: int,
        inteligencia: int,
        sabedoria: int,
        carisma: int
    ):
        """Aloca pontos em atributos (máx 20 por atributo)."""
        
        character = self.character_repo.load_character(interaction.user.id)
        if not character:
            await interaction.response.send_message(
                "❌ Você não tem um personagem!",
                ephemeral=True
            )
            return
        
        # Valida valores
        attrs = Attributes(
            strength=forca,
            dexterity=destreza,
            intelligence=inteligencia,
            wisdom=sabedoria,
            charisma=carisma
        )
        
        if not attrs.validate():
            await interaction.response.send_message(
                f"❌ Valores inválidos! Todos devem estar entre {Attributes.MIN_VALUE} e {Attributes.MAX_VALUE}.",
                ephemeral=True
            )
            return
        
        # Atualiza e salva
        character.attributes = attrs
        self.character_repo.save_character(character)
        
        embed = discord.Embed(
            title="✅ Atributos Alocados!",
            color=discord.Color.green()
        )
        
        mods = character.get_modifiers()
        embed.add_field(
            name="Seus Atributos",
            value=(
                f"**Força:** {attrs.strength} ({mods.strength_mod:+d})\n"
                f"**Destreza:** {attrs.dexterity} ({mods.dexterity_mod:+d})\n"
                f"**Inteligência:** {attrs.intelligence} ({mods.intelligence_mod:+d})\n"
                f"**Sabedoria:** {attrs.wisdom} ({mods.wisdom_mod:+d})\n"
                f"**Carisma:** {attrs.charisma} ({mods.charisma_mod:+d})"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== DESCANSAR ====================
    
    @rpg_group.command(name="descansar", description="Descansa para recuperar HP e Mana")
    async def rest(self, interaction: discord.Interaction):
        """Descansa e recupera todos os HP e Mana."""
        
        character = self.character_repo.load_character(interaction.user.id)
        if not character:
            await interaction.response.send_message(
                "❌ Você não tem um personagem!",
                ephemeral=True
            )
            return
        
        old_hp = character.current_hp
        old_resources = character.resource_points
        
        character.rest()
        self.character_repo.save_character(character)
        
        embed = discord.Embed(
            title="😴 Você descansou",
            color=discord.Color.green()
        )
        embed.add_field(
            name="❤️ HP Recuperado",
            value=f"{old_hp} → {character.current_hp}/{character.max_hp}",
            inline=False
        )
        embed.add_field(
            name="✨ Mana/Energia Recuperada",
            value=f"{old_resources} → {character.resource_points}/{character.max_resource_points}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== CLASSES ====================
    
    @rpg_group.command(name="classes", description="Lista todas as classes disponíveis")
    async def list_classes(self, interaction: discord.Interaction):
        """Mostra todas as classes disponíveis."""
        
        classes = list_available_classes()
        
        embed = discord.Embed(
            title="⚔️ Classes Disponíveis",
            color=discord.Color.gold()
        )
        
        for class_name in classes:
            character_class = get_class_by_name(class_name)
            if character_class:
                embed.add_field(
                    name=character_class.name,
                    value=character_class.description,
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== DELETAR PERSONAGEM ====================
    
    @rpg_group.command(name="deletar", description="Deleta seu personagem")
    async def delete_character(self, interaction: discord.Interaction):
        """Deleta o personagem atual."""
        
        character = self.character_repo.load_character(interaction.user.id)
        if not character:
            await interaction.response.send_message(
                "❌ Você não tem um personagem!",
                ephemeral=True
            )
            return
        
        self.character_repo.delete_character(interaction.user.id)
        
        await interaction.response.send_message(
            f"✅ Personagem **{character.name}** foi deletado.",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    """Carrega a Cog no bot."""
    await bot.add_cog(RPGCog(bot))
