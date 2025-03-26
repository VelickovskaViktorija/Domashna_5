# Domashna_5

Домашна бр. 5

Детален преглед на секој сервис, со спецификации за тоа што прави и кои технологии ги имам користено.
________________________________________
1. Data Ingestion Service
   
Содржина: [data_ingestion.py]

Улога:
•	Зема финансиски податоци од Alpha Vantage API (цени на акции)
•	Кешира податоци локално (stock_data_cache.json) 
•	Испраќа податоци до Kafka

Технологии:
•	requests - HTTP повици до API
•	kafka-python - Producer за Kafka
•	logging - Логирање на грешки и успеси

Влезови/Излези:
•	Влез: API клуч, симболи на акции (AAPL, MSFT, GOOGL)
•	Излез: JSON пораки во Kafka topic stock_data
________________________________________

2. Real-Time Processing Service
   
Содржина: [real_time_processing.py]

Улога:

•	Чита податоци од Kafka со Spark Streaming
•	Ги парсира JSON податоците и ги трансформира во табеларна форма
•	Врши основна валидација и обработка

Технологии:
•	PySpark (Spark Structured Streaming)
•	Apache Kafka интеграција
•	logging

Влезови/Излези:
•	Влез: Kafka topic stock_data
•	Излез: Трансформирани податоци во Spark DataFrame формат

________________________________________

3. Data Storage Service
   
Содржина: [data_storage.py]

Улога:
•	Чита податоци од Kafka
•	Ги зачувува во:
o	Cassandra (за брз пристап)
o	PostgreSQL (за структурирани анализи)

Технологии:
•	cassandra-driver - Cassandra клиент
•	psycopg2 - PostgreSQL клиент
•	kafka-python - Consumer

Влезови/Излези:
•	Влез: Kafka topic stock_data
•	Излез: Податоци во базите
________________________________________

4. Data Analysis Service
   
Содржина: [data_analysis.py]

Улога:
•	Врши анализа на податоците од Cassandra:
o	Пресметува дневни приноси (pct_change)
o	Генерира предвидувања со линеарна регресија (scikit-learn)
o	Создава визуелизации (matplotlib)

Технологии:
•	cassandra-driver - Читање податоци
•	pandas/scikit-learn - Анализа
•	matplotlib - Графикони

Влезови/Излези:
•	Влез: Податоци од Cassandra
•	Излез: price_prediction.png, статистики во конзола

________________________________________

5. Data Visualization Service
   
Содржина: [data_visualization.py]

Улога:
•	Прикажува интерактивни графикони преку Flask веб-интерфејс
•	Користи Plotly за визуелизација

Технологии:

•	Flask - Веб сервер
•	plotly/D3.js - Графикони
•	cassandra-driver - Читање податоци

Влезови/Излези:
•	Влез: Податоци од Cassandra
•	Излез: Веб страна на http://localhost:5000

________________________________________

6. Инфраструктура (Docker Compose)
   
Содржина: [docker-compose.yml]

Улога:
•	Дефинира мрежа (stock-network)
•	Стартува:
o	Zookeeper + Kafka
o	Cassandra + PostgreSQL
o	Сите Python сервиси

Технологии:
•	Docker контејнери
•	Библиотеки од bitnami (Kafka, Zookeeper)
________________________________________
Дијаграм на архитектурата
Alpha Vantage API → [Data Ingestion] → Kafka → [Real-Time Processing] → Spark
                     ↓                          ↓                          
                [Data Storage] ← Cassandra/PostgreSQL ← [Data Analysis] → Графикони
                     ↓
                [Data Visualization] → Flask/Plotly
                
Секој сервис е независен и комуницира преку:
•	Kafka (за поток од податоци)
•	Бази (Cassandra/PostgreSQL)
•	Docker мрежа (stock-network)


