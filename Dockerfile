# Use uma imagem base do Python 3.11 slim
FROM python:3.11-slim

# Defina o diretório de trabalho
WORKDIR /usr/src/app

# Atualize o pip
RUN pip install --upgrade pip

# Copie o arquivo de requisitos e instale as dependências
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código da aplicação
COPY . .

# Exponha a porta 5000
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]