"""
Core Data Models
"""
import pandas as pd
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
from pathlib import Path

@dataclass
class NOTAMRecord:
    """Single NOTAM Record"""
    id: str
    category: str
    raw_text: str
    manual_fields: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NOTAMRecord':
        if 'metadata' in data:
            data.pop('metadata')
        return cls(**data)

@dataclass
class ProcessingBatch:
    """Processing Batch"""
    records: List[NOTAMRecord]
    metadata: Dict[str, Any]
    
    def __len__(self) -> int:
        return len(self.records)
    
    def sample(self, size: int) -> 'ProcessingBatch':
        if size >= len(self.records):
            return self
        import random
        sampled_records = random.sample(self.records, size)
        return ProcessingBatch(
            records=sampled_records,
            metadata={**self.metadata, 'sampled': True, 'sample_size': size}
        )
    
    @staticmethod
    def create_metadata(**kwargs) -> Dict[str, Any]:
        base_metadata = {'created_at': pd.Timestamp.now().isoformat()}
        base_metadata.update(kwargs)
        return base_metadata