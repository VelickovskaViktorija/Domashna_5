# Прва фаза: Подготовка на Java
FROM openjdk:11-jre-slim as java

# Втора фаза: Подготовка на Python
FROM python:3.10-slim-bookworm

WORKDIR /app

# Копирај Java од првата фаза
COPY --from=java /usr/local/openjdk-11 /usr/local/openjdk-11
ENV JAVA_HOME=/usr/local/openjdk-11
ENV PATH="$JAVA_HOME/bin:$PATH"

# Инсталирај ги потребните системски библиотеки
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    wget \
    gnupg \
    procps \
    && rm -rf /var/lib/apt/lists/*


# Копирај ги requirements.txt и инсталирај ги пакетите
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Копирај го остатокот од апликацијата
COPY . .

# Стандардна команда (може да се промени во docker-compose.yml)
CMD ["python", "data_ingestion.py"]