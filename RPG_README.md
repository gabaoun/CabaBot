Olá! Criei um **sistema RPG completo e modular** para seu bot Discord!

## 🎮 O que foi implementado?

Um sistema de RPG de Mesa integrado ao Discord onde seus amigos podem:

### ✅ Sistema de Personagem
- **4 Classes Base:** Guerreiro, Arqueiro, Mago, Druida
- **5 Atributos:** Força, Destreza, Inteligência, Sabedoria, Carisma
- **Sistema de Progressão:** Níveis (1-20), XP, HP escalável
- **Inventário & Equipamentos:** Armas, armaduras, acessórios

### ✅ Sistema de Eventos
- **12 Eventos Padrão:** Com diferentes dificuldades e tipos
- **Testes de Atributos Automáticos:** Baseado nos atributos do personagem
- **Recompensas:** XP e Ouro aleatórios
- **Sistema Modular:** Fácil adicionar novos eventos

### ✅ Sistema de NPCs
- **7 NPCs Padrão:** Goblins, Orcs, Trolls, Mercadores, etc.
- **3 Tipos de Interação:** Atacar, Conversar, Fugir
- **Loot System:** NPCs deixam dinheiro e itens
- **Níveis Variados:** Diferentes desafios

### ✅ Persistência de Dados
- **JSON Storage:** Todos os personagens salvos em `rpg_data/characters.json`
- **Carregamento Automático:** Restaura personagem ao iniciar
- **Fácil Backup:** Arquivo único e fácil de copiar

## 📂 Arquivos Criados

```
CabaBot/
├── rpg_system/                    # Sistema RPG (modular e extensível)
│   ├── __init__.py               # Importações
│   ├── attributes.py             # Atributos e modificadores
│   ├── classes.py                # 4 Classes base + framework
│   ├── character.py              # Personagem e repositório
│   ├── inventory.py              # Inventário, equipamentos, itens
│   ├── events.py                 # 12 Eventos + framework
│   └── npcs.py                   # 7 NPCs padrão + framework
│
├── rpg_commands.py               # Comandos básicos do RPG
├── rpg_events_commands.py        # Comandos de eventos e encontros
│
├── RPG_QUICKSTART.md             # Guia rápido para começar
├── RPG_DOCUMENTATION.md          # Documentação completa
├── RPG_EXPANSION_EXAMPLES.md     # Exemplos prontos para copiar
│
├── rpg_data/                      # Pasta de dados (criada auto)
│   └── characters.json           # Personagens salvos
│
└── CabaBot.py                    # Bot atualizado com RPG integrado
```

## 🚀 Como Usar

### 1. **Criar um Personagem**
```
/rpg criar nome:"Conan" classe:"Guerreiro"
```

### 2. **Alocar Atributos**
```
/rpg atributos forca:15 destreza:14 inteligencia:12 sabedoria:13 carisma:11
```

### 3. **Ver Perfil**
```
/rpg perfil
```

### 4. **Disparar um Evento**
```
/evento aleatorio
```
Todos podem participar clicando em "Participar"!

### 5. **Encontrar um NPC**
```
/evento encontro
```
Escolha: Atacar, Conversar ou Fugir!

## 🎯 Exemplos de Extensão

Tudo foi projetado para ser **fácil de expandir**:

### ➕ Adicionar Nova Classe
Veja `RPG_EXPANSION_EXAMPLES.md` - tem exemplo de Paladino e Bardo prontos!

### ➕ Adicionar Novo Evento
Simples como adicionar um objeto `Event` à lista!

### ➕ Adicionar Novo NPC
Crie um `NPC`, adicione itens ao inventário, e pronto!

## 🎲 Sistema de Mecânicas

### Modificadores
```
Mod = (Atributo - 10) / 2

Exemplo:
- Força 15 → +2 de bônus
- Destreza 8 → -1 de bônus
```

### Testes de Atributo
Quando um evento requer teste:
```
D20 + Modificador >= CD (Classe de Dificuldade)
```

