import discord
from discord import app_commands

# Token
TOKEN = "MTQ2Mzg5OTgzNDIyNTUyOTAwMA.Gulwv1.m0uOFF-vByHORHLBOEWlVXhlGcr694RPYginTg" 

class CabaBot(discord.Client):
    def __init__(self):
        # Intents default são mais leves e suficientes para a maioria dos bots
        intents = discord.Intents.default()
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