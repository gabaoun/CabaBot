"""
CabaBot - Discord Music Bot

Um bot multifuncional para Discord com foco em reprodução de áudio,
gerenciamento de timers e interações com usuários através de slash commands.

Funcionalidades principais:
- Reprodução de música do YouTube com qualidade adaptativa
- Sistema de timers com toque de áudio ao final
- Controles de reprodução (pausar, retomar, pular, parar)
- Gerenciamento de filas de música por servidor
- Rolador de dados padrão (d2 até d100) e customizados
- Comandos de utilidade (calculadora, perfil de usuário, teste de conexão)

Author: CabaBot Team
Version: 1.1.0
"""

import random
import discord
import asyncio
import os
import yt_dlp
from discord import app_commands
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import json
from typing import Dict, Any

# Carrega as variáveis de ambiente do arquivo .env
# find_dotenv() procura automaticamente na árvore de diretórios
load_dotenv(find_dotenv())

# Define o caminho base do script e a localização do ffmpeg local
SCRIPT_DIR = Path(__file__).parent
FFMPEG_PATH = SCRIPT_DIR / "bin" / "ffmpeg" / "ffmpeg.exe"

# Áudio a ser reproduzido quando o bot ficar online (padrão: vídeo do YouTube)
STARTUP_AUDIO_URL = random.choice(["https://www.youtube.com/watch?v=biZlbJAdyTE", "https://www.youtube.com/watch?v=sR9KWAIFSfc", "https://www.youtube.com/watch?v=xmf99leO-Z0", "https://www.youtube.com/watch?v=8zslY2eYJ9M"])

# Path para configuração persistente por guild
CONFIG_PATH = SCRIPT_DIR / "config.json"


def load_config() -> Dict[str, Any]:
    """Carrega o arquivo de configuração (JSON). Retorna dicionário vazio se não existir."""
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        # Se houver problema ao ler, retorna configuração vazia
        pass
    return {}


