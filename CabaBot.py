import discord
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv, find_dotenv

# Carrega .env (procura automaticamente no projeto)
load_dotenv(find_dotenv())

# Aceita TOKEN ou DISCORD_TOKEN, remove espaços/aspas acidentais
_token_raw = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN")
if not _token_raw:
    raise RuntimeError("TOKEN não encontrado. Defina 'TOKEN' no arquivo .env ou nas variáveis de ambiente.")

TOKEN = _token_raw.strip().strip('"').strip("'")

# Segurança: mostra apenas o comprimento para confirmar leitura
print(f"TOKEN carregado ({len(TOKEN)} caracteres)")

class CabaBot(discord.Client):
    def __init__(self):
        # Intents default são mais leves e suficientes para a maioria dos bots
        intents = discord.Intents.default()
        intents.voice_states = True  # Necessário para comandos relacionados a voz
        intents.members = True  # Necessário para acessar informações dos membros
        intents.messages = True  # Necessário para comandos relacionados a mensagens
        intents.message_content = True  # Necessário para ler o conteúdo das mensagens
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sincroniza os comandos "barra" (/) com o Discord
        await self.tree.sync()
        print("Comandos sincronizados!")

    async def on_ready(self):
        print(f'Arriégua! {self.user} está online papai!')


bot = CabaBot()

# --- COMANDOS ---

@bot.tree.command(name="timer", description="Define um timer em segundos")
@app_commands.describe(segundos="Quantos segundos quer esperar?")
async def timer(interaction: discord.Interaction, segundos: int):
    async def safe_send(content: str, *, ephemeral: bool = True):
        if interaction.response.is_done():
            await interaction.followup.send(content, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(content, ephemeral=ephemeral)

    if interaction.guild is None:
        await safe_send("Este comando só funciona dentro de um servidor.", ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member):
        await safe_send("Este comando só funciona dentro de um servidor.", ephemeral=True)
        return
    member: discord.Member = interaction.user

    if not member.voice or not member.voice.channel:
        await safe_send("Você precisa estar em um canal de voz!", ephemeral=True)
        return

    # Confirme a interação, pois aguardaremos (evita timeouts). 
    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=True)

    # Trabalho de longa duração
    await asyncio.sleep(segundos)

    # Enviar resultado como acompanhamento (ou como resposta, caso ainda não tenha sido respondido).
    await safe_send(f"{member.mention} ⏱️ Timer finalizado: {segundos} segundos", ephemeral=True)

@bot.tree.command(name="teste", description="Comando de teste simples")
async def teste(interaction: discord.Interaction):
    # 'ephemeral=True' faz a mensagem aparecer apenas para você (privada)
    await interaction.response.send_message(
        f"Nasci agora, {interaction.user.mention}! Estou pronto.", 
        ephemeral=True
    )

@bot.tree.command(name="soma", description="Soma dois números")
@app_commands.describe(num1="O primeiro número", num2="O segundo número")
async def soma(interaction: discord.Interaction, num1: float, num2: float):
    resultado = num1 + num2
    await interaction.response.send_message(f"A soma de {num1} + {num2} é **{resultado}**")

@bot.tree.command(name="perfil", description="Mostra o avatar de um membro (Exemplo com Embed)")
@app_commands.describe(membro="Escolha um usuário")
async def perfil(interaction: discord.Interaction, membro: discord.Member):
    # Cria um card bonito (Embed)
    embed = discord.Embed(
        title=f"Perfil de {membro.display_name}",
        color=discord.Color.dark_blue()
    )
    embed.set_image(url=membro.avatar.url if membro.avatar else membro.default_avatar.url)
    
    await interaction.response.send_message(embed=embed)

# --- EXECUÇÃO ---

if __name__ == "__main__":
    bot.run(TOKEN)