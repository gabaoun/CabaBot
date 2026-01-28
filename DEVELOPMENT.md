# 👨‍💻 Guia de Desenvolvimento

## Estrutura do Projeto

### `CabaBot` (Classe Principal)

**Responsabilidade:** Gerenciar conexão com Discord e comandos Slash.

**Componentes Principais:**
- `music_queue`: Gerencia filas de reprodução por servidor
- `current_track`: Rastreia o que está tocando
- `loop_control`: Gerencia loops de faixa e fila

### Sistema de Áudio

O bot utiliza `yt-dlp` para extrair URLs de stream direto do YouTube e `ffmpeg` para processar e transmitir o áudio para o Discord.

**Fluxo de Reprodução:**
1. Usuário solicita `/musica`
2. `search_ytdlp_async` busca metadados em thread separada
3. `_get_stream_url` seleciona a melhor URL de áudio
4. `MusicTrack` é criado e adicionado à fila
5. `_play_next_track` processa a fila e inicia o `FFmpegPCMAudio`

---

## Performance e Escalabilidade

- **Asyncio**: Todas as operações de rede (YouTube, Discord API) são assíncronas.
- **Filas Isoladas**: Cada servidor (guild) tem sua própria fila e estado de player.

## Debugging

Logs são impressos no console padrão. Verifique a saída do terminal para erros de FFmpeg ou exceções de conexão.

---

**Boa sorte desenvolvendo! 🚀**