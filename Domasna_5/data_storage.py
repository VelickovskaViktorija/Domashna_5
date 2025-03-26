
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import psycopg2
import json
from kafka import KafkaConsumer

# Kafka consumer setup
consumer = KafkaConsumer(
    'stock_data',  # Името на topic-от
    bootstrap_servers='kafka:9092',  # Адреса на Kafka брокерот
    auto_offset_reset='earliest',  # Почни од почеток на topic-от
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))  # Декодирај ги пораките како JSON
)

# Cassandra connection setup
def connect_to_cassandra():
    cluster = Cluster(['cassandra'], port=9042)
    session = cluster.connect()
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS stock_data
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
    """)
    session.set_keyspace('stock_data')
    session.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            symbol text,
            timestamp text,
            open float,
            high float,
            low float,
            close float,
            volume float,
            PRIMARY KEY (symbol, timestamp)
        );
    """)
    return session

# PostgreSQL connection setup
def connect_to_postgres():
    conn = psycopg2.connect(
        dbname="stock_data",
        user="postgres",
        password="postgres",
        host="postgres",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            symbol TEXT,
            timestamp TIMESTAMP,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume FLOAT,
            PRIMARY KEY (symbol, timestamp)
        );
    """)
    conn.commit()
    return conn, cur

# Читај ги пораките од Kafka и складирај ги во Cassandra и PostgreSQL
def store_data():
    cassandra_session = connect_to_cassandra()
    postgres_conn, postgres_cur = connect_to_postgres()

    for message in consumer:
        data = message.value
        symbol = data['Meta Data']['2. Symbol']
        time_series = data['Time Series (5min)']

        for timestamp, values in time_series.items():
            # Cassandra
            cassandra_session.execute("""
                INSERT INTO stock_prices (symbol, timestamp, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (symbol, timestamp, float(values['1. open']), float(values['2. high']),
                  float(values['3. low']), float(values['4. close']), float(values['5. volume'])))

            # PostgreSQL
            postgres_cur.execute("""
                INSERT INTO stock_prices (symbol, timestamp, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, timestamp) DO NOTHING;
            """, (symbol, timestamp, float(values['1. open']), float(values['2. high']),
                  float(values['3. low']), float(values['4. close']), float(values['5. volume'])))
            postgres_conn.commit()

if __name__ == "__main__":
    store_data()