# Используем официальный образ Python
FROM python:3.11

# Устанавливаем зависимости
RUN pip install aiohttp

# Копируем клиентский скрипт в контейнер
COPY client.py /app/client.py

# Устанавливаем рабочую директорию
WORKDIR /app

# Команда для запуска клиента
CMD ["python", "client.py"]