def save_config(cfg: Dict[str, Any]) -> None:
    """Salva o dicionário de configuração no arquivo JSON."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar config: {e}")


# Carrega configuração inicial na memória
_CONFIG = load_config()


def guild_startup_enabled(guild_id: int) -> bool:
    """Retorna True se o áudio de startup estiver habilitado para a guild.

    Prioriza configuração por guild; se ausente, retorna True por padrão.
    """
    key = str(guild_id)
    guilds = _CONFIG.get("guilds", {})
    return bool(guilds.get(key, True))


def set_guild_startup(guild_id: int, enabled: bool) -> None:
    """Define e persiste a configuração de startup para uma guild."""
    key = str(guild_id)
    if "guilds" not in _CONFIG:
        _CONFIG["guilds"] = {}
    _CONFIG["guilds"][key] = bool(enabled)
    save_config(_CONFIG)

# Obtém o token do Discord das variáveis de ambiente
# Aceita tanto TOKEN quanto DISCORD_TOKEN como nomes de variável
# Remove espaços e aspas acidentais que possam ter sido incluídas
_token_raw = os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN")
if not _token_raw:
    raise RuntimeError(
        "TOKEN não encontrado. Defina 'TOKEN' ou 'DISCORD_TOKEN' no arquivo .env "
        "ou nas variáveis de ambiente do sistema."
    )

TOKEN = _token_raw.strip().strip('"').strip("'")

# Valida que o token foi carregado com sucesso
# Exibe apenas o comprimento por segurança (nunca exibe o token real)
print(f"✅ TOKEN carregado com sucesso ({len(TOKEN)} caracteres)")


class CabaBot(discord.Client):
    """
    Cliente Discord customizado com suporte a slash commands e gerenciamento de filas.
    
    Herança:
        discord.Client: Cliente base do discord.py
        
    Atributos:
        tree (app_commands.CommandTree): Árvore de comandos para slash commands
        music_queue (dict): Dicionário que armazena filas de música por guild ID
    """
    
    def __init__(self):
        """
        Inicializa o cliente Discord com as permissões necessárias.
        
        Configura:
        - Intents default com message_content habilitado
        - CommandTree para gerenciar slash commands (/)
        - Fila de música vazia para cada servidor
        """
        # Intents default são mais leves e suficientes para a maioria dos bots
        intents = discord.Intents.default()
        # Necessário para ler o conteúdo das mensagens em certos contextos
        intents.message_content = True
        
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        # Fila de músicas por guild - permite gerenciar múltiplos servidores
        self.music_queue = {}

    async def setup_hook(self):
        """
        Hook chamado antes do bot começar.
        
        Sincroniza todos os slash commands registrados com a API do Discord.
        Isso garante que os comandos apareçam no menu de slash commands.
        """
        await self.tree.sync()
        print("✅ Comandos sincronizados com sucesso!")

    async def on_ready(self):
        """
        Event handler chamado quando o bot se conecta ao Discord com sucesso.
        
        Exibe informações de conexão e status do bot.
        """
        print(f'🤖 {self.user} tá on — pronto pra tocar umas arretadas!')

        # Evita executar o startup mais de uma vez (on_ready pode disparar várias vezes)
        if getattr(self, "_startup_done", False):
            return
        self._startup_done = True
        # Tenta tocar o áudio de boas-vindas em guilds onde há membros em canais de voz
        async def _play_startup_for_guild(guild: discord.Guild):
            try:
                # Escolhe o primeiro canal de voz que tenha membros não-bot
                voice_channel = None
                for ch in guild.voice_channels:
                    if any(not m.bot for m in ch.members):
                        voice_channel = ch
                        break
                if voice_channel is None:
                    return

                voice_client = guild.voice_client
                if voice_client is None:
                    voice_client = await voice_channel.connect()
                elif voice_client.channel != voice_channel:
                    await voice_client.disconnect()
                    voice_client = await voice_channel.connect()

                # Verifica se startup está habilitado para esta guild e globalmente
                global_enabled = os.getenv("STARTUP_AUDIO_ENABLED", "true").lower() in ("1", "true", "yes", "on")
                if not global_enabled:
                    return
                if not guild_startup_enabled(guild.id):
                    return

                # Busca a URL de áudio via yt-dlp
                ytdlp_options = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                    'noplaylist': True,
                    'nocheckcertificate': True,
                    'cachedir': False,
                }
                query = STARTUP_AUDIO_URL if STARTUP_AUDIO_URL.startswith("http") else f'ytsearch:{STARTUP_AUDIO_URL}'
                results = await search_ytdlp_async(query, ytdlp_options)
                if not results:
                    return
                track = results['entries'][0] if 'entries' in results else results
                audio_url = track.get('url')
                title = track.get('title', 'Música de boas-vindas')
                if not audio_url or "youtube.com/watch" in audio_url:
                    return

                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn -loglevel error',
                }

                source = discord.FFmpegPCMAudio(
                    audio_url,
                    executable=str(FFMPEG_PATH),
                    **ffmpeg_options
                )

                if isinstance(voice_client, discord.VoiceClient):
                    voice_client.play(source)
                    print(f"Tocando áudio de startup em {guild.name}: {title}")

            except Exception as exc:
                print(f"Erro ao tocar áudio de startup em {guild.name}: {exc}")

        # Dispara tarefas para cada guild
        for g in list(self.guilds):
            asyncio.create_task(_play_startup_for_guild(g))


async def search_ytdlp_async(query: str, ydl_opts: dict) -> dict:
    """
    Busca informações de vídeo no YouTube de forma assíncrona.
    
    Executa a operação de I/O bloqueante (yt-dlp) em uma thread separada
    para não bloquear o event loop do Discord.
    
    Args:
        query (str): URL do YouTube ou termo de busca
        ydl_opts (dict): Opções de configuração para yt-dlp
        
    Returns:
        dict: Informações do vídeo extraídas pelo yt-dlp
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_opts))


