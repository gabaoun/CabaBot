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
- Sistema modular de testes de atributos com participação de múltiplos usuários
- Comandos de utilidade (calculadora, perfil de usuário, teste de conexão)

Author: CabaBot Team
Version: 1.2.0
"""

import random
import discord
import asyncio
import math
import os
import yt_dlp
from discord import app_commands
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import json
from typing import Dict, Any, List, Tuple, Optional

# Carrega as variáveis de ambiente do arquivo .env
# find_dotenv() procura automaticamente na árvore de diretórios
load_dotenv(find_dotenv())

# Define o caminho base do script e a localização do ffmpeg local
SCRIPT_DIR = Path(__file__).parent
FFMPEG_PATH = SCRIPT_DIR / "bin" / "ffmpeg" / "ffmpeg.exe"
print(f"FFMPEG path: {FFMPEG_PATH} exists={FFMPEG_PATH.exists()}")

# Áudio a ser reproduzido quando o bot ficar online (padrão: vídeo do YouTube)
STARTUP_AUDIO_URL = random.choice(["https://www.youtube.com/watch?v=6xoJCJYLzZw", "https://www.youtube.com/watch?v=biZlbJAdyTE", "https://www.youtube.com/watch?v=sR9KWAIFSfc", "https://www.youtube.com/watch?v=xmf99leO-Z0", "https://www.youtube.com/watch?v=8zslY2eYJ9M"])

# Path para configuração persistente por guild
CONFIG_PATH = SCRIPT_DIR / "config.json"

# Configurações reutilizáveis para yt-dlp (evita duplicação de código)
YTDLP_OPTIONS = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'cachedir': False,
}

# Configurações reutilizáveis para FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    # Temporariamente usa loglevel info e sem filtro de áudio para facilitar debug
    'options': '-vn -loglevel info',
}


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
        # Controle de loop por guild: {'guild_id': {'loop_track': bool, 'loop_queue': bool}}
        self.loop_control = {}
        # Música atual tocando por guild: {'guild_id': MusicTrack}
        self.current_track = {}
        # Sessões de votação por guild
        self.vote_sessions = {}

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
                voice_channel = next(
                    (ch for ch in guild.voice_channels if any(not m.bot for m in ch.members)),
                    None
                )
                if voice_channel is None:
                    return

                voice_client = await _get_or_connect_voice_client(guild, voice_channel)
                if voice_client is None:
                    return

                # Verifica se startup está habilitado para esta guild e globalmente
                global_enabled = os.getenv("STARTUP_AUDIO_ENABLED", "true").lower() in ("1", "true", "yes", "on")
                if not global_enabled or not guild_startup_enabled(guild.id):
                    return

                # Busca a URL de áudio via yt-dlp
                query = STARTUP_AUDIO_URL if STARTUP_AUDIO_URL.startswith("http") else f'ytsearch:{STARTUP_AUDIO_URL}'
                results = await search_ytdlp_async(query, YTDLP_OPTIONS)
                if not results:
                    return
                track = results['entries'][0] if 'entries' in results else results
                # Debug: inspeciona chave/estrutura retornada pelo yt-dlp
                try:
                    print(f"DEBUG startup track keys: {list(track.keys())}")
                except Exception:
                    print("DEBUG startup: track is not a mapping")
                audio_url = _get_stream_url(track)
                title = track.get('title', 'Música de boas-vindas')
                if not audio_url or "youtube.com/watch" in audio_url:
                    return

                source = discord.FFmpegPCMAudio(
                    audio_url,
                    executable=str(FFMPEG_PATH),
                    before_options=FFMPEG_OPTIONS['before_options'],
                    options=FFMPEG_OPTIONS['options']
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
    voice_channel: discord.VoiceChannel
) -> discord.VoiceClient | None:  # type: ignore[return-value]
    """
    Obtém o cliente de voz atual ou conecta a um novo canal.
    
    Args:
        guild (discord.Guild): O servidor
        voice_channel (discord.VoiceChannel): O canal de voz destino
        
    Returns:
        discord.VoiceClient | None: Cliente de voz conectado ou None se erro
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


