# 🎵 CabaBot - Discord Music & Utility Bot

Um bot Discord robusto, assíncrono e multifuncional desenvolvido com foco em reprodução de áudio de alta qualidade, gerenciamento inteligente de comandos e experiência de usuário aprimorada.

## ✨ Características Principais

### 🎶 Reprodução de Música
- **Busca e reprodução do YouTube** - Integração com yt-dlp para extração de áudio em tempo real
- **Qualidade adaptativa** - Prioriza formato m4a para melhor compatibilidade e estabilidade
- **Reconexão automática** - Trata desconexões com retry configurável até 5 segundos
- **Gerenciamento inteligente de canais** - Conecta e alterna automaticamente entre canais de voz

### ⏱️ Sistema de Timers
- **Timers assíncronos** - Não bloqueia o bot durante a contagem
- **Toque customizável** - Reproduz qualquer música do YouTube ao fim do timer
- **Feedback em tempo real** - Mostra status detalhado da operação

### 🎮 Comandos Disponíveis

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `/musica` | Reproduz música do YouTube | `/musica url:<URL ou termo de busca>` |
| `/timer` | Timer com toque musical | `/timer segundos:<int> url:<URL>` |
| `/parar` | Para a reprodução | `/parar` |
| `/pausar` | Pausa a música | `/pausar` |
| `/retomar` | Retoma a música pausada | `/retomar` |
| `/pular` | Pula para próxima música | `/pular` |
| `/limpar_fila` | Limpa fila de reprodução | `/limpar_fila` |
| `/teste` | Verifica conexão do bot | `/teste` |
| `/soma` | Calculadora simples | `/soma num1:<float> num2:<float>` |
| `/perfil` | Exibe avatar de membro | `/perfil membro:<@usuario>` |
| `/d` | Rola dados padrão | `/d lados:<2\|4\|6\|8\|10\|12\|20\|100> quantidade:<1-100>` |
| `/dado_custom` | Rola dados customizados | `/dado_custom lados:<2-1000> quantidade:<1-100>` |

## 🔧 Arquitetura Técnica

### Tecnologias Utilizadas
- **discord.py** - Framework principal para integração com Discord
- **yt-dlp** - Extrator robusto de metadados e URLs do YouTube
- **FFmpeg** - Processamento e streaming de áudio em tempo real
- **asyncio** - Programação assíncrona para máxima performance
- **python-dotenv** - Gerenciamento seguro de variáveis de ambiente

### Design Patterns
- **Async/Await** - Operações não-bloqueantes para responsividade
- **Command Tree** - Slash commands modernos com auto-completar
- **Error Handling** - Validações em cascata e mensagens de erro descritivas
- **Resource Management** - Cleanup automático e gestão eficiente de conexões

## 📋 Pré-requisitos

- Python 3.8+
- Discord.py 2.0+
- FFmpeg (incluído em `/bin/ffmpeg/`)
- Token do Discord Bot

## 🚀 Instalação Rápida

1. **Clone ou baixe o repositório**
   ```bash
   cd CabaBot
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o token**
   
   Crie um arquivo `.env` na raiz do projeto:
   ```env
   TOKEN=seu_token_aqui
   ```

4. **Execute o bot**
   ```bash
   python CabaBot.py
   ```

## 📦 Estrutura do Projeto

```
📦 CabaBot/
 ┣ 📂 bin/
 ┃ ┗ 📂 ffmpeg/          # FFmpeg executáveis para processamento de áudio
 ┃   ┣ 📜 ffmpeg.exe
 ┃   ┣ 📜 ffplay.exe
 ┃   ┗ 📜 ffprobe.exe
 ┣ 📂 __pycache__/       # Cache compilado de Python (ignorado)
 ┣ 📜 CabaBot.py         # Arquivo principal do bot
 ┣ 📜 README.md          # Documentação do projeto
 ┣ 📜 .env               # Variáveis de ambiente (token do bot)
 ┣ 📜 .gitignore         # Configuração do Git
 ┗ 📜 .gitattributes     # Atributos do Git

```

### Arquivos Principais

| Arquivo | Descrição |
|---------|-----------|
| `CabaBot.py` | Script principal com todos os comandos e funcionalidades |
| `.env` | Arquivo de configuração (contém o TOKEN do Discord) |
| `bin/ffmpeg/` | Binários do FFmpeg para processamento de áudio |
| `README.md` | Documentação completa do projeto |

## 🔐 Segurança

- **Token Protection** - Token apenas exibido por comprimento, nunca em logs
- **Ephemeral Messages** - Comandos sensíveis usam respostas privadas
- **Input Validation** - Validação em cascata de guild, member, e voice channel
- **Error Isolation** - Exceções capturadas e tratadas graciosamente

## 💡 Destaques da Implementação

✅ **Busca Inteligente** - Trata URLs completas e termos de busca automaticamente  
✅ **Async I/O** - Operações YouTube rodando em thread separada sem bloquear  
✅ **Tratamento de Erros** - YouTube block detection com mensagens amigáveis  
✅ **Mensagens Formatadas** - Embeds customizados e emojis descritivos  
✅ **Código Documentado** - Docstrings em todas as funções e classes  
✅ **Gerenciamento de Estado** - Filas por servidor (guild) para escalabilidade  

## 📝 Exemplos de Uso

### Reproduzir música por URL
```
/musica url:https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### Reproduzir música por nome
```
/musica url:Never Gonna Give You Up
```

### Criar timer de 5 minutos com música
```
/timer segundos:300 url:Alarm Clock
```

### Rolar um dado padrão
```
/d lados:20
/d lados:6 quantidade:3
```

### Rolar um dado customizado
```
/dado_custom lados:50
/dado_custom lados:100 quantidade:5
```

## 🐛 Troubleshooting

**"YouTube bloqueou a extração"**
- O YouTube pode bloquear yt-dlp periodicamente
- Solução: Atualize o yt-dlp (`pip install --upgrade yt-dlp`)

**Bot não conecta ao canal de voz**
- Verifique permissões: "Connect" e "Speak" ativadas
- Certifique-se de estar em um canal de voz válido

**Áudio com lag/stuttering**
- Reduz FFmpeg reconnect delay
- Verifica qualidade da conexão de internet

## 🎯 Roadmap Futuro

- [ ] Suporte a playlists do YouTube
- [ ] Sistema de volume adjustável
- [ ] Cache de músicas já tocadas
- [ ] Estatísticas de uso por servidor
- [ ] Comando de lyrics integrado

## 📄 Licença

Este projeto é fornecido como está para fins educacionais e de uso pessoal.

## 👋 Contato

Para reportar bugs ou sugerir features, abra uma issue no repositório.

---

**Desenvolvido com ☕ e ❤️** - CabaBot Team 2025
