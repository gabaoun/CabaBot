import discord
from discord import app_commands

class CabaBot(discord.Client):


    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            intents = intents
        )
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f'Arriégua, {self.user} está online papai!')

bot = CabaBot()

@bot.tree.command(name="teste", description="Comando de teste")
async def teste(interaction: discord.Interaction):
    await interaction.response.send_message(f"Nasci agora, {interaction.user.mention}, Estou pronto!")

@bot.tree.command(name="soma", description="Some dois números")
@app_commands.describe(num1="O primeiro número", num2="O segundo número")
async def soma(interaction: discord.Interaction, num1: float, num2: float):
    await interaction.response.send_message(f"A soma de {num1} e {num2} é {num1 + num2}", ephemeral=True)

bot.run("MTQ2Mzg5OTgzNDIyNTUyOTAwMA.Gulwv1.m0uOFF-vByHORHLBOEWlVXhlGcr694RPYginTg")
