# 🎵 CabaBot - Discord Music & Utility Bot

Um bot Discord robusto, assíncrono e multifuncional desenvolvido com foco em reprodução de áudio de alta qualidade e gerenciamento de filas.

## ✨ Características Principais

### 🎶 Reprodução de Música
- **Busca e reprodução do YouTube** - Integração com yt-dlp para extração de áudio em tempo real
- **Qualidade adaptativa** - Prioriza formato m4a para melhor compatibilidade e estabilidade
- **Reconexão automática** - Trata desconexões com retry configurável
- **Gerenciamento inteligente** - Conecta e alterna automaticamente entre canais de voz

### ⏱️ Sistema de Timers
- **Timers assíncronos** - Não bloqueia o bot durante a contagem
- **Toque customizável** - Reproduz qualquer música do YouTube ao fim do timer

### 🛠️ Comandos Disponíveis

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `/musica` | Reproduz música do YouTube | `/musica url:<URL ou termo>` |
| `/timer` | Timer com toque musical | `/timer segundos:<int> url:<URL>` |
| `/parar` | Para a reprodução | `/parar` |
| `/pausar` | Pausa a música | `/pausar` |
| `/retomar` | Retoma a música pausada | `/retomar` |
| `/pular` | Pula para próxima música | `/pular` |
| `/limpar_fila` | Limpa fila de reprodução | `/limpar_fila` |
| `/ping` | Verifica conexão do bot | `/ping` |
| `/soma` | Calculadora simples | `/soma num1:<float> num2:<float>` |
| `/perfil` | Exibe avatar de membro | `/perfil membro:<@usuario>` |

## 🔧 Arquitetura Técnica

### Tecnologias Utilizadas
- **discord.py** - Framework principal
- **yt-dlp** - Extrator de áudio
- **FFmpeg** - Processamento de áudio
- **asyncio** - Programação assíncrona

## 📋 Pré-requisitos

- Python 3.8+
- Discord.py 2.0+
- FFmpeg (incluído em `/bin/ffmpeg/`)
- Token do Discord Bot

## 🚀 Instalação Rápida

1. **Clone o repositório**
   ```bash
   git clone <url>
   cd CabaBot
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o token**
   Crie um arquivo `.env`:
   ```env
   TOKEN=seu_token_aqui
   ```

4. **Execute o bot**
   ```bash
   python CabaBot.py
   ```

## 🔐 Segurança

- **Token Protection** - Token apenas exibido por comprimento nos logs
- **Ephemeral Messages** - Comandos sensíveis usam respostas privadas

## 📝 Documentação Adicional

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Guia de uso dos comandos de música e utilitários
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de versões

## 📄 Licença

Este projeto é fornecido como está para fins educacionais e de uso pessoal.

---

**Desenvolvido com ☕ e ❤️** - CabaBot Team 2026