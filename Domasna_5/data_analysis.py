import time
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import os
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import WhiteListRoundRobinPolicy

time.sleep(60)



def connect_to_cassandra():
   
    profile = ExecutionProfile(load_balancing_policy=WhiteListRoundRobinPolicy(['cassandra']))

    
    cluster = Cluster(
        ['cassandra'],  # Адреса на Cassandra
        port=9042,  # Порт на Cassandra
        execution_profiles={EXEC_PROFILE_DEFAULT: profile}
    )
    session = cluster.connect('stock_data')  # Користи го keyspace-от 'stock_data'
    return session



def fetch_stock_data(session, symbol):
    query = f"SELECT timestamp, open, high, low, close, volume FROM stock_prices WHERE symbol = '{symbol}'"
    rows = session.execute(query)
    data = pd.DataFrame(rows)
    return data



def analyze_data(data):
   
    print("Основна статистика:")
    print(data.describe())

    data['daily_return'] = data['close'].pct_change()
    print("\nДневен просечен принос:")
    print(data['daily_return'].mean())

    
    data['moving_avg'] = data['close'].rolling(window=5).mean()
    print("\nДвижечки просек за последните 5 интервали:")
    print(data[['timestamp', 'close', 'moving_avg']].tail())



def predict_prices(data):
   
    data['timestamp_numeric'] = pd.to_datetime(data['timestamp']).astype(int) / 10 ** 9
    X = data[['timestamp_numeric']]
    y = data['close']

    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    
    model = LinearRegression()
    model.fit(X_train, y_train)

    
    predictions = model.predict(X_test)

   
    plt.figure(figsize=(10, 6))
    plt.scatter(X_test, y_test, color='blue', label='Вистински цени')
    plt.plot(X_test, predictions, color='red', label='Предвидени цени')
    plt.xlabel('Време (timestamp)')
    plt.ylabel('Цена (close)')
    plt.title(f'Предвидување на цени за акциите')
    plt.legend()

    
    output_dir = "/app"  
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  
    output_path = os.path.join(output_dir, "price_prediction.png")
    plt.savefig(output_path)
    plt.close()  
    print(f"Графиконот е зачуван во: {output_path}")



def main():
    session = connect_to_cassandra()
    symbol = 'AAPL'  # Можеш да го смениш симболот на друга акција

    while True:  
        data = fetch_stock_data(session, symbol)

        
        analyze_data(data)

        
        predict_prices(data)

        time.sleep(3600)  


if __name__ == "__main__":
    main()
