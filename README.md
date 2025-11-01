# Real-Time Anomaly Detection System

This project implements a real-time anomaly detection system using Apache Kafka for data streaming, Python for processing, and InfluxDB for time-series storage.

## Project Structure

```
real-time-anomaly-detection/
├── docker-compose.yml    # Docker services configuration
├── Dockerfile           # Dashboard service container definition
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore file
├── src/
│   ├── producer/       # Kafka producer for sensor data
│   ├── model/         # ML models for anomaly detection
│   ├── consumer/      # Kafka consumer and anomaly detection
│   ├── alerter/       # Alert service
│   └── dashboard/     # Real-time visualization dashboard
├── data/              # Training data
└── models/            # Saved ML models
```

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Git

## Setup Instructions

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the infrastructure services:
   ```bash
   docker-compose up -d
   ```

4. Train the initial model:
   ```bash
   python src/model/train_isolation_forest.py
   ```

5. Start the services in separate terminals:
   ```bash
   # Terminal 1 - Start data producer
   python src/producer/data_producer.py

   # Terminal 2 - Start anomaly consumer
   python src/consumer/anomaly_consumer.py
   ```

6. Access the dashboard at http://localhost:8050

## Environment Variables

Create a `.env` file with the following variables:

```
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=my-super-secret-auth-token
INFLUXDB_ORG=anomaly-org
INFLUXDB_BUCKET=sensor-data
```

## Components

### Data Producer
Generates synthetic sensor data with occasional anomalies and publishes to Kafka.

### Anomaly Detection Models
- Isolation Forest: For point anomalies
- LSTM Autoencoder: For sequence anomalies

### Consumer
Processes incoming sensor data, detects anomalies, and stores results in InfluxDB.

### Dashboard
Real-time visualization of sensor data and detected anomalies.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.