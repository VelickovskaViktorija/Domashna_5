from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode, when
from pyspark.sql.types import StructType, StructField, StringType, FloatType, MapType
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


schema = StructType([
    StructField("Meta Data", MapType(StringType(), StringType())),  
    StructField("Time Series (5min)", MapType(StringType(), StructType([  
        StructField("1. open", StringType()),
        StructField("2. high", StringType()),
        StructField("3. low", StringType()),
        StructField("4. close", StringType()),
        StructField("5. volume", StringType())
    ])))
])


def create_spark_session():
    return SparkSession.builder \
        .appName("RealTimeStockDataProcessing") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()


def process_batch(df, epoch_id):
    try:
        
        logging.info(f"Обработка на бач {epoch_id}...")
        df.show(truncate=False)

        
        for row in df.collect():
            stock_data = {
                "Meta Data": {"2. Symbol": row["symbol"]},
                "Time Series (5min)": {
                    row["timestamp"]: {
                        "1. open": row["open"],
                        "2. high": row["high"],
                        "3. low": row["low"],
                        "4. close": row["close"],
                        "5. volume": row["volume"]
                    }
                }
            }
            
            logging.info(f"Податоци за {row['symbol']} се подготвени за зачувување.")

    except Exception as e:
        logging.error(f"Грешка при обработка на бач {epoch_id}: {e}")

if __name__ == "__main__":
    
    spark = create_spark_session()
    logging.info("Spark сесијата е успешно креирана.")

   
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "stock_data") \
        .option("startingOffsets", "earliest") \
        .load()

    
    json_df = df.selectExpr("CAST(value AS STRING) as value")
    parsed_df = json_df.select(from_json(col("value"), schema).alias("data")).select("data.*")

  
    parsed_df.printSchema()

    
    exploded_df = parsed_df.select(
        when(col("Meta Data").isNotNull(), col("Meta Data").getItem("2. Symbol")).alias("symbol"),
        explode(col("Time Series (5min)")).alias("timestamp", "data")
    ).select(
        "symbol",
        "timestamp",
        col("data.`1. open`").cast(FloatType()).alias("open"),  
        col("data.`2. high`").cast(FloatType()).alias("high"),
        col("data.`3. low`").cast(FloatType()).alias("low"),
        col("data.`4. close`").cast(FloatType()).alias("close"),
        col("data.`5. volume`").cast(FloatType()).alias("volume")
    )

    
    query = exploded_df.writeStream \
        .outputMode("append") \
        .foreachBatch(process_batch) \
        .format("console") \
        .start()

    query.awaitTermination()

