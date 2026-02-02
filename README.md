# 🎵 CabaBot - Discord Music Bot

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Discord](https://img.shields.io/badge/Discord-API-5865F2.svg)](https://discord.com/developers/docs)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Async](https://img.shields.io/badge/Async-await-brightgreen.svg)](https://docs.python.org/3/library/asyncio.html)

> **👨‍💻 Desenvolvido por Gabriel Penha (Gabaoun)** -
> 
**CabaBot** é um bot de música enterprise-grade para Discord, demonstrando expertise em desenvolvimento assíncrono, processamento de áudio em tempo real e integração de múltiplas APIs. Projetado com arquitetura escalável e padrões de engenharia modernos.


## 💼 Stack Tecnológico & Arquitetura

### 🎯 Core Technologies
| Camada | Tecnologia | Propósito |
|--------|------------|-----------|
| **Backend** | Python 3.13+ | Desenvolvimento com type hints modernos |
| **Framework** | discord.py | API Gateway do Discord com voice support |
| **Concurrency** | asyncio | Non-blocking I/O para performance |
| **Audio Processing** | FFmpeg + yt-dlp | Stream de áudio em tempo real |
| **API Integration** | Spotify API | Conversão cross-platform de links |
| **UI Framework** | discord.ui | Componentes interativos reativos |
| **Containerization** | Docker + Docker Compose | Deploy production-ready |
| **Quality** | mypy, pytest | Type safety e test automation |

### 🏗️ Padrões de Projeto Implementados
- **Observer Pattern**: Event-driven architecture para voice events
- **Strategy Pattern**: Múltiplos providers de áudio (YouTube, Spotify)
- **Factory Pattern**: Criação de players customizados por servidor
- **Command Pattern**: Undo/Redo para operações de fila
- **Singleton**: Gerenciamento de conexões voice compartilhadas

## 🚀 Funcionalidades Enterprise

### 🎵 Core Features
- **🎧 High-Fidelity Streaming**: Processamento de áudio em tempo real com qualidade adaptativa
- **🎮 Interactive Controls**: Interface reativa com botões, sliders e modais
- **📊 Multi-Server Queue**: Sistema de playlist isolado por servidor com persistência
- **⏰ Smart Timers**: Sistema de agendamento assíncrono com notificações customizáveis
- **🔄 Cross-Platform Integration**: Conversão automática Spotify → YouTube
- **🛡️ Error Recovery**: Tratamento robusto de falhas com auto-reconexão

### 🏆 Diferenciais Técnicos
- **Zero-Downtime Deployment**: Hot reload sem desconectar usuários
- **Memory Management**: Otimização de recursos para 24/7 operation
- **Rate Limiting**: Proteção contra abuse com throttling inteligente
- **Monitoring**: Health checks e métricas de performance em tempo real
- **Security**: Input sanitization e proteção contra injeção de código

## 🚀 Como Executar

### Opção 1: Docker (Recomendado)
A maneira mais fácil e limpa de rodar, sem instalar nada na sua máquina além do Docker.

1.  **Crie o arquivo .env** com seu token:
    ```env
    TOKEN=seu_token_aqui
    ```
2.  **Suba o container**:
    ```bash
    docker-compose up -d
    ```

### Opção 2: Python Local
Se desejar testar o código diretamente:

1.  **Clone o repositório**
    ```bash
    git clone <url-do-repositorio>
    cd CabaBot
    ```

1.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuração**
    Crie um arquivo `.env` na raiz:
    ```env
    TOKEN=seu_token_discord_aqui
    
    # Opcional: Para suporte a links do Spotify
    SPOTIPY_CLIENT_ID=seu_client_id
    SPOTIPY_CLIENT_SECRET=seu_client_secret
    ```
    *(Consiga as chaves em: https://developer.spotify.com/dashboard)*

3.  **Inicie**
    ```bash
    python CabaBot.py
    ```

---
*Projeto para fins de estudo e portfólio.*