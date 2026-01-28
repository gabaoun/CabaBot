# Usamos uma imagem Python leve (slim) para economizar espaço
FROM python:3.13-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema
# O FFmpeg é essencial para processamento de áudio
# git pode ser necessário para algumas dependências do pip
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia primeiro o requirements para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código para o container
COPY . .

# Comando para rodar o bot
CMD ["python", "CabaBot.py"]
