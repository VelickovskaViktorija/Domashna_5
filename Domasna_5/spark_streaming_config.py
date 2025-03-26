# Конфигурација за Spark
SPARK_CONFIG = {
    "spark.master": "local[*]",
    "spark.app.name": "RealTimeStockDataProcessing",
    "spark.jars.packages": "org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0"
}

# Конфигурација за Cassandra
CASSANDRA_CONFIG = {
    "spark.cassandra.connection.host": "cassandra",
    "spark.cassandra.connection.port": "9042",
    "spark.cassandra.auth.username": "cassandra",
    "spark.cassandra.auth.password": "cassandra"
}

# Конфигурација за PostgreSQL
POSTGRES_CONFIG = {
    "url": "jdbc:postgresql://postgres:5432/stock_data",
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}