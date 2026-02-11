"""
CabaBot - Discord Music Bot

Um bot multifuncional para Discord com foco em reprodução de áudio,
gerenciamento de timers e interações com usuários através de slash commands.

Funcionalidades principais:
- Reprodução de música do YouTube com qualidade adaptativa
- Sistema de timers com toque de áudio ao final
- Controles de reprodução (pausar, retomar, pular, parar)
- Gerenciamento de filas de música por servidor
- Comandos de utilidade (calculadora, perfil de usuário, teste de conexão)

Author: CabaBot Team
Version: 1.2.1
"""

import discord  # type: ignore[import-untyped, import-not-found]
import asyncio
import os
import yt_dlp  # type: ignore[import-untyped, import-not-found]
import spotipy  # type: ignore[import-untyped, import-not-found]
from spotipy.oauth2 import SpotifyClientCredentials  # type: ignore[import-untyped, import-not-found]
from discord import app_commands  # type: ignore[import-untyped, import-not-found]
from dotenv import load_dotenv, find_dotenv  # type: ignore[import-untyped, import-not-found]
from pathlib import Path
from typing import Dict, Any, List, Optional
from dashboard.server import WebServer # Importa o servidor web

# Carrega as variáveis de ambiente do arquivo .env
# find_dotenv() procura automaticamente na árvore de diretórios
load_dotenv(find_dotenv())

# Define o caminho base do script e a localização do ffmpeg local
SCRIPT_DIR = Path(__file__).parent
LOCAL_FFMPEG_WIN = SCRIPT_DIR / "bin" / "ffmpeg" / "ffmpeg.exe"
LOCAL_FFMPEG_NIX = SCRIPT_DIR / "bin" / "ffmpeg" / "ffmpeg"

# Lógica de seleção do FFmpeg:
# 1. Tenta usar o executável local (Windows)
# 2. Tenta usar o executável local (Linux/Mac)
# 3. Se não existir, assume que está no PATH do sistema
if LOCAL_FFMPEG_WIN.exists():
    FFMPEG_PATH = str(LOCAL_FFMPEG_WIN)
    print(f"✅ Usando FFmpeg local (Windows): {FFMPEG_PATH}")
elif LOCAL_FFMPEG_NIX.exists():
    FFMPEG_PATH = str(LOCAL_FFMPEG_NIX)
    print(f"✅ Usando FFmpeg local (Linux/Mac): {FFMPEG_PATH}")
else:
    FFMPEG_PATH = "ffmpeg"
    print("✅ Usando FFmpeg do sistema (PATH)")

# Configuração do Spotify
spotify_client = None
try:
    if os.getenv("SPOTIPY_CLIENT_ID") and os.getenv("SPOTIPY_CLIENT_SECRET"):
        spotify_client = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
            )
        )
        print("✅ Cliente Spotify configurado com sucesso")
    else:
        print("⚠️ Credenciais do Spotify não encontradas. Funcionalidade limitada.")
except Exception as e:
    print(f"⚠️ Erro ao configurar Spotify: {e}")

# Configurações reutilizáveis para yt-dlp (evita duplicação de código)
# 'client': 'android' ajuda a evitar erros 403 Forbidden do YouTube
YTDLP_OPTIONS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'cachedir': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # Bind to ipv4 since ipv6 addresses cause issues sometimes
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
}

# Configurações reutilizáveis para FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    # -af "loudnorm...": Normaliza o áudio para -14 LUFS (padrão confortável)
    # -loglevel error: Reduz o lixo no terminal
    'options': '-vn -loglevel error -af "loudnorm=I=-14:TP=-1.5:LRA=11"',
}

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
        # Controle de loop por guild: {'guild_id': {'loop_track': bool, 'loop_queue': bool}}
        self.loop_control = {}
        # Música atual tocando por guild: {'guild_id': MusicTrack}
        self.current_track = {}
        # Sessões de votação por guild
        self.vote_sessions = {}
        # Armazena a última mensagem de "Tocando Agora" por guild para evitar spam
        self.last_player_message = {}
        # Histórico de músicas tocadas por guild: {'guild_id': [MusicTrack, ...]}
        self.music_history = {}

    async def setup_hook(self):
        """
        Hook chamado antes do bot começar.
        
        Sincroniza todos os slash commands registrados com a API do Discord.
        Isso garante que os comandos apareçam no menu de slash commands.
        """
        await self.tree.sync()
        print("✅ Comandos sincronizados com sucesso!")
        
        # Inicia o Dashboard Web
        self.web_server = WebServer(self)
        # Roda em background sem bloquear
        self.loop.create_task(self.web_server.start())

    async def on_ready(self):
        """
        Event handler chamado quando o bot se conecta ao Discord com sucesso.
        
        Exibe informações de conexão e status do bot.
        """
        print(f'🤖 {self.user} tá on — pronto pra tocar umas arretadas!')


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
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
        return ydl.extract_info(query, download=False)  # type: ignore[return-value]


