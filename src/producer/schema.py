import json
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class SensorData:
    timestamp: str
    sensor_id: str
    value: float
    metric_type: str
    
    def to_json(self) -> str:
        return json.dumps({
            'timestamp': self.timestamp,
            'sensor_id': self.sensor_id,
            'value': self.value,
            'metric_type': self.metric_type
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SensorData':
        data = json.loads(json_str)
        return cls(
            timestamp=data['timestamp'],
            sensor_id=data['sensor_id'],
            value=data['value'],
            metric_type=data['metric_type']
        )