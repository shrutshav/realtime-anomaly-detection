import json
import time
import random
import logging
from datetime import datetime
from confluent_kafka import Producer
import numpy as np
from schema import SensorData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProducer:
    def __init__(self, kafka_config: dict):
        self.producer = Producer(kafka_config)
        self.running = False
        
    def generate_normal_data(self, base_value: float = 0.0) -> float:
        """Generate normal sensor data using sine wave with some noise"""
        t = time.time()
        # Sine wave with period of 60 seconds + small noise
        normal_value = base_value + 10 * np.sin(2 * np.pi * t / 60) + random.gauss(0, 0.5)
        return normal_value
    
    def generate_anomaly(self, base_value: float = 0.0) -> float:
        """Generate anomalous sensor data"""
        anomaly_types = [
            base_value + random.gauss(0, 20),  # Spike
            base_value + 50 + random.gauss(0, 2),  # Level shift
            base_value - 30 + random.gauss(0, 2),  # Negative shift
        ]
        return random.choice(anomaly_types)
    
    def produce_data(self, topic: str, sensor_id: str = "sensor_001"):
        """Produce sensor data to Kafka topic"""
        self.running = True
        base_value = 100  # Base value for the sensor
        
        try:
            while self.running:
                # 5% chance of generating an anomaly
                if random.random() < 0.05:
                    value = self.generate_anomaly(base_value)
                    metric_type = "anomaly"
                else:
                    value = self.generate_normal_data(base_value)
                    metric_type = "normal"
                
                # Create sensor data
                sensor_data = SensorData(
                    timestamp=datetime.utcnow().isoformat(),
                    sensor_id=sensor_id,
                    value=value,
                    metric_type=metric_type
                )
                
                # Produce to Kafka
                self.producer.produce(
                    topic=topic,
                    value=sensor_data.to_json(),
                    callback=self.delivery_callback
                )
                
                self.producer.poll(0)
                time.sleep(1)  # Send data every second
                
        except KeyboardInterrupt:
            logger.info("Shutting down producer...")
        finally:
            self.producer.flush()
    
    def delivery_callback(self, err, msg):
        """Delivery callback for Kafka messages"""
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

if __name__ == "__main__":
    kafka_config = {
        'bootstrap.servers': 'localhost:29092'
    }
    
    producer = DataProducer(kafka_config)
    producer.produce_data("sensor-data")