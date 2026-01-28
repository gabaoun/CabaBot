# ⚙️ Notas de Engenharia

Este documento detalha algumas decisões técnicas tomadas durante o desenvolvimento para garantir performance e manutenibilidade.

## 1. Arquitetura Assíncrona (Asyncio)

Um desafio comum em bots de música é o bloqueio da execução durante o download de metadados ou conexão de rede.

*   **Solução:** Implementação estrita de `async/await`.
*   **Destaque:** A busca no YouTube (`yt-dlp`) é uma operação bloqueante (I/O intensivo). Para resolver isso, utilizei `loop.run_in_executor` para rodar a extração em uma thread separada, mantendo o loop de eventos do Discord livre para processar outros comandos instantaneamente.

## 2. Gerenciamento de Estado (State Management)

O bot precisa funcionar em múltiplos servidores (guilds) simultaneamente sem cruzar dados.

*   **Estrutura:** Utilização de dicionários com o ID do servidor como chave.
    ```python
    self.music_queue = {}   # {guild_id: [Track1, Track2...]}
    self.current_track = {} # {guild_id: TrackAtual}
    ```
*   **Resultado:** Isolamento total. O que acontece no Servidor A não afeta a fila do Servidor B.

## 3. Qualidade de Código

*   **Type Hinting:** Uso de tipagem estática (ex: `def funcao(arg: int) -> None:`) para facilitar a leitura e uso de ferramentas como `mypy`.
*   **Tratamento de Erros:** Blocos `try/except` estratégicos para garantir que o bot não caia (crash) se o YouTube rejeitar uma conexão ou se o usuário fizer algo inesperado. O bot sempre informa o erro de forma amigável.

---
*Este arquivo visa demonstrar o pensamento técnico por trás do código.*
