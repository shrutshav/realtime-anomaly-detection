import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import joblib
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IsolationForestTrainer:
    def __init__(self, contamination=0.05):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def prepare_data(self, data_path: str) -> tuple:
        """Load and prepare training data"""
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        
        # Convert timestamp to datetime features
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        
        # Select features for training
        features = ['value', 'hour', 'minute']
        X = df[features]
        
        # Scale the features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled
        
    def train(self, X):
        """Train the Isolation Forest model"""
        logger.info("Training Isolation Forest model...")
        self.model.fit(X)
        logger.info("Training completed")
        
    def save_model(self, model_dir: str):
        """Save the trained model and scaler"""
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, model_path / 'isolation_forest.pkl')
        joblib.dump(self.scaler, model_path / 'scaler.pkl')
        logger.info(f"Model and scaler saved to {model_path}")

def main():
    # Initialize trainer
    trainer = IsolationForestTrainer()
    
    # Prepare data
    data_path = 'data/training_data.csv'
    X = trainer.prepare_data(data_path)
    
    # Train model
    trainer.train(X)
    
    # Save model
    trainer.save_model('models')

if __name__ == "__main__":
    main()