from kafka import KafkaConsumer
import json


consumer = KafkaConsumer(
    'stock_data',  
    bootstrap_servers='kafka:9092',  
    auto_offset_reset='earliest',  
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))) 


for message in consumer:
    print(f"Received message: {message.value}")

