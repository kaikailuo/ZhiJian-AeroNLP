import re
import json
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Union
from collections import OrderedDict
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, precision_score, recall_score, f1_score
import pandas as pd

class LogManager:
    """Log Manager - Singleton Pattern"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LogManager._initialized:
            self._setup_default_logging()
            LogManager._initialized = True
    
    def _setup_default_logging(self):
        """Set up default logging configuration"""
        # Create root logger
        self.logger = logging.getLogger('notam_processor')
        self.logger.setLevel(logging.INFO)
        
        # Avoid adding handlers multiple times
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # File handler
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_dir / 'notam_processor.log', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            # Add handlers
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """Get logger instance"""
        if name:
            return logging.getLogger(f'notam_processor.{name}')
        return self.logger
    
    def set_level(self, level: str):
        """Set logging level"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                    handler.setLevel(level_map[level.upper()])
    
    def add_file_handler(self, file_path: str, level: str = 'DEBUG'):
        """Add file log handler"""
        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, level.upper()))
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

# Global log manager instance
log_manager = LogManager()

# Convenience function
def get_logger(name: str = None) -> logging.Logger:
    """Convenience function to get logger instance"""
    return log_manager.get_logger(name)


# JSON processing functionality
def extract_json_from_text(content: str) -> Optional[Union[Dict, List]]:
    """Extract JSON data from text content"""
    logger = get_logger('JSONProcessor')
    
    if not content:
        logger.warning("Input content is empty")
        return None

    content = content.strip()
    logger.debug(f"Processing content length: {len(content)}")

    # 1. Try matching JSON in Markdown code blocks
    code_block_patterns = [
        r'```json\n(.*?)\n```',
        r'```\s*json\s*\n(.*?)\n\s*```',
        r'json\n([\s\S]*)',
        r'(?:json)?\s*\n?\s*(\[[\s\S]*?\])',
        r'(?:json)?\s*\n?\s*(\{[\s\S]*?\})'
    ]

    for i, pattern in enumerate(code_block_patterns):
        match = re.search(pattern, content, re.DOTALL)
        if match:
            try:
                json_str = match.group(1).strip().replace('\\"', '"')
                result = json.loads(json_str)
                logger.debug(f"Successfully parsed using pattern {i+1}")
                return result
            except json.JSONDecodeError as e:
                logger.debug(f"Failed to parse using pattern {i+1}: {e}")
                continue

    # 2. Try parsing as raw JSON
    try:
        result = json.loads(content)
        logger.debug("Successfully parsed as raw JSON")
        return result
    except json.JSONDecodeError as e:
        logger.debug(f"Failed to parse as raw JSON: {e}")

    # 3. Try handling JSON strings wrapped in quotes
    if content.startswith('"') and content.endswith('"'):
        try:
            unquoted = content[1:-1].replace('\\"', '"')
            result = json.loads(unquoted)
            logger.debug("Successfully parsed unquoted JSON")
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse unquoted JSON: {e}")

    logger.warning("All JSON parsing methods failed")
    return None


