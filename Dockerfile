# Usando uma imagem leve do Python
FROM python:3.11-slim

# Instala o Git dentro do container (essencial para o agente Git)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Define a pasta de trabalho interna do container
WORKDIR /app

# Instala o CrewAI e as bibliotecas necessárias, incluindo o GitPython
RUN pip install --no-cache-dir crewai crewai-tools google-genai GitPython

# Copia o nosso código para dentro do container
COPY app.py .

# Comando padrão ao iniciar o container
CMD ["python", "app.py"]