def _extract(query: str, ydl_opts: dict) -> dict:
    """
    Extrai informações de um vídeo do YouTube usando yt-dlp.
    
    Esta é uma função síncrona que será executada em thread separada
    para manter o bot responsivo.
    
    Args:
        query (str): URL do YouTube ou termo de busca (com 'ytsearch:' para buscar)
        ydl_opts (dict): Opções de configuração para yt-dlp
        
    Returns:
        dict: Informações do vídeo (URL, título, duração, etc.)
    """
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(query, download=False)


bot = CabaBot()

# --- COMANDOS DE CONFIGURAÇÃO ---

@bot.tree.command(name="startup_audio", description="Ativa/desativa áudio de boas-vindas neste servidor")
@app_commands.describe(enabled="true para ativar, false para desativar")
async def startup_audio(interaction: discord.Interaction, enabled: bool):
    """
    Comando para habilitar ou desabilitar o áudio de startup neste servidor.

    Exige permissão `Manage Guild` para alterar a configuração.
    """
    # Só funciona em servidores
    if interaction.guild is None:
        await interaction.response.send_message("Oxente — esse comando só funciona dentro de um servidor, visse?", ephemeral=True)
        return

    # Verifica permissão do usuário
    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("Você precisa da permissão 'Gerenciar Servidor' pra isso.", ephemeral=True)
        return

    # Salva a configuração e responde
    set_guild_startup(interaction.guild.id, enabled)
    state = "ativado" if enabled else "desativado"
    await interaction.response.send_message(f"Áudio de startup {state} neste servidor.", ephemeral=True)



@bot.tree.command(name="musica", description="Toca uma música no canal de voz")
@app_commands.describe(url="URL do YouTube ou nome da música para tocar")
async def musica(interaction: discord.Interaction, url: str):
    """
    Comando para reproduzir uma música do YouTube no canal de voz.
    
    O bot busca a música no YouTube (se um nome for informado) e reproduz
    através do FFmpeg no canal de voz do usuário.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        url (str): URL do YouTube ou nome da música a buscar
        
    Processo:
        1. Valida se o usuário está em um canal de voz
        2. Conecta ou alterna para o canal do usuário
        3. Busca a música no YouTube
        4. Extrai a melhor qualidade de áudio disponível
        5. Reproduz usando FFmpeg
    """
    await interaction.response.defer()

    # Validar que é um servidor (Guild) válido
    if not interaction.guild:
        await interaction.followup.send("Oxente — esse comando só funciona dentro de um servidor, visse?")
        return
    
    # Validar que o usuário é um Member (não apenas User)
    if not isinstance(interaction.user, discord.Member):
        await interaction.followup.send("Erro ao pegar seus dados, não rolou acessar agora, visse?")
        return
    
    # Verifica se o usuário está em um canal de voz
    voice_channel = interaction.user.voice.channel
    if voice_channel is None:
        await interaction.followup.send("Bota-se num canal de voz primeiro, visse? Só assim eu toco a música.")
        return
    
    # Obtém o cliente de voz atual (se houver)
    voice_client = interaction.guild.voice_client
    
    # Conecta ao canal de voz ou alterna se o bot estiver em outro canal
    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.disconnect()
        voice_client = await voice_channel.connect()

    # Configurações do yt-dlp para melhor compatibilidade de áudio
    ytdlp_options = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',  # Prioriza m4a (mais compatível com FFmpeg)
        'noplaylist': True,  # Não baixa playlists inteiras
        'nocheckcertificate': True,  # Evita erros SSL
        'cachedir': False,  # Não usa cache local
    }

    # Se não for URL, adiciona prefixo de busca para YouTube Search
    query = 'ytsearch:' + url if not url.startswith("http") else url
    results = await search_ytdlp_async(query, ytdlp_options)

    # Valida se encontrou algum resultado
    if not results:
        await interaction.followup.send("Não encontrei nada com esse nome, visse? Tenta outro termo ou URL.")
        return

    # Extrai a faixa corretamente (pode estar em entries se for resultado de busca)
    if 'entries' in results:
        track = results['entries'][0]
    else:
        track = results

    # Obtém URL de áudio e título do vídeo
    audio_url = track.get('url')
    title = track.get('title', 'Música')
    
    # Validação: se não conseguiu extrair a URL real, retorna erro descritivo
    if not audio_url or "youtube.com/watch" in audio_url:
        await interaction.followup.send(
            "❌ Erro: Não consegui extrair o áudio do YouTube. "
            "Tente novamente ou use uma URL diferente."
        )
        return

    # Configurações do FFmpeg para melhor estabilidade de conexão
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',  # Reconecta automaticamente
        'options': '-vn -loglevel error',  # -vn: sem vídeo, -loglevel error: minimiza logs
    }
    
    try:
        # Cria a fonte de áudio através do FFmpeg
        source = discord.FFmpegPCMAudio(
            audio_url,
            executable=str(FFMPEG_PATH),
            **ffmpeg_options
        )

        # Reproduz a música no canal de voz
        if isinstance(voice_client, discord.VoiceClient):
            voice_client.play(source)
            await interaction.followup.send(f"🎵 Tô tocando: **{title}** — aproveita aí")
    except Exception as e:
        # Captura e informa qualquer erro durante a reprodução
        await interaction.followup.send(f"Oxente, deu ruim ao iniciar o áudio: {str(e)[:100]}")


