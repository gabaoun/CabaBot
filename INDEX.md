# 📚 Índice de Documentação - CabaBot v1.2.0

Bem-vindo! Este arquivo ajuda a navegar pela documentação completa do CabaBot.

## 🎯 Começar Rápido

**Novo no CabaBot?** Comece aqui:
1. Leia [README.md](README.md) - Overview geral
2. Veja [USAGE_GUIDE.md](USAGE_GUIDE.md#1️⃣-rolador-de-dados-padrão-d) - Exemplos práticos

---

## 📖 Documentação por Tipo

### Para Usuários 👤

| Documento | Descrição | Tempo de Leitura |
|---|---|---|
| [README.md](README.md) | Visão geral, características, instalação | 5 min |
| [USAGE_GUIDE.md](USAGE_GUIDE.md) | Guia completo com exemplos de cada comando | 15 min |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Resumo do que mudou e como usar | 10 min |

**Onde encontrar:**
- Como usar `/d`? → [USAGE_GUIDE.md - Seção 1](USAGE_GUIDE.md#1️⃣-rolador-de-dados-padrão-d)
- Como usar `/dado_custom`? → [USAGE_GUIDE.md - Seção 2](USAGE_GUIDE.md#2️⃣-rolador-de-dados-customizado-dado_custom)
- Como usar `/teste_atributo`? → [USAGE_GUIDE.md - Seção 3](USAGE_GUIDE.md#3️⃣-testes-de-atributo-teste_atributo-⭐-novo)

---

### Para Desenvolvedores 👨‍💻

| Documento | Descrição | Tempo de Leitura |
|---|---|---|
| [DEVELOPMENT.md](DEVELOPMENT.md) | Arquitetura, classes, como estender | 20 min |
| [TECH_CHANGES.md](TECH_CHANGES.md) | Mudanças técnicas versão 1.2.0 | 10 min |
| [CHANGELOG.md](CHANGELOG.md) | Histórico completo de versões | 5 min |

**Onde encontrar:**
- Como a arquitetura funciona? → [DEVELOPMENT.md - Estrutura de Classes](DEVELOPMENT.md#estrutura-de-classes)
- Como adicionar novo teste? → [DEVELOPMENT.md - Como Adicionar](DEVELOPMENT.md#como-adicionar-novos-tipos-de-testes)
- Quais mudanças técnicas? → [TECH_CHANGES.md](TECH_CHANGES.md)

---

### Para Gerentes/Product 📊

| Documento | Descrição |
|---|---|
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | O que foi entregue e status |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de versões |

---

## 🔍 Encontrar por Tópico

### Rolagem de Dados
- Como usar `/d`? → [USAGE_GUIDE.md#1️⃣](USAGE_GUIDE.md#1️⃣-rolador-de-dados-padrão-d)
- Como usar `/dado_custom`? → [USAGE_GUIDE.md#2️⃣](USAGE_GUIDE.md#2️⃣-rolador-de-dados-customizado-dado_custom)
- Dados individuais e modificadores? → [USAGE_GUIDE.md#📊-entendendo-os-resultados](USAGE_GUIDE.md#📊-entendendo-os-resultados)
- Implementação técnica? → [DEVELOPMENT.md - DiceRoller](DEVELOPMENT.md#diceroller)

### Testes de Atributo
- Como funciona? → [USAGE_GUIDE.md#3️⃣](USAGE_GUIDE.md#3️⃣-testes-de-atributo-teste_atributo-⭐-novo)
- Casos de uso RPG? → [USAGE_GUIDE.md#🎯-caso-de-uso-rpg-com-amigos](USAGE_GUIDE.md#🎯-caso-de-uso-rpg-com-amigos)
- Implementação técnica? → [DEVELOPMENT.md - TestConfig](DEVELOPMENT.md#testconfig)
- Como estender? → [DEVELOPMENT.md - Como Adicionar Novos Testes](DEVELOPMENT.md#como-adicionar-novos-tipos-de-testes)

### Arquitetura
- Visão geral? → [TECH_CHANGES.md - Sistema em 4 Camadas](TECH_CHANGES.md#arquitetura-em-4-camadas)
- Classes principais? → [DEVELOPMENT.md - Estrutura de Classes](DEVELOPMENT.md#estrutura-de-classes)
- Extensibilidade? → [DEVELOPMENT.md](DEVELOPMENT.md)

### FAQ
- Perguntas frequentes? → [USAGE_GUIDE.md#-perguntas-frequentes](USAGE_GUIDE.md#-perguntas-frequentes)

---

## 📊 Estrutura de Arquivos

```
CabaBot/
├── CabaBot.py                    ← Arquivo principal
├── README.md                      ← Documentação geral
├── USAGE_GUIDE.md                ← Guia de uso (para usuários)
├── DEVELOPMENT.md                ← Guia de desenvolvimento (para devs)
├── IMPLEMENTATION_SUMMARY.md     ← Resumo das mudanças
├── TECH_CHANGES.md               ← Detalhes técnicos (para devs)
├── CHANGELOG.md                  ← Histórico de versões
├── INDEX.md                       ← Este arquivo
└── bin/
    └── ffmpeg/                    ← Executáveis FFmpeg
```

---

## 🚀 Roadmap Futuro

### Próximas Versões (Planejadas)

**v1.3.0** - Melhorias de Testes
- Vantagem/Desvantagem (rolar 2d20)
- Críticos automáticos
- Testes combinados

**v1.4.0** - Persistência
- Salvar resultados em banco de dados
- Histórico de testes

**v2.0.0** - Sistema de Desafios
- Testes PvP
- Ranking global
- Achievements

---

## 💡 Dicas de Leitura

### Se você tem 5 minutos
→ Leia [README.md - Características Principais](README.md#-características-principais)

### Se você tem 15 minutos
→ Leia [README.md](README.md) + [USAGE_GUIDE.md - Primeiros 3 Exemplos](USAGE_GUIDE.md#exemplos)

### Se você quer entender tudo
→ Leia todos os arquivos em ordem:
1. README.md
2. USAGE_GUIDE.md
3. IMPLEMENTATION_SUMMARY.md
4. TECH_CHANGES.md
5. DEVELOPMENT.md
6. CHANGELOG.md

### Se você quer estender o código
→ Leia:
1. [DEVELOPMENT.md - Estrutura de Classes](DEVELOPMENT.md#estrutura-de-classes)
2. [DEVELOPMENT.md - Como Adicionar](DEVELOPMENT.md#como-adicionar-novos-tipos-de-testes)
3. [TECH_CHANGES.md - Modularidade](TECH_CHANGES.md#modularidade)

---

## ❓ Não encontrou o que procurava?

### Procure por:

1. **Palavra-chave no browser** (Ctrl+F)
   - Exemplo: "como participar de um teste?"
   
2. **Números/Símbolos:**
   - `/d` → Busque "rolar" em USAGE_GUIDE.md
   - `DiceRoller` → Busque em DEVELOPMENT.md

3. **Conceitos:**
   - "Ranking" → Procure em USAGE_GUIDE.md seção 3
   - "Extensão" → Procure em DEVELOPMENT.md
   - "Mudanças" → Procure em CHANGELOG.md

---

## 📞 Versão e Data

- **Versão:** 1.2.0
- **Data:** 22 de Janeiro de 2026
- **Autor:** CabaBot Team

---

**Boa leitura! 📚✨**
