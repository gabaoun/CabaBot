# 🎵 CabaBot

> **Projeto de Portfólio**: Um bot de música para Discord desenvolvido em **Python**, focado em **processamento de áudio assíncrono** e código limpo.

Este projeto foi criado para aplicar conceitos avançados de programação, gerenciamento de filas e interação com APIs em tempo real.

---

## 🛠️ Tecnologias e Habilidades Aplicadas

*   **Linguagem:** Python 3.13+
*   **Framework:** `discord.py` (Interação com API do Discord)
*   **Assincronismo:** `asyncio` (Para não bloquear a execução durante downloads/streams)
*   **Áudio:** `FFmpeg` & `yt-dlp` (Processamento de stream e extração de metadados)
*   **Boas Práticas:** Tipagem estática (`mypy`), Tratamento de erros robusto, Variáveis de ambiente (`.env`).

## ✨ O Que o Bot Faz?

O CabaBot gerencia uma experiência de áudio completa em servidores do Discord:

1.  **Streaming de Áudio:** Busca e toca músicas do YouTube com qualidade adaptativa.
2.  **Gerenciamento de Fila:** Sistema de playlist por servidor (cada servidor tem sua própria fila isolada).
3.  **Controle em Tempo Real:** Comandos para pausar, pular, retomar e loops.
4.  **Timers Assíncronos:** Utilitário para definir lembretes que tocam um som específico ao finalizar.

## 🚀 Como Executar (Localmente)

Se desejar testar o código em sua máquina:

1.  **Clone o repositório**
    ```bash
    git clone <url-do-repositorio>
    cd CabaBot
    ```

2.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuração**
    Crie um arquivo `.env` na raiz com seu token:
    ```env
    TOKEN=seu_token_discord_aqui
    ```

4.  **Inicie**
    ```bash
    python CabaBot.py
    ```

## 📬 Sobre o Desenvolvedor

Olá! Sou um desenvolvedor apaixonado por backend e automação. Construí este bot para demonstrar minha capacidade de entregar software funcional, organizado e bem documentado.

Estou em busca de oportunidades onde possa contribuir com meu código e continuar aprendendo. Se gostou da estrutura deste projeto, adoraria conversar!

---
*Projeto para fins de estudo e portfólio.*
