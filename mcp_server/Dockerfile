FROM python:3.11-slim

WORKDIR /app

# Установим системные зависимости
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Копируем requirements, если есть
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true

# Установим FastAPI и uvicorn (и mcp[cli] если нужно)
RUN pip install fastapi uvicorn "mcp[cli]"

# Копируем код MCP сервера
COPY . .

EXPOSE 8003

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8003"]
