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
📦BotDiscordOsCaba
 ┗ 📂CabaBot
 ┃ ┣ 📂.git
 ┃ ┃ ┣ 📂hooks
 ┃ ┃ ┃ ┣ 📜applypatch-msg.sample
 ┃ ┃ ┃ ┣ 📜commit-msg.sample
 ┃ ┃ ┃ ┣ 📜fsmonitor-watchman.sample
 ┃ ┃ ┃ ┣ 📜post-update.sample
 ┃ ┃ ┃ ┣ 📜pre-applypatch.sample
 ┃ ┃ ┃ ┣ 📜pre-commit.sample
 ┃ ┃ ┃ ┣ 📜pre-merge-commit.sample
 ┃ ┃ ┃ ┣ 📜pre-push.sample
 ┃ ┃ ┃ ┣ 📜pre-rebase.sample
 ┃ ┃ ┃ ┣ 📜pre-receive.sample
 ┃ ┃ ┃ ┣ 📜prepare-commit-msg.sample
 ┃ ┃ ┃ ┣ 📜push-to-checkout.sample
 ┃ ┃ ┃ ┣ 📜sendemail-validate.sample
 ┃ ┃ ┃ ┗ 📜update.sample
 ┃ ┃ ┣ 📂info
 ┃ ┃ ┃ ┗ 📜exclude
 ┃ ┃ ┣ 📂logs
 ┃ ┃ ┃ ┣ 📂refs
 ┃ ┃ ┃ ┃ ┣ 📂heads
 ┃ ┃ ┃ ┃ ┃ ┗ 📜main
 ┃ ┃ ┃ ┃ ┗ 📂remotes
 ┃ ┃ ┃ ┃ ┃ ┗ 📂origin
 ┃ ┃ ┃ ┃ ┃ ┃ ┣ 📜HEAD
 ┃ ┃ ┃ ┃ ┃ ┃ ┗ 📜main
 ┃ ┃ ┃ ┗ 📜HEAD
 ┃ ┃ ┣ 📂objects
 ┃ ┃ ┃ ┣ 📂0f
 ┃ ┃ ┃ ┃ ┗ 📜5fc2b66971009fc62c7270a268d617bd8fe664
 ┃ ┃ ┃ ┣ 📂10
 ┃ ┃ ┃ ┃ ┗ 📜cee37c6f07e2c350229da580d012b458bc9281
 ┃ ┃ ┃ ┣ 📂12
 ┃ ┃ ┃ ┃ ┗ 📜50a5e2741e0151910dce780dec73c5d175f816
 ┃ ┃ ┃ ┣ 📂1b
 ┃ ┃ ┃ ┃ ┗ 📜cd4c5aa945b3b4140695f62bf961aa8495ae99
 ┃ ┃ ┃ ┣ 📂1f
 ┃ ┃ ┃ ┃ ┗ 📜a2723d0a94fad8bfffc31b0f104f3377d6321e
 ┃ ┃ ┃ ┣ 📂2d
 ┃ ┃ ┃ ┃ ┗ 📜4dafb53f67fd04591ba18eaaf1db4e61f0ce91
 ┃ ┃ ┃ ┣ 📂35
 ┃ ┃ ┃ ┃ ┗ 📜f30015a68c48efaa15ff9763819d253f2c4d17
 ┃ ┃ ┃ ┣ 📂42
 ┃ ┃ ┃ ┃ ┗ 📜890e32f63cde5c813a56495e05855379caea7e
 ┃ ┃ ┃ ┣ 📂45
 ┃ ┃ ┃ ┃ ┗ 📜9f3287aebbb6c2caee5995eec3c407e8b511ab
 ┃ ┃ ┃ ┣ 📂4b
 ┃ ┃ ┃ ┃ ┗ 📜91652692a35ce54e467b0413f04bc87685c2df
 ┃ ┃ ┃ ┣ 📂4c
 ┃ ┃ ┃ ┃ ┗ 📜49bd78f1d08f2bc09fa0bd8191ed38b7dce5e3
 ┃ ┃ ┃ ┣ 📂6a
 ┃ ┃ ┃ ┃ ┗ 📜196994df354261738ce6f0dbf19dff2748c202
 ┃ ┃ ┃ ┣ 📂6f
 ┃ ┃ ┃ ┃ ┗ 📜46904cbd305c5152c18f204cbaadca9c6cb96b
 ┃ ┃ ┃ ┣ 📂72
 ┃ ┃ ┃ ┃ ┗ 📜db38abbc211d7d4256dc0e4da4474ae4ce4873
 ┃ ┃ ┃ ┣ 📂81
 ┃ ┃ ┃ ┃ ┗ 📜9bab7fab33a332651ddafd212bd5c907765193
 ┃ ┃ ┃ ┣ 📂83
 ┃ ┃ ┃ ┃ ┗ 📜86db4b7e3a95a8f3a8734af9a30eb748e21af3
 ┃ ┃ ┃ ┣ 📂96
 ┃ ┃ ┃ ┃ ┗ 📜a7a8498ef20e420f5a67fae661017b4aeb67fc
 ┃ ┃ ┃ ┣ 📂a8
 ┃ ┃ ┃ ┃ ┗ 📜1909bed273d68685fc23de9d9522748241fd5e
 ┃ ┃ ┃ ┣ 📂b2
 ┃ ┃ ┃ ┃ ┗ 📜7d0bebe7f5f299b62769b607dda53021e33bb6
 ┃ ┃ ┃ ┣ 📂cc
 ┃ ┃ ┃ ┃ ┗ 📜5d259ea246865d83710de9f4c72aa82332ed0a
 ┃ ┃ ┃ ┣ 📂d3
 ┃ ┃ ┃ ┃ ┣ 📜22787b0b219a779c7ea40cd4b9dcacbef8826b
 ┃ ┃ ┃ ┃ ┗ 📜f855ac221d99d80b91e07494e728687b2a4d79
 ┃ ┃ ┃ ┣ 📂d9
 ┃ ┃ ┃ ┃ ┗ 📜32244101971f8fe2a45578aec6a1c6352c5d63
 ┃ ┃ ┃ ┣ 📂df
 ┃ ┃ ┃ ┃ ┗ 📜e0770424b2a19faf507a501ebfc23be8f54e7b
 ┃ ┃ ┃ ┣ 📂ff
 ┃ ┃ ┃ ┃ ┗ 📜dbc07e117cbe138c59e6e675ccb75a3ac68e02
 ┃ ┃ ┃ ┣ 📂info
 ┃ ┃ ┃ ┗ 📂pack
 ┃ ┃ ┣ 📂refs
 ┃ ┃ ┃ ┣ 📂heads
 ┃ ┃ ┃ ┃ ┗ 📜main
 ┃ ┃ ┃ ┣ 📂remotes
 ┃ ┃ ┃ ┃ ┗ 📂origin
 ┃ ┃ ┃ ┃ ┃ ┣ 📜HEAD
 ┃ ┃ ┃ ┃ ┃ ┗ 📜main
 ┃ ┃ ┃ ┗ 📂tags
 ┃ ┃ ┣ 📜COMMIT_EDITMSG
 ┃ ┃ ┣ 📜config
 ┃ ┃ ┣ 📜description
 ┃ ┃ ┣ 📜FETCH_HEAD
 ┃ ┃ ┣ 📜HEAD
 ┃ ┃ ┣ 📜index
 ┃ ┃ ┗ 📜ORIG_HEAD
 ┃ ┣ 📂bin
 ┃ ┃ ┗ 📂ffmpeg
 ┃ ┃ ┃ ┣ 📜ffmpeg.exe
 ┃ ┃ ┃ ┣ 📜ffplay.exe
 ┃ ┃ ┃ ┗ 📜ffprobe.exe
 ┃ ┣ 📜.env
 ┃ ┣ 📜.gitattributes
 ┃ ┣ 📜.gitignore
 ┃ ┣ 📜CabaBot.py
 ┃ ┗ 📜README.md
```

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