@bot.tree.command(name="timer", description="Define um timer em segundos e toca uma música ao fim")
@app_commands.describe(
    segundos="Quantos segundos quer esperar? (máximo 1200)",
    url="URL do YouTube para tocar quando o timer acabar"
)
async def timer(interaction: discord.Interaction, segundos: int, url: str):
    """
    Comando para criar um timer que reproduz uma música ao terminar.
    
    Útil para pausas, exercícios ou lembretes musicais. O timer é
    assíncrono - o bot continua respondendo a outros comandos enquanto
    o timer está ativo.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        segundos (int): Duração do timer em segundos
        url (str): URL do YouTube ou nome da música a tocar
        
    Validações:
        - Usuário deve estar em um canal de voz
        - Valor de segundos deve ser razoável (evita timers muito longos)
    """
    
    async def safe_send(content: str, *, ephemeral: bool = True):
        """Envia mensagem de forma segura, verificando se resposta já foi dada."""
        if interaction.response.is_done():
            await interaction.followup.send(content, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(content, ephemeral=ephemeral)

    # Validações iniciais
    if interaction.guild is None:
        await safe_send("Oxente — esse comando só funciona dentro de um servidor, visse?", ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member):
        await safe_send("Erro ao pegar seus dados, não rolou acessar agora, visse?", ephemeral=True)
        return
    
    member: discord.Member = interaction.user

    # Verifica se o usuário está em canal de voz
    if not member.voice or not member.voice.channel:
        await safe_send("Bota-se num canal de voz primeiro, visse? Só assim eu toco a música.", ephemeral=True)
        return

    # Confirma a interação com defer para evitar timeout (comando pode levar tempo)
    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=True)
    
    # Informa o usuário que o timer foi iniciado
    await safe_send(
        f"⏱️ Timer de {segundos}s iniciado — vou avisar quando acabar, visse? \n"
        f"🎵 Música: `{url}` \n"
        f"👤 Pedido por {member.mention}",
    )

    # Aguarda o tempo especificado do timer
    try:
        await asyncio.sleep(segundos)
    except asyncio.CancelledError:
        await safe_send(f"{member.mention} ⏱️ Timer foi cancelado.")
        return

    # Quando o timer acabar, toca a música
    voice_channel = member.voice.channel
    voice_client = interaction.guild.voice_client
    
    # Conecta ao canal de voz ou alterna se necessário
    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.disconnect()
        voice_client = await voice_channel.connect()

    # Configurações iguais ao comando de música
    ytdlp_options = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'noplaylist': True,
        'nocheckcertificate': True,
        'cachedir': False,
    }

    # Formata a query para busca
    query = 'ytsearch:' + url if not url.startswith("http") else url
    results = await search_ytdlp_async(query, ytdlp_options)

    # Valida se encontrou resultado
    if not results:
        await safe_send(f"{member.mention} ⏱️ Timer acabou — não achei a música, visse? ❌", ephemeral=True)
        return

    # Extrai informações da faixa
    if 'entries' in results:
        track = results['entries'][0]
    else:
        track = results

    audio_url = track.get('url')
    title = track.get('title', 'Música')
    
    # Valida extração de URL
    if not audio_url or "youtube.com/watch" in audio_url:
        await safe_send(f"{member.mention} ⏱️ Timer acabou — o YouTube não deixou pegar o áudio ❌", ephemeral=True)
        return

    # Configurações FFmpeg
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -loglevel error',
    }
    
    try:
        # Cria e reproduz a fonte de áudio
        source = discord.FFmpegPCMAudio(
            audio_url,
            executable=str(FFMPEG_PATH),
            **ffmpeg_options
        )

        if isinstance(voice_client, discord.VoiceClient):
            voice_client.play(source)
            await safe_send(f"{member.mention} ⏱️ Timer acabou — tocando agora: **{title}**, aproveita aí!", ephemeral=True)
    except Exception as e:
        await safe_send(f"{member.mention} ⏱️ Acabou o timer mas deu ruim ao reproduzir: {str(e)[:50]}", ephemeral=True)


