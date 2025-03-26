from flask import Flask, render_template
import plotly
import plotly.graph_objs as go
import json
import pandas as pd
from cassandra.cluster import Cluster

app = Flask(__name__)


def connect_to_cassandra():
    cluster = Cluster(['cassandra'], port=9042)
    session = cluster.connect('stock_data')
    return session


@app.route('/')
def visualize_data():
    session = connect_to_cassandra()
    query = "SELECT timestamp, close FROM stock_prices WHERE symbol = 'AAPL'"
    rows = session.execute(query)
    data = pd.DataFrame(rows)

   
    graph = go.Scatter(x=data['timestamp'], y=data['close'], mode='lines', name='AAPL')
    layout = go.Layout(title='Цени на акциите на AAPL', xaxis=dict(title='Време'), yaxis=dict(title='Цена'))
    fig = go.Figure(data=[graph], layout=layout)

    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', graphJSON=graphJSON)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
