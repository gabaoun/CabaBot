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

### � Sistema de Rolagem de Dados
- **Rolador de dados padrão** - d2, d4, d6, d8, d10, d12, d20, d100 com interface de escolha rápida
- **Dados customizados** - Suporta qualquer número de lados (2-1000) e quantidade de dados
- **Modificadores** - Adicione bônus/penalidades aos resultados
- **Detalhamento** - Mostra dados individuais, subtotais e totais em embeds formatados

### 🎭 Sistema Modular de Testes de Atributos
- **Testes participativos** - Múltiplos usuários podem rolar para o mesmo teste
- **Classe de Dificuldade (CD)** - Sistema de sucesso/falha baseado em CD
- **Ranking em tempo real** - Resultados atualizados automaticamente com botão de participação
- **Arquitetura modular** - Fácil expansão para novos tipos de testes
- **Botões interativos** - Interface amigável com buttons do Discord

### �🎮 Comandos Disponíveis

| Comando | Descrição | Uso |
|---------|-----------|-----|
| `/musica` | Reproduz música do YouTube | `/musica url:<URL ou termo de busca>` |
| `/timer` | Timer com toque musical | `/timer segundos:<int> url:<URL>` |
| `/parar` | Para a reprodução | `/parar` |
| `/pausar` | Pausa a música | `/pausar` |
| `/retomar` | Retoma a música pausada | `/retomar` |
| `/pular` | Pula para próxima música | `/pular` |
| `/limpar_fila` | Limpa fila de reprodução | `/limpar_fila` |
| `/ping` | Verifica conexão do bot | `/ping` |
| `/soma` | Calculadora simples | `/soma num1:<float> num2:<float>` |
| `/perfil` | Exibe avatar de membro | `/perfil membro:<@usuario>` |
| `/d` | Rola dados padrão | `/d lados:<2\|4\|6\|8\|10\|12\|20\|100> quantidade:<1-100>` |
| `/dado_custom` | Rola dados customizados | `/dado_custom dado:<d20,3d6,etc> modificador:<int>` |
| `/teste_atributo` | Inicia teste de atributo | `/teste_atributo tipo:<nome> cd:<int> dado:<d20>` |

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
- **OOP Modular** - Classes `DiceRoller`, `TestConfig`, `RollButton`, `RollView` para fácil extensão
- **UI Components** - Buttons e Views interativas para experiência do usuário aprimorada

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
/dado_custom dado:d20
/dado_custom dado:3d6 modificador:2
/dado_custom dado:2d10 modificador:-1
```

### Iniciar um teste de atributo
```
/teste_atributo tipo:Destreza cd:12 dado:d20
/teste_atributo tipo:Força cd:15 dado:d20
/teste_atributo tipo:Inteligência cd:10 dado:d20
```
Após executar, clique no botão 🎲 Rolar para participar do teste. O ranking atualiza automaticamente!
## 📚 Documentação Adicional

Este projeto inclui documentação completa para ajudar você a aproveitar ao máximo:

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Guia completo de uso com exemplos práticos
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guia para desenvolvedores, arquitetura e extensões
- **[CHANGELOG.md](CHANGELOG.md)** - Histórico de versões e mudanças
- **[TECH_CHANGES.md](TECH_CHANGES.md)** - Detalhes técnicos das mudanças na versão 1.2.0
## �️ Extensibilidade e Arquitetura Modular

O CabaBot foi projetado com foco em extensibilidade. O sistema de testes de atributos utiliza uma arquitetura modular que permite adicionar novos tipos de testes facilmente.

### Classes Principais

#### `DiceRoller`
Responsável por parsear e rolar dados. Suporta qualquer formato válido (d20, 3d6, 2d10, etc).

```python
roller = DiceRoller("3d6")
roller.rolar()
print(roller.total)  # Soma dos três dados
print(roller.resultados)  # Lista [2, 5, 1]
```

#### `TestConfig`
Configuração modular para testes. Armazena participantes e resultados.

```python
test = TestConfig(
    tipo="Destreza",
    cd=12,
    dado_str="d20",
    descricao="Teste de reflexo"
)
test.adicionar_resultado(user_id=123, nome="Jogador", resultado=18)
```

#### `RollButton` e `RollView`
Componentes de UI interativa. Fáceis de estender com novas funcionalidades.

### Como Adicionar Novos Testes

1. Estenda `TestConfig` para adicionar lógica customizada
2. Crie um novo `RollButton` se precisar de comportamento diferente
3. Adicione um novo comando slash que instancia essas classes

## �🐛 Troubleshooting

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