async def _run_vote_for_action(
    interaction: discord.Interaction,
    guild: discord.Guild,
    voice_channel: discord.VoiceChannel,
    action_name: str,
    timeout: int = 30,
) -> bool:
    """
    Inicia uma votação pública no canal de texto da interação para aprovar
    uma ação de controle de reprodução (pular/pausar/parar).

    Retorna True se a votação atingir o limiar (>50% dos membros humanos
    presentes no canal de voz) dentro do tempo limite, caso contrário False.
    """
    # Evita concorrência de votações por guild
    if guild.id in bot.vote_sessions:
        try:
            await interaction.response.send_message(
                "Já tem uma votação em andamento neste servidor, visse? Tenta de novo mais tarde.",
                ephemeral=True,
            )
        except Exception:
            pass
        return False

    # Conta apenas membros humanos no canal de voz
    human_members = [m for m in voice_channel.members if not m.bot]
    num_humans = len(human_members)
    if num_humans == 0:
        # Sem usuários humanos, nega por segurança
        try:
            await interaction.response.send_message("Não há participantes humanos no canal de voz.", ephemeral=True)
        except Exception:
            pass
        return False

    votes_needed = (num_humans // 2) + 1  # exige >50%

    # Mensagem pública de votação
    try:
        vote_msg = await interaction.channel.send(
            f"🗳️ Votação para **{action_name}** iniciada por {interaction.user.mention}.\n"
            f"Reaja com ✅ para concordar. São necessários **{votes_needed}** votos de **{num_humans}** participantes em {timeout}s."
        )
    except Exception:
        try:
            await interaction.response.send_message("Não consegui iniciar a votação no canal.", ephemeral=True)
        except Exception:
            pass
        return False

    # adiciona reação inicial para facilitar votação
    try:
        await vote_msg.add_reaction("✅")
    except Exception:
        pass

    # registra sessão para evitar concorrência
    bot.vote_sessions[guild.id] = {'message_id': vote_msg.id, 'required': votes_needed}

    # aguarda o tempo definido e então conta votos válidos
    await asyncio.sleep(timeout)

    passed = False
    votes = 0
    try:
        # procura reação ✅ na mensagem
        reaction = None
        for r in vote_msg.reactions:
            if str(r.emoji) == '✅':
                reaction = r
                break

        if reaction is not None:
            users = []
            async for u in reaction.users():
                if u.bot:
                    continue
                # conta apenas se o usuário ainda estiver no canal de voz
                if any(u.id == m.id for m in voice_channel.members):
                    users.append(u)
            votes = len({u.id for u in users})

        if votes >= votes_needed:
            passed = True
    except Exception:
        passed = False

    # limpa sessão
    try:
        del bot.vote_sessions[guild.id]
    except Exception:
        pass

    # informa resultado
    try:
        if passed:
            await interaction.channel.send(f"✅ Votação aprovada: {votes}/{num_humans} votos.")
        else:
            await interaction.channel.send(f"❌ Votação rejeitada: {votes}/{num_humans} votos.")
    except Exception:
        pass

    return passed


class MusicTrack:
    """Representa uma faixa de música na fila."""

    def __init__(self, url: str, title: str, requester, requester_name: Optional[str] = None):
        """
        Inicializa uma faixa de música.

        Args:
            url (str): URL do áudio
            title (str): Título da música
            requester (int|str): ID do usuário que requisitou ou nome
            requester_name (str | None): Nome do usuário (se requester for id)
        """
        self.url = url
        self.title = title
        if isinstance(requester, int):
            self.requester_id = requester
            self.requester = requester_name or str(requester)
        else:
            self.requester_id = None
            self.requester = str(requester)


async def _play_next_track(guild: discord.Guild) -> None:
    """
    Reproduz a próxima música da fila.
    
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
        # Se não há fila ou está vazia, retorna
        if guild.id not in bot.music_queue or not bot.music_queue[guild.id]:
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
        print(f"🎵 Tocando: {track.title} (requisitado por {track.requester})")
    except Exception as e:
        print(f"Erro ao reproduzir faixa: {e}")


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

    # Validações básicas de guild e membro
    member = await _validate_guild_and_member(interaction)
    if member is None:
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

    # Se não for URL, adiciona prefixo de busca para YouTube Search
    query = 'ytsearch:' + url if not url.startswith("http") else url
    # Decide se deve permitir playlists/mixes (URLs com list= ou playlist)
    allow_playlist = False
    if url.startswith("http") and ("list=" in url or "playlist" in url):
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
            mt = MusicTrack(audio_url_e, title_e, interaction.user.id, interaction.user.display_name)
            bot.music_queue[interaction.guild.id].append(mt)
            added += 1

        # Se nada estava tocando, toca a primeira da fila
        voice_client = await _get_or_connect_voice_client(interaction.guild, voice_channel)
        if voice_client is None:
            await interaction.followup.send("Erro ao conectar ao canal de voz, tenta de novo aí.")
            return

        if not voice_client.is_playing() and bot.music_queue[interaction.guild.id]:
            next_track = bot.music_queue[interaction.guild.id].pop(0)
            bot.current_track[interaction.guild.id] = next_track
            source = discord.FFmpegPCMAudio(next_track.url, executable=str(FFMPEG_PATH), **FFMPEG_OPTIONS)
            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(_play_next_track(interaction.guild), bot.loop))

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
            **FFMPEG_OPTIONS
        )

        # Cria a faixa de música
        track = MusicTrack(audio_url, title, interaction.user.id, interaction.user.display_name)
        
        # Inicializa a fila para este servidor se não existir
        if interaction.guild.id not in bot.music_queue:
            bot.music_queue[interaction.guild.id] = []
        
        # Se não há música tocando, toca direto e configura callback para próxima
        if not voice_client.is_playing():
            def after_track(error):
                if error:
                    print(f"Erro ao reproduzir: {error}")
                asyncio.run_coroutine_threadsafe(_play_next_track(interaction.guild), bot.loop)
            
            # Armazena a música atual
            bot.current_track[interaction.guild.id] = track
            # Inicializa controle de loop se não existir
            if interaction.guild.id not in bot.loop_control:
                bot.loop_control[interaction.guild.id] = {'loop_track': False, 'loop_queue': False}
            
            print(f"DEBUG musica: about to play title={title} url_len={len(audio_url) if audio_url else 0} vc={voice_client} channel={getattr(voice_client.channel,'name',None)}")
            voice_client.play(source, after=after_track)
            await interaction.followup.send(f"🎵 Tô tocando: **{title}** — aproveita aí")
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
            **FFMPEG_OPTIONS
        )

        if isinstance(voice_client, discord.VoiceClient):
            # Armazena música atual para controle de permissões
            bot.current_track[interaction.guild.id] = MusicTrack(audio_url, title, member.id, member.display_name)
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
    if voice_client is None or not voice_client.is_playing():  # type: ignore[attr-defined]
        await interaction.response.send_message(
            "Nada tá tocando agora, visse?",
            ephemeral=True
        )
        return
    
    # Para a reprodução
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
        name="⏱️ Timers / Startup",
        value=(
            "`/timer <segundos> <url|nome>` — Define um timer que toca uma música.\n"
            "`/startup_audio <true|false>` — Ativa/Desativa áudio de boas-vindas."
        ),
        inline=False,
    )

    embed.add_field(
        name="🛠️ Utilitários",
        value=(
            "`/d <lados> <quantidade>` — Rola dados padrão.\n"
            "`/dado_custom <dado> ...` — Rola dados customizados.\n"
            "`/teste_atributo` — Inicia teste participativo.\n"
            "`/ping` — Teste de resposta.\n"
            "`/soma <n1> <n2>` — Soma dois números."
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
    if voice_client is None or not voice_client.is_playing():
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
    if voice_client is None or not voice_client.is_playing():
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
# SISTEMA MODULAR DE TESTES DE ATRIBUTOS
# ============================================================================

class DiceRoller:
    """
    Classe responsável por rolar dados com suporte a modificadores, vantagem e desvantagem.
    Torna o sistema extensível para diferentes tipos de testes.
    """
    
    def __init__(self, dado_str: str, modificador: int = 0, vantagem: bool = False, desvantagem: bool = False):
        """
        Inicializa um rolador de dados.
        
        Args:
            dado_str (str): Formato do dado (ex: 'd20', 'd6', '2d4')
            modificador (int): Modificador a ser adicionado/subtraído ao resultado
            vantagem (bool): Se True, rola 2 vezes e pega o maior resultado
            desvantagem (bool): Se True, rola 2 vezes e pega o menor resultado
        """
        self.dado_str = dado_str.lower().strip()
        self.quantidade, self.lados = self._parse_dado()
        self.modificador = modificador
        self.vantagem = vantagem
        self.desvantagem = desvantagem
        self.resultados: List[int] = []
        self.total = 0
        self.resultado_utilizado = 0  # Para vantagem/desvantagem
        self.resultado_descartado = 0  # Para vantagem/desvantagem
    
    def _parse_dado(self) -> Tuple[int, int]:
        """Extrai quantidade e lados do formato de dado."""
        if 'd' not in self.dado_str:
            raise ValueError(f"Formato inválido: {self.dado_str}")
        
        partes = self.dado_str.split('d')
        try:
            qtd = int(partes[0]) if partes[0] else 1
            lados = int(partes[1])
            
            if qtd < 1 or qtd > 100:
                raise ValueError("Quantidade deve estar entre 1 e 100")
            if lados < 2 or lados > 1000:
                raise ValueError("Lados deve estar entre 2 e 1000")
            
            return qtd, lados
        except (ValueError, IndexError):
            raise ValueError(f"Formato inválido: {self.dado_str}")
    
    def rolar(self) -> None:
        """Rola os dados e armazena os resultados com vantagem/desvantagem se aplicável."""
        if self.vantagem or self.desvantagem:
            # Rola duas vezes quando há vantagem ou desvantagem
            rolagem1 = [random.randint(1, self.lados) for _ in range(self.quantidade)]
            rolagem2 = [random.randint(1, self.lados) for _ in range(self.quantidade)]
            
            soma1 = sum(rolagem1)
            soma2 = sum(rolagem2)
            
            # Seleciona a melhor ou pior rolagem com base em vantagem/desvantagem
            usar_primeira = (soma1 >= soma2) if self.vantagem else (soma1 <= soma2)
            
            self.resultados = rolagem1 if usar_primeira else rolagem2
            self.resultado_utilizado = soma1 if usar_primeira else soma2
            self.resultado_descartado = soma2 if usar_primeira else soma1
            self.total = self.resultado_utilizado
        else:
            # Rolagem normal
            self.resultados = [random.randint(1, self.lados) for _ in range(self.quantidade)]
            self.total = sum(self.resultados)
        
        # Aplica o modificador
        self.total += self.modificador
    
    def format_resultado(self) -> str:
        """Formata o resultado de forma legível."""
        if not self.resultados:
            return "Nenhum resultado disponível"
        
        if self.quantidade == 1:
            return f"**{self.resultados[0]}**"
        else:
            detalhes = ", ".join(map(str, self.resultados))
            return f"`{detalhes}` → **{sum(self.resultados)}**"


class TestConfig:
    """
    Configuração modular para testes de atributos.
    Permite adicionar novos testes facilmente.
    """
    
    def __init__(self, tipo: str, cd: int, dado_str: str, descricao: str = ""):
        """
        Inicializa uma configuração de teste.
        
        Args:
            tipo (str): Nome do atributo/habilidade testada
            cd (str): Classe de Dificuldade
            dado_str (str): Formato do dado a rolar
            descricao (str): Descrição adicional do teste
        """
        self.tipo = tipo.capitalize()
        self.cd = cd
        self.dado = DiceRoller(dado_str)
        self.descricao = descricao
        self.participantes: Dict[int, Tuple[str, int]] = {}  # user_id -> (nome, resultado)
    
    def adicionar_resultado(self, user_id: int, nome: str, resultado: int) -> None:
        """Adiciona o resultado de um participante."""
        self.participantes[user_id] = (nome, resultado)
    
    def get_ranking(self) -> str:
        """Retorna o ranking formatado dos participantes."""
        if not self.participantes:
            return "Nenhum participante ainda."
        
        emojis = ("🥇", "🥈", "🥉")
        ordenado = sorted(self.participantes.values(), key=lambda x: x[1], reverse=True)
        
        return "\n".join(
            f"{emojis[idx] if idx < 3 else f'{idx + 1}.'} **{nome}**: {resultado} "
            f"{'✅ SUCESSO' if resultado >= self.cd else '❌ FALHA'}"
            for idx, (nome, resultado) in enumerate(ordenado)
        )


class RollButton(discord.ui.Button):
    """
    Botão para participar de um teste de atributo.
    Rola o dado configurado e armazena o resultado.
    """
    
    def __init__(self, test_config: TestConfig, test_message_id: int):
        """
        Inicializa o botão de rolagem.
        
        Args:
            test_config (TestConfig): Configuração do teste
            test_message_id (int): ID da mensagem do teste para atualizar
        """
        super().__init__(label="🎲 Rolar", style=discord.ButtonStyle.primary)
        self.test_config = test_config
        self.test_message_id = test_message_id
    
    async def callback(self, interaction: discord.Interaction):
        """Processa o clique no botão."""
        # Verifica se o usuário já participou
        if interaction.user.id in self.test_config.participantes:
            await interaction.response.send_message(
                f"Você já rolou para este teste, {interaction.user.mention}!",
                ephemeral=True
            )
            return
        
        # Rola o dado
        self.test_config.dado.rolar()
        resultado = self.test_config.dado.total
        
        # Armazena o resultado
        self.test_config.adicionar_resultado(
            interaction.user.id,
            interaction.user.display_name,
            resultado
        )
        
        # Resposta ao usuário
        status = "✅ SUCESSO" if resultado >= self.test_config.cd else "❌ FALHA"
        await interaction.response.send_message(
            f"🎲 **{self.test_config.tipo}** ({self.test_config.dado.dado_str})\n"
            f"Seu resultado: **{resultado}** {status}\n"
            f"CD necessária: **{self.test_config.cd}**",
            ephemeral=True
        )
        
        # Atualiza a mensagem do teste com o ranking
        try:
            channel = interaction.channel
            message = await channel.fetch_message(self.test_message_id)
            
            # Cria novo embed com ranking atualizado
            embed = message.embeds[0] if message.embeds else discord.Embed()
            embed.set_field_at(
                2,  # Campo do ranking (3º campo)
                name="📊 Ranking",
                value=self.test_config.get_ranking(),
                inline=False
            )
            await message.edit(embed=embed)
        except Exception as e:
            print(f"Erro ao atualizar mensagem do teste: {e}")


class RollView(discord.ui.View):
    """View que contém o botão de rolagem."""
    
    def __init__(self, test_config: TestConfig, test_message_id: int, timeout: int = 3600):
        """
        Inicializa a view com o botão de rolagem.
        
        Args:
            test_config (TestConfig): Configuração do teste
            test_message_id (int): ID da mensagem do teste
            timeout (int): Tempo em segundos antes do botão expirar
        """
        super().__init__(timeout=timeout)
        self.add_item(RollButton(test_config, test_message_id))


# Armazena testes ativos por canal
active_tests: Dict[int, TestConfig] = {}


# ============================================================================
# COMANDOS - UTILIDADE
# ============================================================================

@bot.tree.command(name="d", description="Rola um dado padrão (d2 até d100)")
@app_commands.describe(
    lados="Número de lados do dado (2, 4, 6, 8, 10, 12, 20, 100)",
    quantidade="Quantidade de dados a rolar (padrão: 1, máximo 100)"
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
    
    Permite rolar um ou mais dados com número de lados pré-definido,
    mostrando os resultados individuais e o total.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        lados (int): Número de lados do dado
        quantidade (int): Quantidade de dados a rolar
    """
    # Valida a quantidade de dados
    if quantidade < 1 or quantidade > 100:
        await interaction.response.send_message(
            f"❌ Quantidade inválida. Use entre 1 e 100 dados, visse?",
            ephemeral=True
        )
        return
    
    try:
        # Usa o DiceRoller para manter consistência
        roller = DiceRoller(f"{quantidade}d{lados}")
        roller.rolar()
        
        # Formata a resposta
        embed = discord.Embed(
            title=f"🎲 Rolagem de {quantidade}d{lados}",
            color=discord.Color.blue()
        )
        
        if quantidade == 1:
            embed.add_field(
                name="Resultado",
                value=f"**{roller.resultados[0]}**",
                inline=False
            )
        else:
            detalhes = ", ".join(map(str, roller.resultados))
            embed.add_field(
                name="Dados Individuais",
                value=f"`{detalhes}`",
                inline=False
            )
            embed.add_field(
                name="Total",
                value=f"**{roller.total}**",
                inline=False
            )
        
        embed.set_footer(text=f"Solicitado por {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        
    except ValueError as e:
        await interaction.response.send_message(
            f"❌ Erro: {str(e)}",
            ephemeral=True
        )


@bot.tree.command(name="dado_custom", description="Rola um dado com número de lados customizado, modificadores e vantagem/desvantagem")
@app_commands.describe(
    dado="Formato do dado (ex: d20, 3d6, 2d10)",
    modificador="Modificador a somar ou subtrair do resultado (ex: +5 ou -2)",
    vantagem="Rola 2 vezes e usa o maior resultado",
    desvantagem="Rola 2 vezes e usa o menor resultado"
)
async def dado_customizado(interaction: discord.Interaction, dado: str, modificador: int = 0, vantagem: bool = False, desvantagem: bool = False):
    """
    Comando para rolar dados com número de lados customizado.
    
    Permite rolar dados em qualquer formato, com opção de modificador, vantagem e desvantagem.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        dado (str): Formato do dado (ex: d20, 3d6, 2d10)
        modificador (int): Modificador a somar ou subtrair do resultado (ex: +5 ou -2)
        vantagem (bool): Se True, rola 2 vezes e usa o maior resultado
        desvantagem (bool): Se True, rola 2 vezes e usa o menor resultado
    """
    # Valida que vantagem e desvantagem não sejam ambas true
    if vantagem and desvantagem:
        await interaction.response.send_message(
            "❌ Você não pode ter vantagem E desvantagem ao mesmo tempo!",
            ephemeral=True
        )
        return
    
    try:
        # Valida e rola o dado com os modificadores
        roller = DiceRoller(dado, modificador=modificador, vantagem=vantagem, desvantagem=desvantagem)
        roller.rolar()
        
        # Determina cores e emojis baseado no tipo de rolagem
        if vantagem:
            cor = discord.Color.gold()
            tipo_roll = "✨ Rolagem com VANTAGEM"
        elif desvantagem:
            cor = discord.Color.dark_red()
            tipo_roll = "💀 Rolagem com DESVANTAGEM"
        else:
            cor = discord.Color.green()
            tipo_roll = "🎲 Rolagem"
        
        # Formata a resposta
        embed = discord.Embed(
            title=f"{tipo_roll} de {roller.dado_str.upper()}",
            color=cor
        )
        
        # Mostra resultados
        if roller.quantidade == 1:
            valor_resultado = f"**{roller.resultados[0]}**"
            if modificador != 0:
                operador = "+" if modificador > 0 else ""
                valor_resultado += f" {operador}{modificador} = **{roller.total}**"
            embed.add_field(
                name="Resultado",
                value=valor_resultado,
                inline=False
            )
        else:
            detalhes = ", ".join(map(str, roller.resultados))
            embed.add_field(
                name="Dados Individuais",
                value=f"`{detalhes}`",
                inline=False
            )
            
            soma_sem_mod = roller.total - modificador
            if modificador != 0:
                operador = "+" if modificador > 0 else ""
                embed.add_field(
                    name="Subtotal",
                    value=f"**{soma_sem_mod}** {operador}{modificador} = **{roller.total}**",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Total",
                    value=f"**{roller.total}**",
                    inline=False
                )
        
        # Se houver vantagem ou desvantagem, mostra os resultados descartados
        if vantagem or desvantagem:
            tipo_desc = "Desvantagem - Descartado" if vantagem else "Vantagem - Descartado"
            embed.add_field(
                name=tipo_desc,
                value=f"`{roller.resultado_descartado}`",
                inline=True
            )
            embed.add_field(
                name="Resultado Utilizado",
                value=f"`{roller.resultado_utilizado}`",
                inline=True
            )
        
        embed.set_footer(text=f"Solicitado por {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        
    except ValueError as e:
        await interaction.response.send_message(
            f"❌ Erro: {str(e)}\n💡 Formato válido: d20, 3d6, 2d10, etc.",
            ephemeral=True
        )


@bot.tree.command(name="teste_atributo", description="Inicia um teste de atributo para múltiplos participantes")
@app_commands.describe(
    tipo="Tipo de atributo testado (ex: Destreza, Força, Inteligência)",
    cd="Classe de Dificuldade (CD) para o teste",
    dado="Tipo de dado a rolar (ex: d20, d12, 2d10)"
)
async def teste_atributo(interaction: discord.Interaction, tipo: str, cd: int, dado: str = "d20"):
    """
    Comando para iniciar um teste de atributo participativo.
    
    Cria um teste onde múltiplos usuários podem clicar em um botão para rolar
    dados. Os resultados são comparados com a CD e exibidos em ranking.
    
    Args:
        interaction (discord.Interaction): A interação do slash command
        tipo (str): Nome do atributo/habilidade testada
        cd (int): Classe de Dificuldade do teste
        dado (str): Formato do dado a usar
    
    Exemplo:
        /teste_atributo tipo:Destreza cd:12 dado:d20
    """
    # Valida os parâmetros
    if cd < 1:
        await interaction.response.send_message(
            "❌ Classe de Dificuldade deve ser maior que 0.",
            ephemeral=True
        )
        return
    
    try:
        # Cria a configuração do teste
        test_config = TestConfig(
            tipo=tipo,
            cd=cd,
            dado_str=dado,
            descricao=f"Teste de {tipo.lower()}"
        )
    except ValueError as e:
        await interaction.response.send_message(
            f"❌ Erro na configuração do teste: {str(e)}",
            ephemeral=True
        )
        return
    
    # Cria o embed do teste
    embed = discord.Embed(
        title=f"🎭 Teste de {test_config.tipo}",
        description=test_config.descricao,
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="Dado",
        value=f"**{test_config.dado.dado_str.upper()}**",
        inline=True
    )
    
    embed.add_field(
        name="Classe de Dificuldade",
        value=f"**CD {test_config.cd}**",
        inline=True
    )
    
    embed.add_field(
        name="📊 Ranking",
        value="Nenhum participante ainda.",
        inline=False
    )
    
    embed.set_footer(text=f"Criado por {interaction.user.display_name}")
    
    # Envia a mensagem com o botão
    view = RollView(test_config, 0)  # ID será atualizado após envio
    await interaction.response.send_message(embed=embed, view=view)
    
    # Obtém a mensagem enviada para armazenar o ID
    response = await interaction.original_response()
    
    # Atualiza o ID da mensagem na view
    for item in view.children:
        if isinstance(item, RollButton):
            item.test_message_id = response.id
    
    # Armazena o teste ativo
    active_tests[response.id] = test_config
    
    print(f"✅ Teste de {tipo} iniciado no canal {interaction.channel_id or 'unknown'}")


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