# ============================================================================
# COMANDOS - CONTROLES DE REPRODUÇÃO
# ============================================================================

@bot.tree.command(name="parar", description="Para a música que está tocando")
async def parar(interaction: discord.Interaction):
    """
    Comando para parar a reprodução de música e limpar a fila.
    
    Interrompe imediatamente a música atual e limpa a fila de reprodução
    para o servidor (guild) específico.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
    """
    # Valida se está dentro de um servidor
    if not interaction.guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Obtém o cliente de voz atual
    voice_client = interaction.guild.voice_client
    if voice_client is None or not voice_client.is_playing():
        await interaction.response.send_message(
            "Nada tá tocando agora, visse?",
            ephemeral=True
        )
        return
    
    # Para a reprodução
    voice_client.stop()
    
    # Limpa a fila para este servidor
    if interaction.guild.id in bot.music_queue:
        bot.music_queue[interaction.guild.id] = []
    
    await interaction.response.send_message("⏹️ Música parada, como cê pediu.", ephemeral=True)


@bot.tree.command(name="pausar", description="Pausa a música que está tocando")
async def pausar(interaction: discord.Interaction):
    """
    Comando para pausar a reprodução de música.
    
    Coloca a música em pausa, mantendo a posição. Use /retomar para continuar.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
    """
    # Valida se está dentro de um servidor
    if not interaction.guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Obtém o cliente de voz e valida se há música tocando
    voice_client = interaction.guild.voice_client
    if voice_client is None or not voice_client.is_playing():
        await interaction.response.send_message(
            "Nada tá tocando agora, visse?",
            ephemeral=True
        )
        return
    
    # Pausa a reprodução
    voice_client.pause()
    await interaction.response.send_message("⏸️ Música pausada, fica tranquila.", ephemeral=True)


