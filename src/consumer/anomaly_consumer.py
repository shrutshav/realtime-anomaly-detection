import json
import logging
from confluent_kafka import Consumer
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import joblib
import os
from schema import SensorData
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnomalyConsumer:
    def __init__(self, kafka_config: dict, influxdb_config: dict):
        self.consumer = Consumer(kafka_config)
        self.influxdb_client = InfluxDBClient(**influxdb_config)
        self.write_api = self.influxdb_client.write_api(write_options=SYNCHRONOUS)
        
        # Load the model and scaler
        self.model = joblib.load('models/isolation_forest.pkl')
        self.scaler = joblib.load('models/scaler.pkl')
        self.running = True
        
    def detect_anomaly(self, value: float, hour: int, minute: int) -> bool:
        """Detect if a value is anomalous using the trained model"""
        # Prepare features
        features = [[value, hour, minute]]
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)
        return prediction[0] == -1  # -1 indicates anomaly
        
    def write_to_influxdb(self, sensor_data: SensorData, is_anomaly: bool):
        """Write data point to InfluxDB"""
        point = Point("sensor_readings") \
            .tag("sensor_id", sensor_data.sensor_id) \
            .field("value", sensor_data.value) \
            .field("is_anomaly", int(is_anomaly)) \
            .time(datetime.fromisoformat(sensor_data.timestamp))
            
        self.write_api.write(
            bucket=os.getenv('INFLUXDB_BUCKET', 'sensor-data'),
            org=os.getenv('INFLUXDB_ORG', 'anomaly-org'),
            record=point
        )
        
    def consume_data(self, topics: list):
        """Consume messages from Kafka topics"""
        self.consumer.subscribe(topics)
        
        try:
            while self.running:
                msg = self.consumer.poll(1.0)
                
                if msg is None:
                    continue
                if msg.error():
                    logger.error(f"Consumer error: {msg.error()}")
                    continue
                    
                try:
                    # Parse message
                    sensor_data = SensorData.from_json(msg.value().decode('utf-8'))
                    
                    # Get time features
                    dt = datetime.fromisoformat(sensor_data.timestamp)
                    hour, minute = dt.hour, dt.minute
                    
                    # Detect anomaly
                    is_anomaly = self.detect_anomaly(sensor_data.value, hour, minute)
                    
                    # Write to InfluxDB
                    self.write_to_influxdb(sensor_data, is_anomaly)
                    
                    logger.info(
                        f"Processed value: {sensor_data.value:.2f}, "
                        f"Anomaly: {is_anomaly}, "
                        f"Sensor: {sensor_data.sensor_id}"
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Shutting down consumer...")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    # Kafka configuration
    kafka_config = {
        'bootstrap.servers': 'localhost:29092',
        'group.id': 'anomaly_detector',
        'auto.offset.reset': 'latest'
    }
    
    # InfluxDB configuration
    influxdb_config = {
        'url': os.getenv('INFLUXDB_URL', 'http://localhost:8086'),
        'token': os.getenv('INFLUXDB_TOKEN', 'my-super-secret-auth-token'),
        'org': os.getenv('INFLUXDB_ORG', 'anomaly-org')
    }
    
    consumer = AnomalyConsumer(kafka_config, influxdb_config)
    consumer.consume_data(['sensor-data'])