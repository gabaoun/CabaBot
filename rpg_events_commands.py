"""
Comandos de Eventos RPG para Discord

Comandos para disparar eventos e encontros.
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import random
import asyncio
from typing import Optional, Dict

from rpg_system import Character, CharacterRepository, NPC
from rpg_system.events import EventRepository, create_event_repository_with_defaults
from rpg_system.npcs import NPCRepository, create_npc_repository_with_defaults


class EventsCog(commands.Cog):
    """Cog para eventos e encontros do RPG."""
    
    def __init__(self, bot: commands.Bot, char_repo: CharacterRepository, 
                 event_repo: EventRepository, npc_repo: NPCRepository):
        self.bot = bot
        self.character_repo = char_repo
        self.event_repo = event_repo
        self.npc_repo = npc_repo
        self.active_events: dict = {}
        
    async def cog_load(self):
        """Chamado quando a Cog é carregada."""
        self.random_event_loop.start()

    async def cog_unload(self):
        """Chamado quando a Cog é descarregada."""
        self.random_event_loop.cancel()

    @tasks.loop(minutes=1)
    async def random_event_loop(self):
        """Loop que tenta disparar eventos aleatórios a cada minuto."""
        # Chance de evento: intervalo de 2-4 minutos significa aprox 25-50% chance por minuto
        # Vamos usar 33% de chance por minuto para média de 3 min
        if random.random() > 0.33:
            return

        for guild in self.bot.guilds:
            try:
                # Verifica se tem canal RPG configurado
                config = self.bot.get_guild_config(guild.id)
                rpg_channel_id = config.get("rpg_channel_id")
                
                if not rpg_channel_id:
                    continue
                    
                channel = self.bot.get_channel(rpg_channel_id)
                if not channel:
                    continue

                # Escolhe tipo de evento (50% evento, 50% NPC)
                if random.choice([True, False]):
                    # Evento aleatório
                    event = self.event_repo.get_random_event()
                    if not event: continue
                    
                    embed = discord.Embed(
                        title=f"⚡ Evento Aleatório: {event.name}",
                        description=event.description,
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Dificuldade", value="⭐" * event.difficulty)
                    embed.add_field(
                        name="Recompensa",
                        value=f"EXP: {event.min_exp_reward}-{event.max_exp_reward}\n"
                              f"Ouro: {event.min_gold_reward}-{event.max_gold_reward}",
                        inline=False
                    )
                    # Adiciona checks se houver
                    if event.required_checks:
                         checks_str = ", ".join([f"{k.capitalize()}: {v}" for k, v in event.required_checks.items()])
                         embed.add_field(name="Testes Necessários", value=checks_str, inline=False)

                    view = EventResponseView(self, None, event) # interaction é None aqui
                    await channel.send(f"@everyone 🎲 Algo está acontecendo!", embed=embed, view=view)
                
                else:
                    # Encontro NPC
                    npc = self.npc_repo.get_random_npc()
                    if not npc: continue
                    
                    embed = discord.Embed(
                        title=f"👹 Encontro Aleatório: {npc.name}",
                        description=npc.description,
                        color=discord.Color.orange()
                    )
                    embed.add_field(name="Título", value=npc.title)
                    embed.add_field(name="Nível", value=str(npc.level))
                    embed.add_field(name="Classe", value=npc.npc_class.name if npc.npc_class else "Desconhecida")
                    
                    view = EncounterResponseView(self, None, npc) # interaction é None aqui
                    await channel.send(f"@everyone 👀 Um vulto se aproxima...", embed=embed, view=view)
                    
            except Exception as e:
                print(f"Erro no loop de eventos para guild {guild.name}: {e}")

    @random_event_loop.before_loop
    async def before_random_event_loop(self):
        await self.bot.wait_until_ready()
    
    events_group = app_commands.Group(name="evento", description="Comandos de eventos RPG")
    
    @events_group.command(name="aleatorio", description="Dispara um evento aleatório")
    @app_commands.describe(dificuldade="Dificuldade (1-5)")
    async def random_event(
        self,
        interaction: discord.Interaction,
        dificuldade: Optional[int] = None
    ):
        """Dispara um evento aleatório no servidor."""
        
        # 1. Determina o canal alvo
        target_channel = interaction.channel
        rpg_channel_id = None
        try:
            config = self.bot.get_guild_config(interaction.guild_id)
            rpg_channel_id = config.get("rpg_channel_id")
        except AttributeError:
            pass

        if rpg_channel_id:
            fetched_channel = self.bot.get_channel(rpg_channel_id)
            if fetched_channel:
                target_channel = fetched_channel
            else:
                print(f"⚠️ [RPG] Canal configurado {rpg_channel_id} não encontrado.")
                await interaction.response.send_message("⚠️ Canal RPG configurado não encontrado. Reconfigure com `/rpg canal`.", ephemeral=True)
                return

        # 2. Obtém evento
        event = self.event_repo.get_random_event(dificuldade)
        if not event:
            await interaction.response.send_message(
                "❌ Nenhum evento disponível!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"⚡ {event.name}",
            description=event.description,
            color=discord.Color.red()
        )
        embed.add_field(name="Dificuldade", value="⭐" * event.difficulty)
        embed.add_field(
            name="Recompensa",
            value=f"EXP: {event.min_exp_reward}-{event.max_exp_reward}\n"
                  f"Ouro: {event.min_gold_reward}-{event.max_gold_reward}",
            inline=False
        )
        
        view = EventResponseView(self, interaction, event)
        
        # 3. Envia para o canal alvo com segurança
        try:
            # Se o canal alvo for diferente da interação, manda lá e responde efemero aqui
            if target_channel.id != interaction.channel_id:
                await target_channel.send(f"@everyone Um evento começou!", embed=embed, view=view)
                await interaction.response.send_message(f"✅ Evento disparado em {target_channel.mention}!", ephemeral=True)
            else:
                # Se for o mesmo canal, responde normal
                await interaction.response.send_message(f"@everyone Um evento começou!", embed=embed, view=view)
                
        except (discord.Forbidden, discord.NotFound) as e:
            print(f"⚠️ [RPG] Erro ao enviar evento: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ Erro ao acessar o canal do evento.", ephemeral=True)
        
        self.active_events[interaction.guild_id] = {
            "event": event,
            "participants": [],
            "start_time": asyncio.get_event_loop().time()
        }
    
    @events_group.command(name="encontro", description="Encontra um NPC aleatório")
    async def encounter_npc(self, interaction: discord.Interaction):
        """Encontra um NPC aleatório para uma batalha ou negociação."""
        
        # 1. Determina o canal alvo
        target_channel = interaction.channel
        rpg_channel_id = None
        try:
            config = self.bot.get_guild_config(interaction.guild_id)
            rpg_channel_id = config.get("rpg_channel_id")
        except AttributeError:
            pass

        if rpg_channel_id:
            fetched_channel = self.bot.get_channel(rpg_channel_id)
            if fetched_channel:
                target_channel = fetched_channel
            else:
                print(f"⚠️ [RPG] Canal configurado {rpg_channel_id} não encontrado.")
                await interaction.response.send_message("⚠️ Canal RPG configurado não encontrado. Reconfigure com `/rpg canal`.", ephemeral=True)
                return

        npc = self.npc_repo.get_random_npc()
        if not npc:
            await interaction.response.send_message(
                "❌ Nenhum NPC disponível!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"👹 Encontro: {npc.name}",
            description=npc.description,
            color=discord.Color.orange()
        )
        embed.add_field(name="Título", value=npc.title)
        embed.add_field(name="Nível", value=str(npc.level))
        embed.add_field(
            name="Saúde",
            value=f"{npc.current_hp}/{npc.max_hp}",
            inline=True
        )
        embed.add_field(
            name="Classe",
            value=npc.npc_class.name if npc.npc_class else "Desconhecida",
            inline=True
        )
        
        if npc.title.lower() == "inimigo":
            loot_money = npc.inventory.money if npc.inventory else 0
            loot_items = len(npc.inventory.items) if npc.inventory else 0
            embed.add_field(
                name="Possível Loot",
                value=f"💰 Ouro: {loot_money}\n"
                      f"🎁 Itens: {loot_items}",
                inline=False
            )
        
        view = EncounterResponseView(self, interaction, npc)
        
        # 3. Envia para o canal alvo com segurança
        try:
            if target_channel.id != interaction.channel_id:
                await target_channel.send(f"{interaction.user.mention} encontrou algo!", embed=embed, view=view)
                await interaction.response.send_message(f"✅ Encontro iniciado em {target_channel.mention}!", ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, view=view)
        except (discord.Forbidden, discord.NotFound) as e:
            print(f"⚠️ [RPG] Erro ao enviar encontro: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ Erro ao acessar o canal do evento.", ephemeral=True)
    
    @events_group.command(name="listar", description="Lista todos os eventos disponíveis")
    async def list_events(self, interaction: discord.Interaction):
        """Lista todos os eventos registrados."""
        
        events = self.event_repo.list_all_events()
        if not events:
            await interaction.response.send_message(
                "❌ Nenhum evento disponível!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📋 Eventos Disponíveis",
            color=discord.Color.blue()
        )
        
        for event_id, event in list(events.items())[:25]:  # Discord limit
            embed.add_field(
                name=f"{event.name} {'⭐' * event.difficulty}",
                value=event.description,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)


class EventResponseView(discord.ui.View):
    """View para responder a um evento."""
    
    def __init__(self, cog: "EventsCog", interaction: discord.Interaction, event):
        super().__init__(timeout=300)  # 5 minutos
        self.cog = cog
        self.interaction = interaction
        self.event = event
        self.participants: Dict[int, Dict] = {}
    
    @discord.ui.button(label="Participar", style=discord.ButtonStyle.primary)
    async def participate(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Usuário participa do evento."""
        
        character = self.cog.character_repo.load_character(interaction.user.id)
        if not character:
            await interaction.response.send_message(
                "❌ Você não tem um personagem!",
                ephemeral=True
            )
            return
        
        if interaction.user.id in self.participants:
            await interaction.response.send_message(
                "✅ Você já está participando!",
                ephemeral=True
            )
            return
        
        # Realiza testes de atributo
        success = True
        results = []
        
        for attr_name, required_value in self.event.required_checks.items():
            attr_value = getattr(character.attributes, attr_name, 10)
            test_roll = random.randint(1, 20)
            
            # Simples: roll + modificador vs required
            mod = (attr_value - 10) // 2
            total = test_roll + mod
            
            result = total >= required_value
            success = success and result
            
            results.append(
                f"{'✅' if result else '❌'} {attr_name.capitalize()}: "
                f"D20({test_roll}) + {mod:+d} = {total} vs {required_value}"
            )
        
        self.participants[interaction.user.id] = {
            "character": character,
            "success": success,
            "results": results
        }
        
        embed = discord.Embed(
            title="🎲 Teste de Atributos",
            color=discord.Color.green() if success else discord.Color.red()
        )
        embed.add_field(
            name="Resultado",
            value="\n".join(results) if results else "Nenhum teste requerido",
            inline=False
        )
        
        if success:
            exp, gold = self.event.get_random_reward()
            character.gain_experience(exp)
            character.inventory.add_money(gold)
            self.cog.character_repo.save_character(character)
            
            embed.add_field(
                name="✅ Sucesso!",
                value=f"Ganhou {exp} XP e {gold} ouro!",
                inline=False
            )
        else:
            # Leve dano em caso de falha
            damage = random.randint(5, 15)
            character.take_damage(damage)
            self.cog.character_repo.save_character(character)
            
            embed.add_field(
                name="❌ Falha!",
                value=f"Você tomou {damage} dano!",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class EncounterResponseView(discord.ui.View):
    """View para responder a um encontro com NPC."""
    
    def __init__(self, cog: EventsCog, interaction: Optional[discord.Interaction], npc: NPC):
        super().__init__(timeout=300)
        self.cog = cog
        self.interaction = interaction
        self.npc = npc
    
    @discord.ui.button(label="Atacar", style=discord.ButtonStyle.red)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ataca o NPC."""
        
        character = self.cog.character_repo.load_character(interaction.user.id)
        if not character:
            await interaction.response.send_message(
                "❌ Você não tem um personagem!",
                ephemeral=True
            )
            return
        
        # Calcula dano
        mods = character.get_modifiers()
        base_damage = random.randint(1, 8)
        damage = base_damage + mods.get_attack_bonus()
        
        # NPC toma dano
        alive = self.npc.take_damage(damage)
        
        embed = discord.Embed(
            title="⚔️ Ataque!",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Dano Causado",
            value=f"D8({base_damage}) + {mods.get_attack_bonus():+d} = {damage}",
            inline=False
        )
        embed.add_field(
            name="Saúde do NPC",
            value=f"{self.npc.current_hp}/{self.npc.max_hp}",
            inline=False
        )
        
        if alive:
            embed.add_field(
                name="Status",
                value="O NPC ainda está em pé!",
                inline=False
            )
        else:
            embed.add_field(
                name="🎉 Vitória!",
                value="Você derrotou o NPC!",
                inline=False
            )
            
            # Distribui loot
            gold, items = self.npc.get_loot()
            character.inventory.add_money(gold)
            for item in items:
                character.inventory.add_item(item)
            
            exp_reward = 50 * self.npc.level
            character.gain_experience(exp_reward)
            self.cog.character_repo.save_character(character)
            
            embed.add_field(
                name="Loot",
                value=f"💰 {gold} ouro\n📦 {len(items)} itens\n⭐ {exp_reward} XP",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Conversar", style=discord.ButtonStyle.green)
    async def talk(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Conversa com o NPC."""
        
        character = self.cog.character_repo.load_character(interaction.user.id)
        if not character:
            await interaction.response.send_message(
                "❌ Você não tem um personagem!",
                ephemeral=True
            )
            return
        
        mods = character.get_modifiers()
        
        # Teste de Carisma
        test_roll = random.randint(1, 20)
        total = test_roll + mods.get_charisma_bonus()
        success = total >= 12
        
        embed = discord.Embed(
            title="💬 Negociação",
            color=discord.Color.purple()
        )
        embed.add_field(
            name="Teste de Carisma",
            value=f"D20({test_roll}) + {mods.get_charisma_bonus():+d} = {total}",
            inline=False
        )
        
        if success:
            embed.add_field(
                name="✅ Negociação Bem-sucedida!",
                value="Você conversa pacificamente com o NPC.",
                inline=False
            )
            
            if self.npc.title.lower() == "mercador":
                embed.add_field(
                    name="🏪 Itens à Venda",
                    value="Visite novamente para comprar itens!",
                    inline=False
                )
        else:
            embed.add_field(
                name="❌ Negociação Fracassou",
                value="O NPC não quer conversar com você.",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Huir", style=discord.ButtonStyle.secondary)
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Tenta fugir do encontro."""
        
        character = self.cog.character_repo.load_character(interaction.user.id)
        if not character:
            await interaction.response.send_message(
                "❌ Você não tem um personagem!",
                ephemeral=True
            )
            return
        
        mods = character.get_modifiers()
        
        # Teste de Destreza
        test_roll = random.randint(1, 20)
        total = test_roll + mods.get_finesse_bonus()
        success = total >= 12
        
        embed = discord.Embed(
            title="🏃 Fuga",
            color=discord.Color.yellow()
        )
        embed.add_field(
            name="Teste de Destreza",
            value=f"D20({test_roll}) + {mods.get_finesse_bonus():+d} = {total}",
            inline=False
        )
        
        if success:
            embed.add_field(
                name="✅ Você conseguiu fugir!",
                value="Você desaparece rapidamente",
                inline=False
            )
        else:
            damage = random.randint(5, 10)
            character.take_damage(damage)
            self.cog.character_repo.save_character(character)
            
            embed.add_field(
                name="❌ Você não conseguiu fugir!",
                value=f"Você tomou {damage} dano enquanto fugia",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    """Carrega a Cog no bot."""
    # Nota: Esta função será chamada pelo bot principal
    pass
