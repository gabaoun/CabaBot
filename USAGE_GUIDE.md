# 🎮 Funcionalidades Principais

Aqui estão os principais recursos disponíveis no bot, demonstrando a interação com o usuário via **Slash Commands** (`/`).

## 🎵 Sistema de Música

O foco principal do projeto. O bot entra no canal de voz e gerencia o stream.

*   `/musica [url/nome]`
    *   **O que faz:** Busca o áudio e toca. Aceita links diretos ou termos de busca.
    *   **Destaque:** Se já tiver algo tocando, ele adiciona inteligentemente à fila.
*   `/pausar` e `/retomar`
    *   **O que faz:** Controle total do estado do player.
*   `/pular`
    *   **O que faz:** Avança para a próxima faixa da fila.
*   `/fila`
    *   **O que faz:** Mostra visualmente (Embed) as próximas músicas.

## ⏱️ Utilitários Assíncronos

Demonstração de tarefas que rodam em paralelo sem travar o bot.

*   `/timer [segundos] [url]`
    *   **Cenário:** "Me avise em 5 minutos tocando a música do Rocky Balboa".
    *   **Técnica:** Usa `asyncio.sleep` para não bloquear outros comandos enquanto espera.
*   `/ping`
    *   **Uso:** Verifica a latência da conexão com a API.

---
*Documentação simplificada para demonstração de funcionalidades.*
