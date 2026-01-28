# 🎵 Guia de Uso - CabaBot

## 🎶 Comandos de Música

### `/musica`
Toca uma música do YouTube.
**Exemplos:**
- `/musica url:https://www.youtube.com/watch?v=...`
- `/musica url:Nome da Música` (Busca automática)
- `/musica url:https://www.youtube.com/playlist?list=...` (Toca playlist)

### Controles de Reprodução
- `/pausar` - Pausa a música atual.
- `/retomar` - Continua a música pausada.
- `/pular` - Vai para a próxima música da fila.
- `/parar` - Para a música e limpa a fila.
- `/limpar_fila` - Remove todas as músicas da fila sem parar a atual.
- `/agora` - Mostra detalhes da música tocando no momento.
- `/fila` - Exibe a lista de próximas músicas.
- `/loop` - Repete a música atual.
- `/loop_fila` - Repete a fila inteira.

### `/timer`
Define um temporizador que toca uma música ao final.
**Exemplo:**
- `/timer segundos:300 url:Alarm Sound` (Toca em 5 minutos)

### `/startup_audio`
Configura se o bot deve tocar um som ao iniciar.
- `/startup_audio enabled:true`

---

## 🛠️ Utilitários

### `/ping`
Testa se o bot está online e respondendo.

### `/soma`
Calculadora simples.
**Exemplo:** `/soma num1:10 num2:5` -> 15

### `/perfil`
Mostra o avatar de um usuário em tamanho grande.
**Exemplo:** `/perfil membro:@Usuario`