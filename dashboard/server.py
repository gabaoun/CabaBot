from aiohttp import web
import aiohttp_jinja2
import jinja2
import os
import asyncio
import discord

class WebServer:
    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.routes = web.RouteTableDef()
        self._setup_routes()
        
        # Configura templates
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader(template_path))

    def _setup_routes(self):
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/api/status', self.handle_status)
        self.app.router.add_post('/api/control/{action}', self.handle_control)
        self.app.router.add_post('/api/queue/add', self.handle_add_queue)
        self.app.router.add_post('/api/queue/remove', self.handle_remove_queue)
        self.app.router.add_static('/static/', path=os.path.join(os.path.dirname(__file__), 'static'), name='static')

    @aiohttp_jinja2.template('index.html')
    async def handle_index(self, request):
        return {'bot_name': self.bot.user.name if self.bot.user else "CabaBot"}

    async def handle_status(self, request):
        """Retorna o estado atual do bot (música tocando, fila, etc)."""
        status = []
        for guild in self.bot.guilds:
            voice_client = guild.voice_client
            track = self.bot.current_track.get(guild.id)
            queue = self.bot.music_queue.get(guild.id, [])
            
            queue_data = [{'title': t.title, 'requester': t.requester} for t in queue]
            
            guild_data = {
                'id': str(guild.id),
                'name': guild.name,
                'is_playing': voice_client.is_playing() if voice_client else False,
                'is_paused': voice_client.is_paused() if voice_client else False,
                'current_track': {
                    'title': track.title,
                    'requester': track.requester
                } if track else None,
                'queue_count': len(queue),
                'queue': queue_data,
                'has_history': bool(self.bot.music_history.get(guild.id))
            }
            status.append(guild_data)
        
        return web.json_response(status)

    async def handle_add_queue(self, request):
        try:
            data = await request.json()
            guild_id = int(data.get('guild_id'))
            query = data.get('query')
        except (ValueError, TypeError):
            return web.Response(status=400, text="Invalid Data")

        guild = self.bot.get_guild(guild_id)
        if not guild: return web.Response(status=404, text="Guild not found")

        # Usa channel_id 0 ou tenta pegar o último usado
        channel_id = 0
        if guild.id in self.bot.last_player_message:
            try:
                channel_id = self.bot.last_player_message[guild.id].channel.id
            except: pass

        res = await self.bot.add_track_to_guild(guild, query, 0, "Dashboard User", channel_id)
        return web.json_response({'message': res})

    async def handle_remove_queue(self, request):
        try:
            data = await request.json()
            guild_id = int(data.get('guild_id'))
            index = int(data.get('index'))
        except (ValueError, TypeError):
             return web.Response(status=400, text="Invalid Data")

        if guild_id in self.bot.music_queue:
            try:
                self.bot.music_queue[guild_id].pop(index)
            except IndexError:
                return web.Response(status=400, text="Index out of bounds")
        return web.json_response({'status': 'ok'})

    async def handle_control(self, request):
        """Recebe comandos da interface web (pause, skip, stop, previous)."""
        action = request.match_info['action']
        try:
            data = await request.json()
            guild_id = int(data.get('guild_id'))
        except (ValueError, TypeError):
            return web.Response(status=400, text="Invalid Guild ID")
        
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return web.Response(status=404, text="Guild not found")
            
        vc = guild.voice_client
        if not vc or not isinstance(vc, discord.VoiceClient):
             return web.Response(status=400, text="Not connected to voice")

        if action == 'pause':
            if vc.is_playing(): vc.pause()
            elif vc.is_paused(): vc.resume()
        elif action == 'skip':
            vc.stop()
        elif action == 'previous':
            await self.bot.play_previous_track(guild)
        elif action == 'stop':
            # Limpa fila
            if guild.id in self.bot.music_queue:
                self.bot.music_queue[guild.id] = []
            vc.stop()
            
        return web.json_response({'status': 'ok'})

    async def start(self):
        """Inicia o servidor web na porta 8080."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        print("🌐 Dashboard rodando em http://localhost:8080")