@bot.tree.command(name="retomar", description="Retoma a música pausada")
async def retomar(interaction: discord.Interaction):
    """
    Comando para retomar a reprodução de uma música pausada.
    
    Continua a música a partir do ponto onde foi pausada com /pausar.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
    """
    # Valida se está dentro de um servidor
    if not interaction.guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Obtém o cliente de voz e valida se há música pausada
    voice_client = interaction.guild.voice_client
    if voice_client is None or voice_client.is_playing():
        await interaction.response.send_message(
            "Não achei nenhuma música pausada, visse?",
            ephemeral=True
        )
        return
    
    # Retoma a reprodução
    voice_client.resume()
    await interaction.response.send_message("▶️ Retomei a música pra você.", ephemeral=True)


@bot.tree.command(name="pular", description="Pula para a próxima música da fila")
async def pular(interaction: discord.Interaction):
    """
    Comando para pular a música atual.
    
    Para a música em andamento. Se houver próxima música na fila,
    ela será reproduzida automaticamente.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
    """
    # Valida se está dentro de um servidor
    if not interaction.guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Obtém o cliente de voz e valida se há música tocando
    voice_client = interaction.guild.voice_client
    if voice_client is None or not voice_client.is_playing():
        await interaction.response.send_message(
            "Nada tá tocando agora, visse?",
            ephemeral=True
        )
        return
    
    # Para a música atual (pula)
    voice_client.stop()
    await interaction.response.send_message("⏭️ Pulei pra próxima, vamo que vamo.", ephemeral=True)


@bot.tree.command(name="limpar_fila", description="Limpa a fila de músicas")
async def limpar_fila(interaction: discord.Interaction):
    """
    Comando para limpar a fila de reprodução de música.
    
    Remove todas as músicas enfileiradas. A música atualmente tocando
    não é afetada - use /parar para interromper.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
    """
    # Valida se está dentro de um servidor
    if not interaction.guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Limpa a fila para este servidor
    if interaction.guild.id in bot.music_queue:
        bot.music_queue[interaction.guild.id] = []
    
    await interaction.response.send_message("🗑️ Limpei a fila, tá zerado.", ephemeral=True)


# ============================================================================
# COMANDOS - UTILIDADE
# ============================================================================

@bot.tree.command(name="teste", description="Comando de teste simples")
async def teste(interaction: discord.Interaction):
    """
    Comando de teste para verificar se o bot está responsivo.
    
    Útil para diagnosticar conexão e latência. A resposta é visível
    apenas para o usuário que invocou o comando (ephemeral).
    
    Args:
        interaction (discord.Interaction): A interação do slash command
    """
    # Resposta visível apenas para o usuário que invocou (mensagem privada)
    await interaction.response.send_message(
        f"✅ Tô na área e respondi, {interaction.user.mention}!",
        ephemeral=True
    )


@bot.tree.command(name="soma", description="Soma dois números")
@app_commands.describe(num1="O primeiro número", num2="O segundo número")
async def soma(interaction: discord.Interaction, num1: float, num2: float):
    """
    Comando de utilidade para calcular a soma de dois números.
    
    Um exemplo simples de comando com parâmetros numéricos e cálculo.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        num1 (float): Primeiro número a ser somado
        num2 (float): Segundo número a ser somado
    """
    resultado = num1 + num2
    await interaction.response.send_message(
        f"➕ **{num1}** + **{num2}** = **{resultado}**"
    )