def clean_text(text: str) -> str:
    """Clean text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters
    text = re.sub(r'[^\w\s\(\)/\-\.]', '', text)
    
    return text.strip()

def _serialize_for_comparison(value: Any) -> str:
    """Serialize value to a consistent string for comparison"""
    if value is None:
        return "null"
    
    # If the value is a string, try parsing it as a JSON object
    if isinstance(value, str):
        try:
            # Parse and re-serialize to unify format (e.g., quotes and spaces)
            # sort_keys=True ensures consistent dictionary key order
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # If not a valid JSON string, keep it as is
            return value
    
    # If the value is a dictionary or list (from parsed JSON), serialize it
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(',', ':'))
        
    # Other types are converted to strings directly
    return str(value)

def compare_json_results(api_json: Any, gold_json: Any) -> bool:
    """Compare JSON results, ignoring order"""
    logger = get_logger('JSONProcessor')
    
    try:
        if not isinstance(api_json, list) or not isinstance(gold_json, list) or len(api_json) != len(gold_json):
            logger.debug(f"Type or length mismatch: {type(api_json)} vs {type(gold_json)}")
            return False

        for api_item in api_json:
            if not isinstance(api_item, dict):
                logger.debug("API item is not a dictionary")
                return False
            found_match = False
            for gold_item in gold_json:
                if not isinstance(gold_item, dict):
                    continue
                if all(api_item.get(key) == gold_item.get(key) for key in api_item):
                    found_match = True
                    break
            if not found_match:
                logger.debug(f"No matching item found: {api_item}")
                return False
        
        logger.debug("JSON comparison successful")
        return True
    except Exception as e:
        logger.error(f"Error comparing JSON: {e}")
        return False


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity (simple implementation)"""
    if not text1 or not text2:
        return 0.0
    
    # Simple word overlap similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def load_processed_data(file_path: str) -> List[Dict[str, Any]]:
    """Load processed JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['records']

def _normalize_parse_fields(parse_fields_raw: Any) -> Dict[str, Any]:
    """Normalize parse_fields format"""
    if isinstance(parse_fields_raw, dict):
        if 'rows' in parse_fields_raw and isinstance(parse_fields_raw['rows'], list):
            return parse_fields_raw['rows'][0] if parse_fields_raw['rows'] else {}
        return parse_fields_raw
    elif isinstance(parse_fields_raw, list):
        return parse_fields_raw[0] if parse_fields_raw and isinstance(parse_fields_raw[0], dict) else {}
    else:
        return {}

def extract_field_values(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, List]]:
    """Extract true and predicted values for all fields"""
    field_data = {}
    
    for record in records:
        manual_fields = record.get('manual_fields', {})
        parse_fields_raw = record.get('parse_fields', {})
        
        # Skip records with errors
        if isinstance(parse_fields_raw, dict) and 'error' in parse_fields_raw:
            continue
        
        # Process rows structure in manual_fields
        if 'rows' in manual_fields and isinstance(manual_fields['rows'], list):
            manual_rows = manual_fields['rows']
        else:
            # If no rows structure, treat the entire manual_fields as a single row
            manual_rows = [manual_fields]
        
        # Process parse_fields - fix part
        parse_rows = []
        if isinstance(parse_fields_raw, list):
            # Ensure each element in the list is a dictionary
            parse_rows = [item for item in parse_fields_raw if isinstance(item, dict)]
        elif isinstance(parse_fields_raw, dict):
            if 'rows' in parse_fields_raw and isinstance(parse_fields_raw['rows'], list):
                # Ensure each element in rows is a dictionary
                parse_rows = [item for item in parse_fields_raw['rows'] if isinstance(item, dict)]
            else:
                parse_rows = [parse_fields_raw]
        
        # Skip invalid parse_fields
        if not parse_rows:
            continue
            
        # For multi-row data, perform best matching instead of sequential matching
        if len(manual_rows) > 1 and len(parse_rows) > 1:
            # Use Hungarian algorithm or simple greedy matching
            matched_pairs = _find_best_row_matches(manual_rows, parse_rows)
        else:
            # Single row or one is empty, process as before
            min_length = min(len(manual_rows), len(parse_rows))
            matched_pairs = [(i, i) for i in range(min_length)]
        
        # Extract field values based on matching results
        for manual_idx, parse_idx in matched_pairs:
            if manual_idx < len(manual_rows) and parse_idx < len(parse_rows):
                manual_row = manual_rows[manual_idx]
                parse_row = parse_rows[parse_idx]
                
                # Ensure both rows are dictionaries
                if not isinstance(manual_row, dict) or not isinstance(parse_row, dict):
                    continue
                
                # Exclude "rows" field, only process actual data fields
                for field_name, manual_value in manual_row.items():
                    if field_name == 'rows':  # Skip rows field
                        continue
                        
                    if field_name not in field_data:
                        field_data[field_name] = {'y_true': [], 'y_pred': []}
                    
                    field_data[field_name]['y_true'].append(manual_value)
                    field_data[field_name]['y_pred'].append(parse_row.get(field_name, None))
    
    return field_data

def _calculate_row_similarity(manual_row: Dict, parse_row: Dict) -> float:
    """
    Calculate similarity score between two rows
    """
    # Add type checking
    if not isinstance(manual_row, dict) or not isinstance(parse_row, dict):
        return 0.0
    
    if not manual_row or not parse_row:
        return 0.0
    
    total_fields = 0
    matching_fields = 0
    
    for field_name, manual_value in manual_row.items():
        if field_name == 'rows':  # Skip rows field
            continue
            
        total_fields += 1
        parse_value = parse_row.get(field_name)
        
        # Standardized comparison (convert to string and handle None values)
        manual_str = str(manual_value) if manual_value is not None else "null"
        parse_str = str(parse_value) if parse_value is not None else "null"
        
        # Add intelligent comparison for JSON strings and dictionaries
        if manual_str != parse_str:
            # Try JSON parsing comparison
            if _try_json_comparison(manual_value, parse_value):
                matching_fields += 1
            # If not JSON comparable, keep the original mismatch result
        else:
            matching_fields += 1
    
    return matching_fields / total_fields if total_fields > 0 else 0.0

def _try_json_comparison(value1: Any, value2: Any) -> bool:
    """
    Attempt intelligent comparison of JSON strings and dictionaries
    """
    try:
        # Case 1: value1 is a JSON string, value2 is a dictionary
        if isinstance(value1, str) and isinstance(value2, dict):
            parsed_value1 = json.loads(value1)
            return parsed_value1 == value2
            
        # Case 2: value1 is a dictionary, value2 is a JSON string
        if isinstance(value1, dict) and isinstance(value2, str):
            parsed_value2 = json.loads(value2)
            return value1 == parsed_value2
            
        # Case 3: Both are JSON strings
        if isinstance(value1, str) and isinstance(value2, str):
            try:
                parsed_value1 = json.loads(value1)
                parsed_value2 = json.loads(value2)
                return parsed_value1 == parsed_value2
            except:
                return False
                
        return False
    except (json.JSONDecodeError, TypeError):
        return False

def _find_best_row_matches(manual_rows: List[Dict], parse_rows: List[Dict]) -> List[Tuple[int, int]]:
    """
    Find the best matches between manually labeled rows and parsed rows
    Return a list of matched index pairs [(manual_idx, parse_idx), ...]
    """
    logger = get_logger('FieldMatcher')
    
    if not manual_rows or not parse_rows:
        return []
    
    # Calculate match scores for each pair of rows
    scores = []
    for i, manual_row in enumerate(manual_rows):
        for j, parse_row in enumerate(parse_rows):
            score = _calculate_row_similarity(manual_row, parse_row)
            scores.append((score, i, j))
    
    # Sort by score and select the best matches
    scores.sort(reverse=True)
    
    used_manual = set()
    used_parse = set()
    matches = []
    
    for score, manual_idx, parse_idx in scores:
        if manual_idx not in used_manual and parse_idx not in used_parse:
            matches.append((manual_idx, parse_idx))
            used_manual.add(manual_idx)
            used_parse.add(parse_idx)
            logger.debug(f"Matched rows: manual[{manual_idx}] <-> parse[{parse_idx}], score: {score:.3f}")
    
    return matches

def calculate_metrics(file_path):
    """Calculate evaluation metrics"""
    records = load_processed_data(file_path)
    if not records:
        return None
    
    field_data = extract_field_values(records)
    if not field_data:
        return None
    
    results = {}
    for field_name, data in field_data.items():
        y_true = [_serialize_for_comparison(val) for val in data['y_true']]
        y_pred = [_serialize_for_comparison(val) for val in data['y_pred']]
        
        if not y_true:
            continue
        
        results[field_name] = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
            'f1': f1_score(y_true, y_pred, average='weighted', zero_division=0),
            'total_samples': len(y_true)
        }
    
    return results

def print_evaluation_report(file_path: str):
    """Print evaluation report"""
    logger = get_logger('EvaluationReport')  # Get logger instance
    
    logger.info(f"Starting evaluation report generation: {file_path}")
    print(f"\n=== Evaluation Report: {file_path} ===")
    
    results = calculate_metrics(file_path)
    if not results:
        logger.warning("Unable to generate evaluation report - no available data")
        print("Unable to generate evaluation report")
        return
    
    logger.info(f"Successfully calculated metrics for {len(results)} fields")
    
    # Print header
    print(f"\n{'Field Name':<20} {'Accuracy':<8} {'Precision':<8} {'Recall':<8} {'F1 Score':<8} {'Samples':<8}")
    print("-" * 75)
    
    # Print metrics for each field
    for field_name, metrics in results.items():
        logger.debug(f"Field {field_name}: Accuracy={metrics['accuracy']:.3f}, F1={metrics['f1']:.3f}")
        print(f"{field_name:<20} {metrics['accuracy']:.3f}    {metrics['precision']:.3f}    {metrics['recall']:.3f}    {metrics['f1']:.3f}    {metrics['total_samples']:<8}")
    
    # Overall metrics
    total_accuracy = sum(m['accuracy'] for m in results.values()) / len(results)
    total_f1 = sum(m['f1'] for m in results.values()) / len(results)
    total_samples = sum(m['total_samples'] for m in results.values())
    
    logger.info(f"Evaluation completed - Average Accuracy: {total_accuracy:.1%}, Average F1: {total_f1:.1%}, Total Samples: {total_samples}")
    
    print("-" * 75)
    print(f"{'Overall Average':<20} {total_accuracy:.3f}    {'N/A':<8} {'N/A':<8} {total_f1:.3f}    {total_samples:<8}")
    
    print(f"Evaluation Summary:")
    print(f"   Number of evaluated fields: {len(results)}")
    print(f"   Total samples: {total_samples}")
    print(f"   Average Accuracy: {total_accuracy:.1%}")
    print(f"   Average F1 Score: {total_f1:.1%}")

def compare_parsed_fields(manual_fields: Dict[str, Any], parse_fields: Any) -> Dict[str, Any]:
    """Compare manually labeled and AI-parsed fields"""
    normalized_parse_fields = _normalize_parse_fields(parse_fields)
    
    if 'error' in normalized_parse_fields:
        return {'match': False, 'error': normalized_parse_fields.get('error')}
    
    total_matches = sum(1 for field_name, manual_value in manual_fields.items() 
                       if normalized_parse_fields.get(field_name) == manual_value)
    total_fields = len(manual_fields)
    
    return {
        'match': total_matches == total_fields,
        'match_rate': total_matches / total_fields if total_fields > 0 else 0
    }