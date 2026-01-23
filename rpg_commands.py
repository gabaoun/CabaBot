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
    
    # ==================== HELPERS ====================

    def _get_rpg_channel_id(self, guild_id: int) -> Optional[int]:
        """Retorna o ID do canal RPG configurado para a guild."""
        try:
            config = self.bot.get_guild_config(guild_id)
            return config.get("rpg_channel_id")
        except AttributeError:
            return None

    def _set_rpg_channel_id(self, guild_id: int, channel_id: int) -> None:
        """Define o ID do canal RPG para a guild."""
        try:
            self.bot.set_guild_config(guild_id, "rpg_channel_id", channel_id)
        except AttributeError:
            pass

    async def _safe_send(self, guild_id: int, content: str = None, embed: discord.Embed = None, view: discord.ui.View = None, interaction: discord.Interaction = None) -> bool:
        """
        Tenta enviar uma mensagem no canal RPG configurado.
        Se falhar (canal deletado/sem permissão), loga no terminal.
        
        Se interaction for fornecida e o canal não estiver configurado, 
        responde na interaction (fallback).
        """
        channel_id = self._get_rpg_channel_id(guild_id)
        
        # Se não tem canal configurado, usa a interaction se disponível
        if not channel_id:
            if interaction and not interaction.response.is_done():
                await interaction.response.send_message(content=content, embed=embed, view=view or discord.utils.MISSING, ephemeral=True)
                return True
            return False

        channel = self.bot.get_channel(channel_id)
        
        # Se canal não existe (foi deletado) ou bot não consegue ver
        if not channel:
            print(f"⚠️ [RPG] Erro: Canal RPG {channel_id} não encontrado na guild {guild_id}.")
            if interaction and not interaction.response.is_done():
                 await interaction.response.send_message("⚠️ O canal RPG configurado não foi encontrado. Por favor, reconfigure com `/rpg canal`.", ephemeral=True)
            return False

        try:
            if isinstance(channel, (discord.TextChannel, discord.Thread)):
                await channel.send(content=content, embed=embed, view=view or discord.utils.MISSING)
                
                # Se foi chamado via interaction, confirma visualmente que foi enviado lá
                if interaction and not interaction.response.is_done():
                    await interaction.response.send_message(f"✅ Enviado no canal {channel.mention}", ephemeral=True)
                return True
        except discord.Forbidden:
            print(f"⚠️ [RPG] Erro: Permissão negada para enviar mensagem no canal {channel_id} (Guild {guild_id}).")
        except Exception as e:
            print(f"⚠️ [RPG] Erro ao enviar mensagem: {e}")
            
        return False

    # ==================== CONFIGURAÇÃO ====================

    @rpg_group.command(name="canal", description="Define o canal exclusivo para o RPG")
    @app_commands.describe(canal="O canal de texto onde o RPG vai acontecer")
    async def set_rpg_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Define o canal onde os eventos e mensagens do RPG serão enviados."""
        self._set_rpg_channel_id(interaction.guild_id, canal.id)
        await interaction.response.send_message(f"✅ Canal do RPG definido para {canal.mention}! Todas as aventuras acontecerão lá.", ephemeral=True)

    # ==================== JOGAR (ENTRY POINT) ====================

    @rpg_group.command(name="jogar", description="Começa sua jornada ou continua de onde parou")
    async def play_rpg(self, interaction: discord.Interaction):
        """Ponto de entrada principal para o RPG."""
        character = self.character_repo.load_character(interaction.user.id)
        
        # Cenário 1: Sem personagem
        if not character:
            embed = discord.Embed(
                title="🐉 Bem-vindo ao CabaRPG!",
                description=(
                    "Você ainda não tem um personagem. Para começar sua aventura, "
                    "você precisa criar sua ficha.\n\n"
                    "**Como começar:**\n"
                    "1. Use `/rpg criar` escolhendo um nome e uma classe.\n"
                    "2. Use `/rpg classes` para ver as opções.\n"
                ),
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Cenário 2: Personagem existe, verificar atributos
        # Se a soma dos atributos for igual aos valores base (assumindo base 0 ou 10*5=50 muito baixo)
        # Vamos assumir que se a soma for < 50 (média 10), ele ainda não alocou
        total_stats = (
            character.attributes.strength + 
            character.attributes.dexterity + 
            character.attributes.intelligence + 
            character.attributes.wisdom + 
            character.attributes.charisma
        )
        
        # Se os atributos ainda estão muito baixos (padrão inicial pode ser 1 ou 10)
        # O sistema Attributes.py define defaults como 10. 10*5 = 50.
        # Se o jogador tiver exatamente 50 pontos, assumimos que ele não distribuiu ainda, 
        # pois o sistema "balanceado" permite até 72.
        if total_stats <= 55:
            pontos_restantes = 72 - total_stats
            embed = discord.Embed(
                title=f"👋 Olá, {character.name}!",
                description=(
                    "Sua ficha foi criada, mas seus atributos parecem básicos.\n\n"
                    "🎯 **Você tem pontos para alocar!**\n"
                    "O sistema permite distribuir até **72 pontos** totais entre seus 5 atributos.\n"
                    "Atualmente você tem: **50 pontos** (Padrão).\n\n"
                    "**Use `/rpg atributos` para distribuir seus pontos.**\n"
                    "Exemplo: `/rpg atributos forca:15 destreza:14 inteligencia:13 sabedoria:12 carisma:10`"
                ),
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Cenário 3: Tudo pronto
        channel_id = self._get_rpg_channel_id(interaction.guild_id)
        canal_msg = f"<#{channel_id}>" if channel_id else "neste canal"
        
        embed = discord.Embed(
            title="⚔️ Hora da Aventura!",
            description=(
                f"Tudo pronto com **{character.name}** (Nível {character.level} {character.character_class.name}).\n\n"
                f"🎲 **O que fazer?**\n"
                f"- Espere por eventos em {canal_msg}\n"
                f"- Use `/evento encontro` para buscar confusão\n"
                f"- Use `/rpg perfil` para ver seus itens e ouro"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

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
            title=f"📋 Ficha de {character.name}",
            description=f"**{character.character_class.name}** | Nível {character.level}",
            color=discord.Color.blue()
        )
        
        # Atributos
        attrs = character.attributes
        embed.add_field(
            name="📊 Atributos",
            value=(
                f"**FOR:** {attrs.strength} ({mods.strength_mod:+d}) | "
                f"**DES:** {attrs.dexterity} ({mods.dexterity_mod:+d}) | "
                f"**INT:** {attrs.intelligence} ({mods.intelligence_mod:+d})\n"
                f"**SAB:** {attrs.wisdom} ({mods.wisdom_mod:+d}) | "
                f"**CAR:** {attrs.charisma} ({mods.charisma_mod:+d})"
            ),
            inline=False
        )
        
        # Saúde e Recursos
        hp_percent = int((character.current_hp / character.max_hp) * 100)
        hp_bar = "🟩" * (hp_percent // 20) + "⬜" * (5 - (hp_percent // 20))
        
        resource_percent = int((character.resource_points / character.max_resource_points) * 100)
        resource_bar = "🟦" * (resource_percent // 20) + "⬜" * (5 - (resource_percent // 20))
        
        embed.add_field(
            name=f"❤️ HP: {character.current_hp}/{character.max_hp}",
            value=hp_bar,
            inline=True
        )
        embed.add_field(
            name=f"✨ Mana: {character.resource_points}/{character.max_resource_points}",
            value=resource_bar,
            inline=True
        )
        
        # Equipamentos
        equipped_items = character.inventory.get_equipped_items()
        equipped_text = "Nenhum"
        if equipped_items:
            equipped_text = "\n".join([f"**{eq.slot.value.capitalize()}:** {eq.name}" for eq in equipped_items])
        
        embed.add_field(name="🛡️ Equipamentos", value=equipped_text, inline=False)

        # Inventário Resumido
        inventory_items = list(character.inventory.items.values())
        inv_text = "Vazio"
        if inventory_items:
            # Lista os primeiros 5 itens
            item_list = [f"{item.quantity}x {item.name}" for item in inventory_items[:5]]
            if len(inventory_items) > 5:
                item_list.append(f"...e mais {len(inventory_items) - 5}")
            inv_text = ", ".join(item_list)
        
        embed.add_field(
            name=f"🎒 Mochila ({len(inventory_items)}/{character.inventory.max_capacity})", 
            value=inv_text, 
            inline=True
        )
        embed.add_field(
            name="💰 Ouro", 
            value=f"{character.inventory.money} moedas", 
            inline=True
        )
        
        # XP Bar
        next_level_xp = 1000 * character.level
        xp_percent = int((character.experience / next_level_xp) * 100)
        xp_bar_char = "🟨" * (xp_percent // 10) + "⬛" * (10 - (xp_percent // 10))
        embed.add_field(name=f"⭐ XP: {character.experience}/{next_level_xp}", value=xp_bar_char, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== ATRIBUTOS ====================
    
    @rpg_group.command(name="atributos", description="Aloca pontos em atributos (Max total: 72)")
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
        """Aloca pontos em atributos (máx 20 por atributo, soma max 72)."""
        
        character = self.character_repo.load_character(interaction.user.id)
        if not character:
            await interaction.response.send_message(
                "❌ Você não tem um personagem!",
                ephemeral=True
            )
            return
        
        # Valida soma total (Balanceamento)
        total_points = forca + destreza + inteligencia + sabedoria + carisma
        MAX_POINTS = 72
        
        if total_points > MAX_POINTS:
            await interaction.response.send_message(
                f"❌ **Muitos pontos!** A soma dos atributos deu **{total_points}**.\n"
                f"O limite máximo para balanceamento é **{MAX_POINTS}** pontos.\n"
                f"Tente reduzir alguns valores.",
                ephemeral=True
            )
            return

        # Valida valores individuais
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
        # Recalcula HP e recursos baseados nos novos atributos
        character.max_hp = character.character_class.get_hit_points_per_level() * character.level + attrs.get_modifiers().strength_mod
        character.current_hp = min(character.current_hp, character.max_hp) # Ajusta se o max diminuiu
        character.max_resource_points = 10 + (attrs.intelligence * 2) + ((character.level - 1) * 5)
        character.resource_points = min(character.resource_points, character.max_resource_points)

        self.character_repo.save_character(character)
        
        embed = discord.Embed(
            title="✅ Atributos Alocados!",
            description=f"Total de pontos usados: **{total_points}/{MAX_POINTS}**",
            color=discord.Color.green()
        )
        
        mods = character.get_modifiers()
        embed.add_field(
            name="Seus Novos Atributos",
            value=(
                f"**FOR:** {attrs.strength} ({mods.strength_mod:+d})\n"
                f"**DES:** {attrs.dexterity} ({mods.dexterity_mod:+d})\n"
                f"**INT:** {attrs.intelligence} ({mods.intelligence_mod:+d})\n"
                f"**SAB:** {attrs.wisdom} ({mods.wisdom_mod:+d})\n"
                f"**CAR:** {attrs.charisma} ({mods.charisma_mod:+d})"
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