### Progressão
```
Nível 1: 0 XP
Nível 2: 1000 XP requeridos
Nível 3: 2000 XP requeridos
... (cada nível = nível * 1000 XP)
```

## 💡 Recursos Únicos

1. **Sistema Modular:** Adicione classes, eventos e NPCs sem alterar código core
2. **Persistência:** Tudo é salvo em JSON fácil de ver/editar
3. **Testes Interativos:** Múltiplos usuários participam simultaneamente
4. **Modificadores Automáticos:** Calculados dinamicamente
5. **Sistema de Cooldown:** Habilidades têm espera apropriada
6. **Raridade de Itens:** comum, incomum, raro, muito_raro, lendário
7. **Views Discord:** Botões bonitos para interação

## 📊 Estatísticas

- **Classes:** 4 base (fácil adicionar mais)
- **Eventos:** 12 padrão (framework para infinitos)
- **NPCs:** 7 padrão (gerador modular)
- **Atributos:** 5 principais
- **Habilidades:** 3-4 por classe
- **Slots de Equipamento:** 6 (mão principal, secundária, armadura, cabeça, pés, acessório)

## 🔧 Tecnologia

- **Python 3.11+**
- **discord.py 2.x**
- **JSON para persistência**
- **Type hints** para melhor IDE support
- **Dataclasses** para estruturas limpas
- **Enums** para tipos seguros

## 📚 Documentação

- **RPG_QUICKSTART.md** - Começa aqui!
- **RPG_DOCUMENTATION.md** - Guia completo com todas as funcionalidades
- **RPG_EXPANSION_EXAMPLES.md** - Exemplos prontos para copiar

## 🎮 Próximas Ideias para Expansão

- [ ] Sistema de loja (comprar/vender itens)
- [ ] Quests/Missões persistentes
- [ ] Clãs/Guildas com rankings
- [ ] Leaderboard mensal
- [ ] Sistema de Skills/Perícias
- [ ] Crafting e Alquimia
- [ ] Dungeons instanciados
- [ ] PvP com árbitro
- [ ] Magia customizável
- [ ] Companheiros/Pets

## ⚡ Quick Commands

| Comando | Descrição |
|---------|-----------|
| `/rpg criar` | Novo personagem |
| `/rpg perfil` | Ver seu perfil |
| `/rpg atributos` | Alocar pontos |
| `/rpg descansar` | Recuperar HP/Mana |
| `/rpg classes` | Listar classes |
| `/rpg deletar` | Deletar personagem |
| `/evento aleatorio` | Evento aleatório |
| `/evento encontro` | Encontrar NPC |
| `/evento listar` | Listar eventos |

## 🎨 Design Pattern

O sistema usa:
- **Repository Pattern:** Para persistência
- **Factory Pattern:** Para criar classes/eventos/NPCs
- **Strategy Pattern:** Para diferentes tipos de eventos
- **Builder Pattern:** Para personagens complexos

## ✨ Highlights

✅ **Totalmente Modular** - Adicione conteúdo sem alterar código core  
✅ **Type-Safe** - Type hints em tudo  
✅ **Bem Documentado** - 3 docs + exemplos  
✅ **Fácil Expandir** - Estrutura pronta para crescer  
✅ **Persistente** - Dados salvos automaticamente  
✅ **Interativo** - Botões Discord bonitos  
✅ **Balanceado** - Modificadores sensatos  
✅ **Extensível** - 12 eventos + 7 NPCs + 4 classes + infinitas possibilidades  

---

## 🎯 Próximos Passos

1. **Testar os comandos básicos** - Crie um personagem e explore!
2. **Disparar um evento** - Veja como funciona a interação
3. **Personalizar** - Use `RPG_EXPANSION_EXAMPLES.md` para adicionar conteúdo
4. **Expandir** - Adicione suas próprias classes, eventos e NPCs!

Divirta-se com seus amigos! 🎲✨

---

**Criado com ❤️ para CabaBot**  
Um sistema RPG completo, modular e facilmente expansível para Discord!
