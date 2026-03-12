# Use uma imagem Python leve
FROM python:3.12-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema necessárias para algumas libs (psutil, etc)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Comando padrão (ajustado para rodar o master por padrão)
CMD ["python", "polymarket_master.py"]
