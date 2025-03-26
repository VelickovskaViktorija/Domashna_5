import os
import json
import time
import logging
import requests
from kafka import KafkaProducer

# Alpha Vantage API key
API_KEY = '9ZGQ97ICWQWEUW63'


CACHE_FILE = 'stock_data_cache.json'


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_kafka_producer():
    retries = 5
    while retries > 0:
        try:
            producer = KafkaProducer(
                bootstrap_servers='kafka:9092',
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            return producer
        except Exception as e:
            logging.error(f"Failed to connect to Kafka: {e}. Retrying in 5 minutes...")
            retries -= 1
            time.sleep(300)  
    raise Exception("Could not connect to Kafka after multiple retries.")

producer = create_kafka_producer()

def fetch_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}&outputsize=compact'
    response = requests.get(url)
    data = response.json()

    
    if "Information" in data and "rate limit" in data["Information"]:
        logging.warning(f"Достигнавте дневна граница на API повици за {symbol}. Ве молиме надградете на премиум план или почекајте до утре.")
        return None
    elif "Error Message" in data:
        logging.error(f"Грешка при земање на податоци за {symbol}: {data['Error Message']}")
        return None
    else:
        return data

def send_to_kafka(topic, data):
    try:
        
        print("Sending data to Kafka:")
        print(json.dumps(data, indent=4))  # Печатење на податоците во уреден формат
        producer.send(topic, value=data)
        producer.flush()
        logging.info(f"Податоците за {data['Meta Data']['2. Symbol']} се испратени до Kafka topic {topic}")
    except Exception as e:
        logging.error(f"Грешка при испраќање на податоци до Kafka: {e}")



def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

if __name__ == "__main__":
    symbols = ['AAPL', 'MSFT', 'GOOGL']  # Примерни симболи на акции
    topic = 'stock_data'
    cache = load_cache()

    while True:
        for symbol in symbols:
            if symbol in cache:
                logging.info(f"Користам кеширани податоци за {symbol}.")
                stock_data = cache[symbol]
            else:
                logging.info(f"Земам нови податоци за {symbol}...")
                stock_data = fetch_stock_data(symbol)
                if stock_data:
                    cache[symbol] = stock_data
                    save_cache(cache)

            if stock_data:
                send_to_kafka(topic, stock_data)
        time.sleep(3600)  
