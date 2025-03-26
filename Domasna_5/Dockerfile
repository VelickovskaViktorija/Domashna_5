
FROM openjdk:11-jre-slim as java


FROM python:3.10-slim-bookworm

WORKDIR /app


COPY --from=java /usr/local/openjdk-11 /usr/local/openjdk-11
ENV JAVA_HOME=/usr/local/openjdk-11
ENV PATH="$JAVA_HOME/bin:$PATH"


RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    wget \
    gnupg \
    procps \
    && rm -rf /var/lib/apt/lists/*



COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt



COPY . .

CMD ["python", "data_ingestion.py"]