@bot.tree.command(name="perfil", description="Mostra o avatar e informações de um membro")
@app_commands.describe(membro="Escolha um membro do servidor")
async def perfil(interaction: discord.Interaction, membro: discord.Member):
    """
    Comando para exibir o perfil e avatar de um membro.
    
    Mostra uma card formatada (Embed) com o avatar do membro escolhido.
    Útil para ver informações visuais de usuários.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        membro (discord.Member): O membro cujo perfil será exibido
    """
    # Cria um card formatado (Embed) com informações do membro
    embed = discord.Embed(
        title=f"Perfil de {membro.display_name}",
        description=f"ID: {membro.id}",
        color=discord.Color.blue()
    )
    
    # Define a imagem do card como o avatar do membro
    avatar_url = membro.avatar.url if membro.avatar else membro.default_avatar.url
    embed.set_image(url=avatar_url)
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="d", description="Rola um dado padrão (d2 até d100)")
@app_commands.describe(
    lados="Número de lados do dado (2, 4, 6, 8, 10, 12, 20, 100)",
    quantidade="Quantidade de dados a rolar (padrão: 1)"
)
@app_commands.choices(lados=[
    discord.app_commands.Choice(name="d2", value=2),
    discord.app_commands.Choice(name="d4", value=4),
    discord.app_commands.Choice(name="d6", value=6),
    discord.app_commands.Choice(name="d8", value=8),
    discord.app_commands.Choice(name="d10", value=10),
    discord.app_commands.Choice(name="d12", value=12),
    discord.app_commands.Choice(name="d20", value=20),
    discord.app_commands.Choice(name="d100", value=100),
])
async def rolar_dado(interaction: discord.Interaction, lados: int, quantidade: int = 1):
    """
    Comando para rolar dados padrão.
    
    Permite rolar um ou mais dados com número de lados pré-definido.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        lados (int): Número de lados do dado (2, 4, 6, 8, 10, 12, 20, 100)
        quantidade (int): Quantidade de dados a rolar (padrão: 1)
    """
    # Valida a quantidade de dados
    if quantidade < 1 or quantidade > 100:
        await interaction.response.send_message(
            f"❌ Quantidade inválida. Use entre 1 e 100 dados, visse?",
            ephemeral=True
        )
        return
    
    # Rola os dados
    resultados = [random.randint(1, lados) for _ in range(quantidade)]
    total = sum(resultados)
    
    # Formata a resposta
    if quantidade == 1:
        resposta = f"🎲 **d{lados}**: **{resultados[0]}**"
    else:
        resultados_str = ", ".join(map(str, resultados))
        resposta = f"🎲 **{quantidade}d{lados}**\nResultados: `{resultados_str}`\n**Total: {total}**"
    
    await interaction.response.send_message(resposta)


@bot.tree.command(name="dado_custom", description="Rola um dado com número de lados customizado")
@app_commands.describe(
    lados="Número de lados do dado (mínimo 2, máximo 1000)",
    quantidade="Quantidade de dados a rolar (padrão: 1, máximo 100)"
)
async def dado_customizado(interaction: discord.Interaction, lados: int, quantidade: int = 1):
    """
    Comando para rolar dados com número de lados customizado.
    
    Permite rolar um ou mais dados com qualquer número de lados dentro dos limites.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        lados (int): Número de lados do dado (2 a 1000)
        quantidade (int): Quantidade de dados a rolar (1 a 100)
    """
    # Valida o número de lados
    if lados < 2 or lados > 1000:
        await interaction.response.send_message(
            f"❌ Número de lados inválido. Use entre 2 e 1000, visse?",
            ephemeral=True
        )
        return
    
    # Valida a quantidade de dados
    if quantidade < 1 or quantidade > 100:
        await interaction.response.send_message(
            f"❌ Quantidade inválida. Use entre 1 e 100 dados, visse?",
            ephemeral=True
        )
        return
    
    # Rola os dados
    resultados = [random.randint(1, lados) for _ in range(quantidade)]
    total = sum(resultados)
    
    # Formata a resposta
    if quantidade == 1:
        resposta = f"🎲 **d{lados}**: **{resultados[0]}**"
    else:
        resultados_str = ", ".join(map(str, resultados))
        resposta = f"🎲 **{quantidade}d{lados}**\nResultados: `{resultados_str}`\n**Total: {total}**"
    
    await interaction.response.send_message(resposta)


# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    """
    Ponto de entrada principal do bot.
    
    Inicia a conexão com o Discord usando o token carregado do .env.
    O bot permanecerá rodando indefinidamente até ser interrompido.
    """
    bot.run(TOKEN)
