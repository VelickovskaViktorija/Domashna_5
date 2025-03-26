import time
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import os
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import WhiteListRoundRobinPolicy

# Почекај 60 секунди за Cassandra да се иницијализира
time.sleep(60)


# Cassandra connection setup
def connect_to_cassandra():
    # Дефинирај execution profile
    profile = ExecutionProfile(load_balancing_policy=WhiteListRoundRobinPolicy(['cassandra']))

    # Креирај кластер со execution profile
    cluster = Cluster(
        ['cassandra'],  # Адреса на Cassandra
        port=9042,  # Порт на Cassandra
        execution_profiles={EXEC_PROFILE_DEFAULT: profile}
    )
    session = cluster.connect('stock_data')  # Користи го keyspace-от 'stock_data'
    return session


# Земи ги податоците за акциите од Cassandra
def fetch_stock_data(session, symbol):
    query = f"SELECT timestamp, open, high, low, close, volume FROM stock_prices WHERE symbol = '{symbol}'"
    rows = session.execute(query)
    data = pd.DataFrame(rows)
    return data


# Анализа на податоците
def analyze_data(data):
    # Основна статистика
    print("Основна статистика:")
    print(data.describe())

    # Пресметај го дневниот просечен принос
    data['daily_return'] = data['close'].pct_change()
    print("\nДневен просечен принос:")
    print(data['daily_return'].mean())

    # Пресметај го движечкиот просек за последните 5 временски интервали
    data['moving_avg'] = data['close'].rolling(window=5).mean()
    print("\nДвижечки просек за последните 5 интервали:")
    print(data[['timestamp', 'close', 'moving_avg']].tail())


# Предвидување на идни цени користејќи линеарна регресија
def predict_prices(data):
    # Креирај ги карактеристиките (features) и целната променлива (target)
    data['timestamp_numeric'] = pd.to_datetime(data['timestamp']).astype(int) / 10 ** 9
    X = data[['timestamp_numeric']]
    y = data['close']

    # Подели ги податоците на тренинг и тест множество
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Обучи го моделот
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Предвиди ги цените
    predictions = model.predict(X_test)

    # Прикажи ги резултатите
    plt.figure(figsize=(10, 6))
    plt.scatter(X_test, y_test, color='blue', label='Вистински цени')
    plt.plot(X_test, predictions, color='red', label='Предвидени цени')
    plt.xlabel('Време (timestamp)')
    plt.ylabel('Цена (close)')
    plt.title(f'Предвидување на цени за акциите')
    plt.legend()

    # Зачувај го графиконот како слика во root folder-от
    output_dir = "/app"  # Патека до root folder-от во контејнерот
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Креирај директориум ако не постои
    output_path = os.path.join(output_dir, "price_prediction.png")
    plt.savefig(output_path)
    plt.close()  # Затвори го графиконот за да се ослободи меморија
    print(f"Графиконот е зачуван во: {output_path}")


# Главна функција
def main():
    session = connect_to_cassandra()
    symbol = 'AAPL'  # Можеш да го смениш симболот на друга акција

    while True:  # Бесконечна јамка за континуирано работење
        data = fetch_stock_data(session, symbol)

        # Анализа на податоците
        analyze_data(data)

        # Предвидување на идни цени
        predict_prices(data)

        time.sleep(3600)  # Чекај 1 час пред следната анализа


if __name__ == "__main__":
    main()