def _get_stream_url(track: dict) -> Optional[str]:
    """
    Retorna a URL direta do stream de áudio a partir do dicionário retornado pelo yt-dlp.
    Prioriza `track['url']` quando for um stream direto, caso contrário tenta
    escolher uma URL de `formats` apropriada.
    """
    if not isinstance(track, dict):
        return None

    url = track.get('url')
    # Se já for uma URL direta válida (e não apenas a página do YouTube), retorna
    if isinstance(url, str) and url.startswith('http') and 'youtube.com/watch' not in url:
        return url

    # Tenta escolher uma URL dos formats (prefere formatos com áudio)
    formats = track.get('formats') or []
    if formats and isinstance(formats, list):
        # percorre do fim (melhor qualidade normalmente no final)
        for f in reversed(formats):
            fu = f.get('url')
            if fu and isinstance(fu, str):
                acodec = f.get('acodec')
                # ignora entradas sem codec de áudio
                if acodec and acodec != 'none':
                    return fu

    return None


async def fetch_tracks(query: str, allow_playlist: bool = False) -> List[dict]:
    """Retorna uma lista de track dicts a partir de uma query (pode ser playlist)."""
    opts = dict(YTDLP_OPTIONS)
    # permitir playlist apenas quando explicitado
    opts['noplaylist'] = not allow_playlist
    # Se for playlist, adiciona 'playlistend' para parar de baixar após 20 músicas
    if allow_playlist:
        opts['playlistend'] = 20
    results = await search_ytdlp_async(query, opts)
    if not results:
        return []
    if 'entries' in results and isinstance(results['entries'], list):
        return results['entries']
    return [results]


async def _validate_guild_and_member(interaction: discord.Interaction) -> discord.Member | None:
    """
    Valida se a interação ocorreu em um servidor e se o usuário é um membro válido.
    Envia mensagens de erro automáticas se a validação falhar.
    
    Args:
        interaction (discord.Interaction): A interação a validar
        
    Returns:
        discord.Member | None: O membro se válido, None caso contrário
    """
    if interaction.guild is None:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return None
    
    if not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message(
            "Erro ao pegar seus dados, não rolou acessar agora, visse?",
            ephemeral=True
        )
        return None
    
    return interaction.user


async def _get_or_connect_voice_client(
    guild: discord.Guild, 
    voice_channel: discord.VoiceChannel | discord.StageChannel
) -> discord.VoiceClient | discord.VoiceProtocol | None:
    """
    Obtém o cliente de voz atual ou conecta a um novo canal.
    
    Args:
        guild (discord.Guild): O servidor
        voice_channel (discord.VoiceChannel | discord.StageChannel): O canal de voz destino
        
    Returns:
        discord.VoiceClient | discord.VoiceProtocol | None: Cliente de voz conectado ou None se erro
    """
    voice_client = guild.voice_client
    
    try:
        print(f"DEBUG: _get_or_connect_voice_client guild={getattr(guild,'name',guild.id)} channel={getattr(voice_channel,'name',None)} current_vc={voice_client}")
        if voice_client is None:
            print("DEBUG: connecting to voice channel...")
            return await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            print(f"DEBUG: moving voice client from {voice_client.channel} to {voice_channel}")
            await voice_client.disconnect(force=True)
            return await voice_channel.connect()
        else:
            print("DEBUG: already connected to requested channel")
        return voice_client
    except Exception as e:
        print(f"Erro ao conectar ao canal de voz: {e}")
        return None





class MusicTrack:
    """Representa uma faixa de música na fila."""

    def __init__(self, url: str, title: str, requester, channel_id: int, requester_name: Optional[str] = None):
        """
        Inicializa uma faixa de música.

        Args:
            url (str): URL do áudio
            title (str): Título da música
            requester (int|str): ID do usuário que requisitou ou nome
            channel_id (int): ID do canal de texto onde a música foi pedida (para enviar o player)
            requester_name (str | None): Nome do usuário (se requester for id)
        """
        self.url = url
        self.title = title
        self.channel_id = channel_id
        if isinstance(requester, int):
            self.requester_id: int | None = requester
            self.requester = requester_name or str(requester)
        else:
            self.requester_id = None
            self.requester = str(requester)


