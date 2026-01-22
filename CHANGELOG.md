# Changelog - CabaBot

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.2.0] - 2026-01-22

### ✨ Adicionado
- **Sistema Modular de Testes de Atributos** 
  - Novo comando `/teste_atributo` para testes participativos
  - Classe `TestConfig` para configurações de testes extensíveis
  - Classe `DiceRoller` para parsing e rolagem de dados robusta
  - Classe `RollButton` com lógica interativa de buttons
  - Sistema de ranking em tempo real que atualiza automaticamente
  - Suporte a múltiplos participantes por teste
  - Classe de Dificuldade (CD) com cálculo de sucesso/falha

- **Melhorias no Sistema de Dados**
  - Comando `/d` agora mostra dados individuais quando quantidade > 1
  - Comando `/dado_custom` com suporte a modificadores
  - Novo comando `/dado_custom` aceita formato texto (ex: d20, 3d6)
  - Embeds formatados com cores e detalhamentos
  - Footer com nome de quem solicitou o comando

- **Arquitetura Modular para Futuras Expansões**
  - Classes bem estruturadas para fácil extensão
  - Separação clara de responsabilidades
  - Suporte a novos tipos de testes sem modificar código existente

### 🔄 Alterado
- Comando `/teste` renomeado para `/ping` para melhor clareza
- Versão atualizada de 1.1.0 para 1.2.0
- Imports expandidos para incluir `List` e `Tuple` do `typing`

### 📝 Documentação
- README atualizado com novas seções
- Adicionada seção "Extensibilidade e Arquitetura Modular"
- Exemplos de uso para todos os novos comandos
- Documentação de classes para facilitar extensões futuras

### 🏗️ Refatoração
- Sistema de dados consolidado em classe `DiceRoller`
- Dicionário global `active_tests` para rastreamento de testes
- Validações centralizadas em `DiceRoller._parse_dado()`

## [1.1.0] - 2026-01-22

### ✨ Adicionado
- Rolador de dados padrão (`/d`)
- Rolador de dados customizados (`/dado_custom`)
- Suporte a múltiplos dados em uma única rolagem

### 📝 Documentação
- README atualizado com novos comandos
- Versão incrementada

## [1.0.0] - Inicial

### ✨ Adicionado
- Reprodução de música do YouTube
- Sistema de timers com áudio
- Controles de reprodução (pausar, retomar, pular, parar)
- Gerenciamento de fila por servidor
- Comandos básicos (soma, perfil, teste)
- Sistema de startup audio configurável

---

**Nota sobre Versão 1.2.0:** Este lançamento marca um ponto de inflexão na arquitetura do bot. O sistema modular de testes estabelece um padrão reutilizável que pode ser estendido com novos tipos de testes, sistemas de desafio, ou mini-games sem necessidade de refatoração do código existente.
