import os
from datetime import datetime, timedelta
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from influxdb_client import InfluxDBClient
import pandas as pd

# Initialize Dash app
app = dash.Dash(__name__)

# InfluxDB configuration
client = InfluxDBClient(
    url=os.getenv('INFLUXDB_URL', 'http://localhost:8086'),
    token=os.getenv('INFLUXDB_TOKEN', 'my-super-secret-auth-token'),
    org=os.getenv('INFLUXDB_ORG', 'anomaly-org')
)

# Layout
app.layout = html.Div([
    html.H1("Real-Time Anomaly Detection Dashboard"),
    
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    ),
    
    dcc.Graph(id='live-graph'),
    
    html.Div([
        html.H3("Statistics"),
        html.Div(id='stats')
    ])
])

@app.callback(
    [Output('live-graph', 'figure'),
     Output('stats', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    # Query last 5 minutes of data
    query_api = client.query_api()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=5)
    
    query = f'''
    from(bucket: "{os.getenv('INFLUXDB_BUCKET', 'sensor-data')}")
        |> range(start: -{5}m)
        |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
    '''
    
    result = query_api.query_data_frame(query)
    
    if result.empty:
        return {}, "No data available"
        
    # Process data for plotting
    df = pd.DataFrame(result)
    df['_time'] = pd.to_datetime(df['_time'])
    
    # Create graph
    fig = go.Figure()
    
    # Add normal points
    normal_points = df[df['is_anomaly'] == 0]
    fig.add_trace(go.Scatter(
        x=normal_points['_time'],
        y=normal_points['value'],
        mode='markers',
        name='Normal',
        marker=dict(color='blue', size=8)
    ))
    
    # Add anomaly points
    anomaly_points = df[df['is_anomaly'] == 1]
    fig.add_trace(go.Scatter(
        x=anomaly_points['_time'],
        y=anomaly_points['value'],
        mode='markers',
        name='Anomaly',
        marker=dict(color='red', size=10, symbol='x')
    ))
    
    # Update layout
    fig.update_layout(
        title='Sensor Readings with Anomaly Detection',
        xaxis_title='Time',
        yaxis_title='Value',
        showlegend=True
    )
    
    # Calculate statistics
    total_points = len(df)
    anomaly_count = len(anomaly_points)
    anomaly_rate = (anomaly_count / total_points * 100) if total_points > 0 else 0
    
    stats = html.Div([
        html.P(f"Total data points: {total_points}"),
        html.P(f"Detected anomalies: {anomaly_count}"),
        html.P(f"Anomaly rate: {anomaly_rate:.2f}%")
    ])
    
    return fig, stats

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)