class MusicPlayerView(discord.ui.View):
    """View que contém os controles de reprodução de música (Botões)."""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=None) # Botões não expiram
        self.guild_id = guild_id

    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.secondary, custom_id="player_pause_resume")
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Pausa ou retoma a música."""
        if interaction.guild is None:
            return

        vc = interaction.guild.voice_client
        
        # Verifica tipagem explicitamente para o Pylance
        if not isinstance(vc, discord.VoiceClient):
            await interaction.response.send_message("Não estou conectado ou reproduzindo.", ephemeral=True)
            return

        if vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Pausado!", ephemeral=True)
        elif vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Retomado!", ephemeral=True)
        else:
            await interaction.response.send_message("Nada tocando no momento.", ephemeral=True)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, custom_id="player_skip")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Pula para a próxima música."""
        if interaction.guild is None:
            return

        vc = interaction.guild.voice_client
        # Garante que é um VoiceClient válido e está conectado
        if not isinstance(vc, discord.VoiceClient) or (not vc.is_playing() and not vc.is_paused()):
            await interaction.response.send_message("Nada tocando para pular.", ephemeral=True)
            return
        
        await interaction.response.send_message("⏭️ Pulando...", ephemeral=True)
        vc.stop() # Isso dispara o callback 'after' que toca a próxima

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, custom_id="player_stop")
    async def stop_music(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Para a música e limpa a fila."""
        if interaction.guild is None:
            return

        vc = interaction.guild.voice_client
        if not isinstance(vc, discord.VoiceClient):
            await interaction.response.send_message("Não estou tocando nada.", ephemeral=True)
            return

        # Limpa a fila
        if self.guild_id in bot.music_queue:
            bot.music_queue[self.guild_id] = []
        
        # Reseta loops
        if self.guild_id in bot.loop_control:
            bot.loop_control[self.guild_id] = {'loop_track': False, 'loop_queue': False}

        vc.stop()
        await interaction.response.send_message("⏹️ Parado e fila limpa!", ephemeral=True)

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.success, label="Loop", custom_id="player_loop")
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Alterna o modo de loop da música atual."""
        if self.guild_id not in bot.loop_control:
            bot.loop_control[self.guild_id] = {'loop_track': False, 'loop_queue': False}
        
        # Alterna loop da faixa
        current = bot.loop_control[self.guild_id]['loop_track']
        bot.loop_control[self.guild_id]['loop_track'] = not current
        
        state = "ativado" if not current else "desativado"
        # Atualiza a cor do botão visualmente (feedback)
        button.style = discord.ButtonStyle.primary if not current else discord.ButtonStyle.success
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"🔁 Loop da música {state}.", ephemeral=True)


