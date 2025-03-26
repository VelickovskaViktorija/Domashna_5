from kafka import KafkaConsumer
import json

# Kafka consumer setup
consumer = KafkaConsumer(
    'stock_data',  # Името на topic-от
    bootstrap_servers='kafka:9092',  # Адреса на Kafka брокерот
    auto_offset_reset='earliest',  # Почни од почеток на topic-от
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))) # Декодирај ги пораките како JSON

# Читај ги пораките од Kafka
for message in consumer:
    print(f"Received message: {message.value}")

