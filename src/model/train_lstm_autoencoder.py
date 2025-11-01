import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LSTMAutoencoder:
    def __init__(self, sequence_length=60, n_features=1):
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = self._build_model()
        self.scaler = StandardScaler()
        
    def _build_model(self):
        """Build LSTM Autoencoder model"""
        model = Sequential([
            LSTM(64, activation='relu', input_shape=(self.sequence_length, self.n_features)),
            RepeatVector(self.sequence_length),
            LSTM(64, activation='relu', return_sequences=True),
            TimeDistributed(Dense(self.n_features))
        ])
        
        model.compile(optimizer='adam', loss='mse')
        return model
        
    def prepare_data(self, data_path: str) -> tuple:
        """Load and prepare training data"""
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        
        # Scale the data
        values = df['value'].values.reshape(-1, 1)
        scaled_values = self.scaler.fit_transform(values)
        
        # Create sequences
        sequences = []
        for i in range(len(scaled_values) - self.sequence_length + 1):
            sequence = scaled_values[i:(i + self.sequence_length)]
            sequences.append(sequence)
            
        return np.array(sequences)
        
    def train(self, X, epochs=50, batch_size=32):
        """Train the LSTM Autoencoder"""
        logger.info("Training LSTM Autoencoder...")
        
        self.model.fit(
            X, X,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            verbose=1
        )
        
        logger.info("Training completed")
        
    def save_model(self, model_dir: str):
        """Save the trained model and scaler"""
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)
        
        self.model.save(model_path / 'lstm_autoencoder.h5')
        joblib.dump(self.scaler, model_path / 'lstm_scaler.pkl')
        logger.info(f"Model and scaler saved to {model_path}")

def main():
    # Initialize model
    autoencoder = LSTMAutoencoder()
    
    # Prepare data
    data_path = 'data/training_data.csv'
    X = autoencoder.prepare_data(data_path)
    
    # Train model
    autoencoder.train(X)
    
    # Save model
    autoencoder.save_model('models')

if __name__ == "__main__":
    main()