async def _play_next_track(guild: discord.Guild) -> None:
    """
    Reproduz a próxima música da fila e envia o player interativo.
    
    Args:
        guild (discord.Guild): O servidor
    """
    voice_client = guild.voice_client
    if voice_client is None or not isinstance(voice_client, discord.VoiceClient):  # type: ignore[union-attr]
        return
    
    # Verifica se há loop de música individual
    loop_track = bot.loop_control.get(guild.id, {}).get('loop_track', False)
    loop_queue = bot.loop_control.get(guild.id, {}).get('loop_queue', False)
    
    # Se está em loop de música, reproduz a mesma música
    if loop_track and guild.id in bot.current_track:
        track = bot.current_track[guild.id]
    else:
        # Salva a música anterior no histórico antes de mudar
        if guild.id in bot.current_track:
            if guild.id not in bot.music_history:
                bot.music_history[guild.id] = []
            bot.music_history[guild.id].append(bot.current_track[guild.id])
            # Limita histórico a 20 músicas para economizar memória
            if len(bot.music_history[guild.id]) > 20:
                bot.music_history[guild.id].pop(0)

        # Se não há fila ou está vazia, retorna
        if guild.id not in bot.music_queue or not bot.music_queue[guild.id]:
            # Limpa track atual pois acabou a música
            if guild.id in bot.current_track:
                del bot.current_track[guild.id]
            return
        
        # Pega a próxima faixa
        track = bot.music_queue[guild.id].pop(0)
        
        # Se está em loop de fila, re-adiciona a faixa no final
        if loop_queue:
            bot.music_queue[guild.id].append(track)
        
        # Armazena a música atual
        bot.current_track[guild.id] = track
    
    try:
        source = discord.FFmpegPCMAudio(
            track.url,
            executable=str(FFMPEG_PATH),
            before_options=FFMPEG_OPTIONS['before_options'],
            options=FFMPEG_OPTIONS['options']
        )
        print(f"DEBUG _play_next_track: playing title={track.title} url_len={len(track.url) if track.url else 0} vc={voice_client} channel={getattr(voice_client.channel,'name',None)}")
        
        # Define callback para quando a música termina
        def after_track(error):
            if error:
                print(f"Erro ao reproduzir: {error}")
            # Reproduz a próxima faixa
            asyncio.run_coroutine_threadsafe(_play_next_track(guild), bot.loop)
        
        voice_client.play(source, after=after_track)  # type: ignore[attr-defined]
        
        # --- ENVIA O PLAYER COM BOTÕES ---
        try:
            channel = bot.get_channel(track.channel_id)
            if isinstance(channel, (discord.TextChannel, discord.Thread)):
                # Tenta apagar a mensagem anterior se existir (Limpeza de chat)
                last_msg = bot.last_player_message.get(guild.id)
                if last_msg:
                    try:
                        await last_msg.delete()
                    except Exception:
                        pass # Mensagem pode ter sido deletada manualmente ou bot sem permissão
                
                embed = discord.Embed(
                    title="🎵 Tocando Agora",
                    description=f"**{track.title}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="Pedido por", value=track.requester, inline=True)
                embed.set_thumbnail(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmZpbXJ6YnI1b3g4b3g4b3g4b3g4b3g4b3g4b3g4b3g4/S99mGj4FhZ9tq/giphy.gif") # Gif de musica opcional
                
                view = MusicPlayerView(guild.id)
                msg = await channel.send(embed=embed, view=view)
                bot.last_player_message[guild.id] = msg
        except Exception as e:
            print(f"Erro ao enviar player UI: {e}")

        print(f"🎵 Tocando: {track.title} (requisitado por {track.requester})")
    except Exception as e:
        print(f"Erro ao reproduzir faixa: {e}")


async def _play_previous_track(guild: discord.Guild) -> bool:
    """
    Tenta voltar para a música anterior.
    Retorna True se sucesso, False se não houver histórico.
    """
    if guild.id not in bot.music_history or not bot.music_history[guild.id]:
        return False

    # Pega a última música do histórico
    previous_track = bot.music_history[guild.id].pop()
    
    # Coloca ela no início da fila
    if guild.id not in bot.music_queue:
        bot.music_queue[guild.id] = []
    bot.music_queue[guild.id].insert(0, previous_track)
    
    # Se tinha uma música tocando, ela vai pro histórico "naturalmente" pelo _play_next_track
    # Mas queremos evitar que a música que estava tocando (que foi interrompida pra voltar)
    # se duplique ou bagunce o fluxo. 
    # O fluxo normal do .stop() chama _play_next_track -> salva current -> toca next (que é a previous).
    # Isso faria a música interrompida ir pro histórico, o que é CORRETO (botão voltar = "essa não, volta a anterior").
    
    # Para a música atual para disparar o próximo
    voice_client = guild.voice_client
    if isinstance(voice_client, discord.VoiceClient):
        voice_client.stop()
        
    return True

bot = CabaBot()
# Anexa funções auxiliares ao bot para acesso no dashboard
#bot.add_track_to_guild = add_track_to_guild # type: ignore
bot.play_previous_track = _play_previous_track # type: ignore

async def add_track_to_guild(guild: discord.Guild, query: str, requester_id: int, requester_name: str, channel_id: int) -> str:
    """
    Adiciona uma música à fila de um servidor (usado pelo Dashboard e Slash Commands).
    Retorna uma mensagem de status.
    """
    # Lógica de Busca
    url = query
    allow_playlist = False
    spotify_client_loc = spotify_client # Acessa variável global

    # 1. Tratamento Spotify
    if "open.spotify.com" in url:
        if not spotify_client_loc:
            return "⚠️ Suporte a Spotify não configurado."
        
        spotify_query = _get_spotify_track_info(url)
        if spotify_query:
            query = f'ytsearch:{spotify_query}'
        else:
            return "❌ Não consegui ler esse link do Spotify."

    # 2. Tratamento YouTube
    elif not url.startswith("http"):
        query = 'ytsearch:' + url
    elif "list=" in url or "playlist" in url:
        allow_playlist = True

    # Busca tracks
    tracks = await fetch_tracks(query, allow_playlist=allow_playlist)
    if not tracks:
        return "❌ Não encontrei nada com esse nome."

    voice_client = guild.voice_client
    if not isinstance(voice_client, discord.VoiceClient):
        return "❌ Bot não conectado a um canal de voz."

    # Se for playlist
    if len(tracks) > 1:
        if guild.id not in bot.music_queue:
            bot.music_queue[guild.id] = []
        
        for entry in tracks:
            audio_url_e = _get_stream_url(entry)
            if not audio_url_e or "youtube.com/watch" in audio_url_e:
                continue
            title_e = entry.get('title', 'Música')
            mt = MusicTrack(audio_url_e, title_e, requester_id, channel_id, requester_name)
            bot.music_queue[guild.id].append(mt)
        
        # Se não está tocando, inicia
        if not voice_client.is_playing():
            await _play_next_track(guild)
            
        return f"✅ Playlist com {len(tracks)} músicas adicionada."

    # Faixa única
    track_info = tracks[0]
    audio_url = _get_stream_url(track_info)
    title = track_info.get('title', 'Música')
    
    if not audio_url or "youtube.com/watch" in audio_url:
        return "❌ Erro ao extrair áudio."

    track = MusicTrack(audio_url, title, requester_id, channel_id, requester_name)
    
    if guild.id not in bot.music_queue:
        bot.music_queue[guild.id] = []
        
    if not voice_client.is_playing():
        bot.current_track[guild.id] = track
        # Setup loop control se necessário
        if guild.id not in bot.loop_control:
            bot.loop_control[guild.id] = {'loop_track': False, 'loop_queue': False}
            
        # Toca
        try:
             # Cria a fonte de áudio através do FFmpeg
            source = discord.FFmpegPCMAudio(
                audio_url,
                executable=str(FFMPEG_PATH),
                before_options=FFMPEG_OPTIONS['before_options'],
                options=FFMPEG_OPTIONS['options']
            )
            
            def after_track(error):
                if error:
                    print(f"Erro: {error}")
                asyncio.run_coroutine_threadsafe(_play_next_track(guild), bot.loop)
                
            voice_client.play(source, after=after_track)
            
            # Envia player (copiando lógica do play_next)
            # Como é primeira musica, fazemos manualmente ou chamamos play_next?
            # A lógica original do comando /musica fazia manualmente.
            # Vamos simplificar: se play_next_track for robusto, poderiamos usar ele.
            # Mas ele assume que tira da fila. Aqui já setamos current_track.
            
            # Envia UI
            try:
                channel = bot.get_channel(channel_id)
                if isinstance(channel, (discord.TextChannel, discord.Thread)):
                    embed = discord.Embed(title="🎵 Tocando Agora", description=f"**{title}**", color=discord.Color.green())
                    embed.add_field(name="Pedido por", value=requester_name, inline=True)
                    view = MusicPlayerView(guild.id)
                    msg = await channel.send(embed=embed, view=view)
                    bot.last_player_message[guild.id] = msg
            except Exception:
                pass
            
            return f"▶️ Tocando agora: {title}"
        except Exception as e:
            return f"❌ Erro ao tocar: {e}"
    else:
        bot.music_queue[guild.id].append(track)
        return f"✅ Adicionado à fila: {title}"

# --- COMANDOS - CONTROLES DE REPRODUÇÃO ---

def _get_spotify_track_info(url: str) -> Optional[str]:
    """
    Tenta extrair informações (Artista - Título) de uma URL do Spotify.
    
    Args:
        url (str): URL da faixa no Spotify
    
    Returns:
        Optional[str]: 'Artista - Título' ou None se falhar
    """
    if not spotify_client:
        return None

    try:
        # Suporta apenas faixas individuais por enquanto
        if "track" in url:
            track = spotify_client.track(url)
            if track and 'artists' in track and track['artists']:
                artist = track['artists'][0]['name']
                name = track['name']
                return f"{artist} - {name}"
    except Exception as e:
        print(f"Erro ao buscar no Spotify: {e}")
        return None
    return None

@bot.tree.command(name="musica", description="Toca uma música do YouTube ou Spotify")
@app_commands.describe(url="URL (YouTube/Spotify) ou nome da música")
async def musica(interaction: discord.Interaction, url: str):
    """
    Comando para reproduzir uma música.
    
    Suporta:
    - Busca por nome (YouTube)
    - URL do YouTube (Vídeo ou Playlist)
    - URL do Spotify (Faixa única -> busca automática no YouTube)
    """
    await interaction.response.defer()

    # Validações básicas de guild e membro
    member = await _validate_guild_and_member(interaction)
    if member is None or interaction.guild is None:
        return
    
    # Verifica se o usuário está em um canal de voz
    if member.voice is None or member.voice.channel is None:
        await interaction.followup.send("Bota-se num canal de voz primeiro, visse? Só assim eu toco a música.")
        return
    
    voice_channel = member.voice.channel
    if voice_channel is None:
        await interaction.followup.send("Bota-se num canal de voz primeiro, visse? Só assim eu toco a música.")
        return
    
    # Conecta ao canal de voz
    voice_client = await _get_or_connect_voice_client(interaction.guild, voice_channel)
    if voice_client is None:
        await interaction.followup.send("Erro ao conectar ao canal de voz, tenta de novo aí.")
        return

    # Lógica de Busca
    query = url
    allow_playlist = False

    # 1. Tratamento Spotify
    if "open.spotify.com" in url:
        if not spotify_client:
            await interaction.followup.send("⚠️ Suporte a Spotify não configurado neste bot (falta credenciais). Tente usar link do YouTube.")
            return
        
        spotify_query = _get_spotify_track_info(url)
        if spotify_query:
            query = f'ytsearch:{spotify_query}'
            await interaction.followup.send(f"🔎 Link Spotify detectado: Buscando **'{spotify_query}'** no YouTube...")
        else:
            await interaction.followup.send("❌ Não consegui ler esse link do Spotify. Tente outro.")
            return

    # 2. Tratamento YouTube (URL ou Busca)
    elif not url.startswith("http"):
        query = 'ytsearch:' + url
    elif "list=" in url or "playlist" in url:
        allow_playlist = True

    # Busca tracks (pode retornar múltiplas entradas se for playlist)
    tracks = await fetch_tracks(query, allow_playlist=allow_playlist)
    if not tracks:
        await interaction.followup.send("Não encontrei nada com esse nome, visse? Tenta outro termo ou URL.")
        return

    # Se for múltiplas faixas (playlist/mix), adiciona todas à fila
    if len(tracks) > 1:
        added = 0
        # Inicializa a fila se necessário
        if interaction.guild.id not in bot.music_queue:
            bot.music_queue[interaction.guild.id] = []

        for entry in tracks:
            audio_url_e = _get_stream_url(entry)
            if not audio_url_e or "youtube.com/watch" in audio_url_e:
                continue
            title_e = entry.get('title', 'Música')
            # Garante que channel_id seja int (fallback para 0 se None)
            cid = interaction.channel_id if interaction.channel_id else 0
            mt = MusicTrack(audio_url_e, title_e, interaction.user.id, cid, interaction.user.display_name)
            bot.music_queue[interaction.guild.id].append(mt)
            added += 1

        # Se nada estava tocando, toca a primeira da fila
        voice_client = await _get_or_connect_voice_client(interaction.guild, voice_channel)
        if voice_client is None:
            await interaction.followup.send("Erro ao conectar ao canal de voz, tenta de novo aí.")
            return

        if isinstance(voice_client, discord.VoiceClient) and not voice_client.is_playing() and bot.music_queue[interaction.guild.id]:
            # Inicia o ciclo de reprodução (que vai enviar o UI)
            await _play_next_track(interaction.guild)
        
        await interaction.followup.send(f"📚 Playlist/mix adicionada à fila — {added} música(s) adicionadas.")
        return

    # Caso única faixa
    track = tracks[0]
    audio_url = _get_stream_url(track)
    title = track.get('title', 'Música')

    # Validação: se não conseguiu extrair a URL real, retorna erro descritivo
    if not audio_url or "youtube.com/watch" in audio_url:
        await interaction.followup.send(
            "❌ Erro: Não consegui extrair o áudio do YouTube. "
            "Tente novamente ou use uma URL diferente."
        )
        return

    try:
        # Cria a fonte de áudio através do FFmpeg
        source = discord.FFmpegPCMAudio(
            audio_url,
            executable=str(FFMPEG_PATH),
            before_options=FFMPEG_OPTIONS['before_options'],
            options=FFMPEG_OPTIONS['options']
        )

        # Cria a faixa de música
        # IMPORTANTE: Passamos o channel_id para saber onde enviar o player depois
        # Garante channel_id válido
        cid = interaction.channel_id if interaction.channel_id else 0
        track = MusicTrack(audio_url, title, interaction.user.id, cid, interaction.user.display_name)  # type: ignore[assignment]
        
        # Inicializa a fila para este servidor se não existir
        if interaction.guild.id not in bot.music_queue:
            bot.music_queue[interaction.guild.id] = []
        
        # Se não há música tocando, toca direto e configura callback para próxima
        if isinstance(voice_client, discord.VoiceClient) and not voice_client.is_playing():
            guild = interaction.guild
            def after_track(error):
                if error:
                    print(f"Erro ao reproduzir: {error}")
                asyncio.run_coroutine_threadsafe(_play_next_track(guild), bot.loop)
            
            # Armazena a música atual
            bot.current_track[interaction.guild.id] = track
            # Inicializa controle de loop se não existir
            if interaction.guild.id not in bot.loop_control:
                bot.loop_control[interaction.guild.id] = {'loop_track': False, 'loop_queue': False}
            
            print(f"DEBUG musica: about to play title={title} url_len={len(audio_url) if audio_url else 0} vc={voice_client} channel={getattr(voice_client.channel,'name',None)}")
            voice_client.play(source, after=after_track)
            
            # --- ENVIA O PLAYER COM BOTÕES (Primeira música) ---
            embed = discord.Embed(
                title="🎵 Tocando Agora",
                description=f"**{title}**",
                color=discord.Color.green()
            )
            embed.add_field(name="Pedido por", value=interaction.user.display_name, inline=True)
            view = MusicPlayerView(interaction.guild.id)
            await interaction.followup.send(embed=embed, view=view)
            
        else:
            # Se há música tocando, adiciona à fila
            bot.music_queue[interaction.guild.id].append(track)
            queue_pos = len(bot.music_queue[interaction.guild.id])
            await interaction.followup.send(
                f"📋 **{title}** foi adicionada à fila na posição **#{queue_pos}**"
            )
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
        await interaction.response.defer()
    
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
    voice_client = await _get_or_connect_voice_client(interaction.guild, voice_channel)
    
    if voice_client is None:
        await safe_send(f"{member.mention} ⏱️ Timer acabou — erro ao conectar ao canal ❌", ephemeral=True)
        return

    # Formata a query para busca
    query = 'ytsearch:' + url if not url.startswith("http") else url
    results = await search_ytdlp_async(query, YTDLP_OPTIONS)

    # Valida se encontrou resultado
    if not results:
        await safe_send(f"{member.mention} ⏱️ Timer acabou — não achei a música, visse? ❌", ephemeral=True)
        return

    # Extrai informações da faixa
    if 'entries' in results:
        track = results['entries'][0]
    else:
        track = results

    try:
        print(f"DEBUG timer track keys: {list(track.keys())}")
    except Exception:
        print("DEBUG timer: track is not a mapping")
    audio_url = _get_stream_url(track)
    title = track.get('title', 'Música')
    
    # Valida extração de URL
    if not audio_url or "youtube.com/watch" in audio_url:
        await safe_send(f"{member.mention} ⏱️ Timer acabou — o YouTube não deixou pegar o áudio ❌", ephemeral=True)
        return

    # Configurações FFmpeg
    try:
        # Cria e reproduz a fonte de áudio
        source = discord.FFmpegPCMAudio(
            audio_url,
            executable=str(FFMPEG_PATH),
            before_options=FFMPEG_OPTIONS['before_options'],
            options=FFMPEG_OPTIONS['options']
        )

        if isinstance(voice_client, discord.VoiceClient):
            # Se já estiver tocando algo, para a música para tocar o alarme
            if voice_client.is_playing():
                voice_client.stop()
            
            # Armazena música atual para controle de permissões
            # Channel ID é o canal da interação, fallback 0
            cid = interaction.channel_id if interaction.channel_id else 0
            bot.current_track[interaction.guild.id] = MusicTrack(audio_url, title, member.id, cid, member.display_name)
            voice_client.play(source)
            await safe_send(f"{member.mention} ⏱️ Timer acabou — tocando agora: **{title}**, aproveita aí!")
    except Exception as e:
        await safe_send(f"{member.mention} ⏱️ Acabou o timer mas deu ruim ao reproduzir: {str(e)[:50]}")


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
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Obtém o cliente de voz atual
    voice_client = guild.voice_client  # type: ignore[assignment]
    if voice_client is None or (isinstance(voice_client, discord.VoiceClient) and not voice_client.is_playing()):  # type: ignore[attr-defined]
        await interaction.response.send_message(
            "Nada tá tocando agora, visse?",
            ephemeral=True
        )
        return
    
    # Para a reprodução
    if isinstance(voice_client, discord.VoiceClient):
        voice_client.stop()  # type: ignore[attr-defined]
    
    # Limpa a fila para este servidor
    bot.music_queue[guild.id] = []
    
    # Desativa loops
    if guild.id in bot.loop_control:
        bot.loop_control[guild.id] = {'loop_track': False, 'loop_queue': False}
    
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
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Obtém o cliente de voz e valida se há música tocando
    voice_client = guild.voice_client  # type: ignore[assignment]
    if voice_client is None or not voice_client.is_playing():  # type: ignore[attr-defined]
        await interaction.response.send_message(
            "Nada tá tocando agora, visse?",
            ephemeral=True
        )
        return
    
    # Pausa a reprodução
    voice_client.pause()  # type: ignore[attr-defined]
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
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Obtém o cliente de voz e valida se há música pausada
    voice_client = guild.voice_client  # type: ignore[assignment]
    if voice_client is None or voice_client.is_playing():  # type: ignore[attr-defined]
        await interaction.response.send_message(
            "Não achei nenhuma música pausada, visse?",
            ephemeral=True
        )
        return
    
    # Retoma a reprodução
    voice_client.resume()  # type: ignore[attr-defined]
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
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Obtém o cliente de voz e valida se há música tocando
    voice_client = guild.voice_client  # type: ignore[assignment]
    if voice_client is None or not voice_client.is_playing():  # type: ignore[attr-defined]
        await interaction.response.send_message(
            "Nada tá tocando agora, visse?",
            ephemeral=True
        )
        return
    
    # Verifica se há próxima música na fila
    if guild.id in bot.music_queue and bot.music_queue[guild.id]:
        await interaction.response.send_message("⏭️ Pulei pra próxima, vamo que vamo.")
    else:
        await interaction.response.send_message("⏭️ Pulei a música, mas não tem mais nada na fila.")
    
    # Para a música atual (pula)
    voice_client.stop()  # type: ignore[attr-defined]


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
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Limpa a fila para este servidor
    bot.music_queue[guild.id] = []
    
    await interaction.response.send_message("🗑️ Limpei a fila, tá zerado.", ephemeral=True)


@bot.tree.command(name="agora", description="Mostra qual música está tocando agora")
async def agora(interaction: discord.Interaction):
    """
    Comando para exibir a música atualmente tocando.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
    """
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Valida se há música tocando
    voice_client = guild.voice_client  # type: ignore[assignment]
    if voice_client is None or not voice_client.is_playing():  # type: ignore[attr-defined]
        await interaction.response.send_message(
            "Nada tá tocando agora, visse?",
            ephemeral=True
        )
        return
    
    # Obtém a música atual
    current = bot.current_track.get(guild.id)
    if not current:
        await interaction.response.send_message(
            "Não consegui encontrar a música atual.",
            ephemeral=True
        )
        return
    
    # Cria o embed
    embed = discord.Embed(
        title="🎵 Tocando Agora",
        description=current.title,
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="Requisitado por",
        value=current.requester,
        inline=True
    )
    
    # Mostra status dos loops
    loop_track = bot.loop_control.get(guild.id, {}).get('loop_track', False)
    loop_queue = bot.loop_control.get(guild.id, {}).get('loop_queue', False)
    
    loop_status = []
    if loop_track:
        loop_status.append("🔁 Loop da música")
    if loop_queue:
        loop_status.append("🔁 Loop da fila")
    
    if loop_status:
        embed.add_field(
            name="Status",
            value="\n".join(loop_status),
            inline=True
        )
    
    # Mostra próximas músicas na fila
    queue = bot.music_queue.get(guild.id, [])
    if queue:
        next_tracks = "\n".join(
            f"{i}. {track.title}" 
            for i, track in enumerate(queue[:3], 1)
        )
        if len(queue) > 3:
            next_tracks += f"\n... + {len(queue) - 3} mais"
        embed.add_field(
            name="Próximas",
            value=next_tracks,
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="comandos", description="Lista os comandos disponíveis do bot")
async def comandos(interaction: discord.Interaction):
    """
    Lista os comandos públicos do bot com uma breve descrição.
    """
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return

    embed = discord.Embed(title="📜 Comandos do CabaBot", color=discord.Color.blurple())

    embed.add_field(
        name="🎶 Música",
        value=(
            "`/musica <url|nome>` — Toca uma música (aceita playlist).\n"
            "`/parar` — Para e limpa a fila.\n"
            "`/pausar` — Pausa a reprodução.\n"
            "`/retomar` — Retoma a reprodução.\n"
            "`/pular` — Pula para a próxima música.\n"
            "`/limpar_fila` — Limpa a fila.\n"
            "`/fila` — Mostra a fila atual.\n"
            "`/agora` — Mostra a música que está tocando now."
        ),
        inline=False,
    )

    embed.add_field(
        name="⏱️ Timers",
        value=(
            "`/timer <segundos> <url|nome>` — Define um timer que toca uma música."
        ),
        inline=False,
    )

    embed.add_field(
        name="🛠️ Utilitários",
        value=(
            "`/ping` — Teste de resposta.\n"
            "`/soma <n1> <n2>` — Soma dois números.\n"
            "`/perfil <membro>` — Exibe o perfil de um usuário."
        ),
        inline=False,
    )

    embed.set_footer(text=f"Solicitado por {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="fila", description="Mostra a fila de músicas")
async def fila(interaction: discord.Interaction):
    """
    Comando para exibir a fila de reprodução.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
    """
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    queue = bot.music_queue.get(guild.id, [])
    
    if not queue:
        await interaction.response.send_message("📋 A fila tá vazia, não tem música enfileirada.", ephemeral=True)
        return
    
    # Cria o embed com a fila
    embed = discord.Embed(
        title="📋 Fila de Músicas",
        description=f"Total: **{len(queue)}** música(s) enfileirada(s)",
        color=discord.Color.blue()
    )
    
    # Mostra até 10 próximas músicas
    for idx, track in enumerate(queue[:10], 1):
        embed.add_field(
            name=f"#{idx}",
            value=f"**{track.title}**\nRequisitado por: {track.requester}",
            inline=False
        )
    
    if len(queue) > 10:
        embed.add_field(
            name="...",
            value=f"+ {len(queue) - 10} música(s)",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="loop", description="Ativa/desativa loop da música atual")
@app_commands.describe(enabled="true para ativar, false para desativar")
async def loop_track(interaction: discord.Interaction, enabled: Optional[bool] = None):
    """
    Comando para ativar/desativar loop da música atual.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        enabled (bool): Ativar ou desativar (toggle se None)
    """
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Valida se há música tocando
    voice_client = guild.voice_client
    if voice_client is None or (isinstance(voice_client, discord.VoiceClient) and not voice_client.is_playing()):
        await interaction.response.send_message(
            "Nada tá tocando agora, visse?",
            ephemeral=True
        )
        return
    
    # Inicializa loop_control para a guild se não existir
    if guild.id not in bot.loop_control:
        bot.loop_control[guild.id] = {'loop_track': False, 'loop_queue': False}
    
    # Toggle ou define o valor
    if enabled is None:
        bot.loop_control[guild.id]['loop_track'] = not bot.loop_control[guild.id]['loop_track']
    else:
        bot.loop_control[guild.id]['loop_track'] = bool(enabled)
    
    state = "ativado" if bot.loop_control[guild.id]['loop_track'] else "desativado"
    await interaction.response.send_message(f"🔁 Loop da música {state}.", ephemeral=True)


@bot.tree.command(name="loop_fila", description="Ativa/desativa loop da fila de músicas")
@app_commands.describe(enabled="true para ativar, false para desativar")
async def loop_queue(interaction: discord.Interaction, enabled: Optional[bool] = None):
    """
    Comando para ativar/desativar loop da fila de músicas.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        enabled (bool): Ativar ou desativar (toggle se None)
    """
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "Oxente — esse comando só funciona dentro de um servidor, visse?",
            ephemeral=True
        )
        return
    
    # Valida se há música tocando
    voice_client = guild.voice_client
    if voice_client is None or (isinstance(voice_client, discord.VoiceClient) and not voice_client.is_playing()):
        await interaction.response.send_message(
            "Nada tá tocando agora, visse?",
            ephemeral=True
        )
        return
    
    # Inicializa loop_control para a guild se não existir
    if guild.id not in bot.loop_control:
        bot.loop_control[guild.id] = {'loop_track': False, 'loop_queue': False}
    
    # Toggle ou define o valor
    if enabled is None:
        bot.loop_control[guild.id]['loop_queue'] = not bot.loop_control[guild.id]['loop_queue']
    else:
        bot.loop_control[guild.id]['loop_queue'] = bool(enabled)
    
    state = "ativado" if bot.loop_control[guild.id]['loop_queue'] else "desativado"
    await interaction.response.send_message(f"🔁 Loop da fila {state}.", ephemeral=True)


# ============================================================================
# COMANDOS - UTILIDADE
# ============================================================================




@bot.tree.command(name="ping", description="Comando de teste simples")
async def ping(interaction: discord.Interaction):
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
