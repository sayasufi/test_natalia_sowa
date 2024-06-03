# Используем официальный образ Python
FROM python:3.11

# Устанавливаем зависимости
RUN pip install aiohttp asyncpg pytest pytest-asyncio pytest-aiohttp

# Копируем серверный скрипт и тесты в контейнер
COPY server.py /app/server.py
COPY tests /app/tests

# Устанавливаем рабочую директорию
WORKDIR /app

# Настраиваем PYTHONPATH, чтобы тесты могли найти модуль server
ENV PYTHONPATH /app

# Запускаем тесты
RUN pytest --maxfail=1 --disable-warnings

# Команда для запуска сервера
CMD ["python", "server.py"]
