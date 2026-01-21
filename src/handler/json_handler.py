"""
JSON文件处理器
"""
import json
from pathlib import Path
from typing import List, Union, Dict, Any
from src.models import NOTAMRecord, ProcessingBatch
from src.utils import get_logger

class JSONHandler:
    """JSON文件处理器"""
    
    def __init__(self):
        self.logger = get_logger('JSONHandler')
    
    def read(self, file_path: Union[str, Path]) -> List[NOTAMRecord]:
        """读取JSON文件"""
        file_path = Path(file_path)
        self.logger.info(f"读取JSON文件: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records_data = data.get('records', data) if isinstance(data, dict) else data
        records = [NOTAMRecord.from_dict(item) for item in records_data]
        
        self.logger.info(f"读取了 {len(records)} 条记录")
        return records
    
    def write(self, records: List[NOTAMRecord], file_path: Union[str, Path], metadata: Dict[str, Any] = None):
        """写入JSON文件"""
        file_path = Path(file_path)
        self.logger.info(f"写入JSON文件: {file_path}")
        
        if metadata is None:
            metadata = ProcessingBatch.create_metadata(total_records=len(records))
        
        data = {
            'metadata': metadata,
            'records': [record.to_dict() for record in records]
        }
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"写入完成: {len(records)} 条记录")