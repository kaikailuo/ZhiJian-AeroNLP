import argparse
import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# === POML MODIFICATION ===
# Import poml if available
try:
    import poml
    POML_AVAILABLE = True
except ImportError:
    POML_AVAILABLE = False
    print("⚠️  Warning: 'poml' module not found. POML mode will be disabled.")

# Import project modules
from src.api_manager import create_api_manager
from src.utils import get_logger, print_evaluation_report
from src.handler.json_handler import JSONHandler
from src.models import ProcessingBatch
from config.prompts import *

logger = get_logger('main')

class DataProcessor:
    """Data Processor - Process JSON data and call API"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize processor"""
        self.config = config
        self.api_manager = create_api_manager(
            config.get('api_config', {}),
            max_workers=config.get('max_workers', 5),
            max_retries=config.get('max_retries', 3),
            retry_delay=config.get('retry_delay', 1.0),
            rate_limit=config.get('rate_limit', None)
        )
        self.json_handler = JSONHandler()
        # Add self-consistency configuration
        self.self_consistency_enabled = config.get('self_consistency', {}).get('enabled', False)
        self.consistency_rounds = config.get('self_consistency', {}).get('rounds', 3)
        self.consistency_strategy = config.get('self_consistency', {}).get('strategy', 'majority_vote')
        
        # === POML MODIFICATION ===
        self.use_poml = config.get('use_poml', False)
        self.poml_file = config.get('poml_file', None)
        
        logger.info("Data processor initialization complete")
        if self.self_consistency_enabled:
            logger.info(f"Self-consistency enabled: {self.consistency_rounds} rounds, strategy: {self.consistency_strategy}")
        # === POML MODIFICATION ===
        if self.use_poml:
            logger.info(f"POML mode enabled, using file: {self.poml_file}")
    
    def process_json_file(self, 
                         input_file: str, 
                         output_file: str, 
                         prompt: str = None,  # ← 改为可选
                         progress_callback=None, 
                         batch_size: int = 50) -> Dict[str, Any]:
        """Process complete flow for JSON file"""
        logger.info(f"Starting processing: {input_file} -> {output_file}")
        
        # 1. Read data
        records = self._load_records(input_file)
        logger.info(f"Read {len(records)} records")
        
        # 2. Prepare output file directory
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 3. Process in batches
        processed_records = []
        total_success_count = 0
        
        for batch_start in range(0, len(records), batch_size):
            batch_end = min(batch_start + batch_size, len(records))
            batch_records = records[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_start//batch_size + 1}: records {batch_start+1}-{batch_end}/{len(records)}")
            
            # === POML MODIFICATION ===
            if self.use_poml:
                batch_processed, batch_success = self._process_batch_poml(
                    batch_records, batch_start, len(records), progress_callback
                )
            else:
                batch_processed, batch_success = self._process_batch(
                    batch_records, prompt, batch_start, len(records), progress_callback
                )
            # === END MODIFICATION ===
            
            processed_records.extend(batch_processed)
            total_success_count += batch_success
            
            # Incremental save
            self._save_progress(output_file, processed_records, total_success_count, len(records))
            
            logger.info(f"Batch complete: {batch_success}/{len(batch_records)} successful, cumulative: {total_success_count}/{len(processed_records)}")
        
        # 4. Save final result
        final_output_data = {
            'metadata': ProcessingBatch.create_metadata(
                total_records=len(processed_records),
                processing_type='api_processing',
                success_count=total_success_count
            ),
            'records': processed_records,
            'api_stats': self.api_manager.get_stats()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Processing complete: {total_success_count}/{len(records)} successful")
        
        # 5. Output evaluation report
        print_evaluation_report(output_file)
        
        return {
            'input_file': input_file,
            'output_file': output_file,
            'total_records': len(records),
            'success_count': total_success_count,
            'success_rate': total_success_count / len(records) if records else 0,
            'api_stats': self.api_manager.get_stats()
        }
    
    def _load_records(self, input_file: str) -> List[Dict]:
        """Load records - Handle different JSON structures uniformly"""
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'records' in data:
            return data['records']
        elif isinstance(data, list):
            return data
        else:
            return [data]
    
    # === POML MODIFICATION ===
    def _process_batch_poml(self, batch_records: List[Dict], 
                           batch_start: int, total_records: int, progress_callback) -> tuple[List[Dict], int]:
        """Process a single batch in POML mode"""
        batch_requests = []
        batch_indices = []
        
        for i, item in enumerate(batch_records):
            if 'raw_text' in item:
                if self.self_consistency_enabled:
                    for round_idx in range(self.consistency_rounds):
                        batch_requests.append({
                        'mode': 'poml',
                            'poml_file': self.poml_file,
                            'input_text': item['raw_text'],
                            'max_retries': 3,
                            'original_index': i,
                            'round': round_idx
                        })
                else:
                    batch_requests.append({
                        'mode': 'poml',
                        'poml_file': self.poml_file,
                        'input_text': item['raw_text'],
                        'max_retries': 3,
                        'original_index': i,
                        'round': 0
                    })
                batch_indices.append(i)
        
        def batch_progress_wrapper(completed, total):
            if self.self_consistency_enabled:
                overall_completed = batch_start + (completed // self.consistency_rounds)
            else:
                overall_completed = batch_start + completed
            if progress_callback:
                progress_callback(overall_completed, total_records)
        
        api_results = self.api_manager.batch_call(batch_requests, progress_callback=batch_progress_wrapper) if batch_requests else []
        
        processed_records = []
        success_count = 0
        
        for i, original in enumerate(batch_records):
            result_record = original.copy()
            
            if i in batch_indices:
                if self.self_consistency_enabled:
                    round_results = []
                    for round_idx in range(self.consistency_rounds):
                        result_idx = i * self.consistency_rounds + round_idx
                        if result_idx < len(api_results):
                            round_results.append(api_results[result_idx])
                    
                    best_result = self._apply_consistency_strategy(round_results)
                    if best_result and best_result['result'].get('success'):
                        parsed_fields = best_result['result']['data']
                        if parsed_fields is not None:
                            result_record['parse_fields'] = parsed_fields
                            result_record['consistency_info'] = {
                                'rounds': len(round_results),
                                'strategy': self.consistency_strategy,
                                'all_results': [r['result'] for r in round_results]
                            }
                            success_count += 1
                        else:
                            result_record['parse_fields'] = {
                                'error': 'Self-consistency returned empty data',
                                'consistency_info': {'rounds': len(round_results)}
                            }
                    else:
                        result_record['parse_fields'] = {
                            'error': 'Self-consistency failed',
                            'consistency_info': {'rounds': len(round_results)}
                        }
                else:
                    if i < len(api_results):
                        api_result = api_results[i]
                        if api_result['result'].get('success'):
                            parsed_fields = api_result['result']['data']
                            if parsed_fields is not None:
                                result_record['parse_fields'] = parsed_fields
                                success_count += 1
                            else:
                                result_record['parse_fields'] = {
                                    'error': 'API returned empty data',
                                    'raw_response': api_result['result'].get('raw_response')
                                }
                        else:
                            result_record['parse_fields'] = {'error': api_result['result'].get('error')}
            else:
                result_record['parse_fields'] = {'error': 'Missing raw_text field'}
            
            processed_records.append(result_record)
        
        return processed_records, success_count
    # === END POML MODIFICATION ===
    
    def _process_batch(self, batch_records: List[Dict], prompt: str, 
                      batch_start: int, total_records: int, progress_callback) -> tuple[List[Dict], int]:
        """Process a single batch (Traditional mode)"""
        # Prepare API requests
        batch_requests = []
        batch_indices = []
        
        for i, item in enumerate(batch_records):
            if 'raw_text' in item:
                if self.self_consistency_enabled:
                    for round_idx in range(self.consistency_rounds):
                        batch_requests.append({
                            'prompt': prompt,
                            'input_text': item['raw_text'],
                            'max_retries': 3,
                            'original_index': i,
                            'round': round_idx
                        })
                else:
                    batch_requests.append({
                        'prompt': prompt,
                        'input_text': item['raw_text'],
                        'max_retries': 3,
                        'original_index': i,
                        'round': 0
                    })
                batch_indices.append(i)
        
        # Batch API call
        def batch_progress_wrapper(completed, total):
            if self.self_consistency_enabled:
                overall_completed = batch_start + (completed // self.consistency_rounds)
            else:
                overall_completed = batch_start + completed
            if progress_callback:
                progress_callback(overall_completed, total_records)
        
        api_results = self.api_manager.batch_call(batch_requests, progress_callback=batch_progress_wrapper) if batch_requests else []
        
        # Process results
        processed_records = []
        success_count = 0
        
        for i, original in enumerate(batch_records):
            result_record = original.copy()
            
            if i in batch_indices:
                if self.self_consistency_enabled:
                    round_results = []
                    for round_idx in range(self.consistency_rounds):
                        result_idx = i * self.consistency_rounds + round_idx
                        if result_idx < len(api_results):
                            round_results.append(api_results[result_idx])
                    
                    best_result = self._apply_consistency_strategy(round_results)
                    if best_result and best_result['result'].get('success'):
                        parsed_fields = best_result['result']['data']
                        if parsed_fields is not None:
                            result_record['parse_fields'] = parsed_fields
                            result_record['consistency_info'] = {
                                'rounds': len(round_results),
                                'strategy': self.consistency_strategy,
                                'all_results': [r['result'] for r in round_results]
                            }
                            success_count += 1
                        else:
                            result_record['parse_fields'] = {
                                'error': 'Self-consistency returned empty data',
                                'consistency_info': {'rounds': len(round_results)}
                            }
                    else:
                        result_record['parse_fields'] = {
                            'error': 'Self-consistency failed',
                            'consistency_info': {'rounds': len(round_results)}
                        }
                else:
                    if i < len(api_results):
                        api_result = api_results[i]
                        if api_result['result'].get('success'):
                            parsed_fields = api_result['result']['data']
                            if parsed_fields is not None:
                                result_record['parse_fields'] = parsed_fields
                                success_count += 1
                            else:
                                result_record['parse_fields'] = {
                                    'error': 'API returned empty data',
                                    'raw_response': api_result['result'].get('raw_response')
                                }
                        else:
                            result_record['parse_fields'] = {'error': api_result['result'].get('error')}
            else:
                result_record['parse_fields'] = {'error': 'Missing raw_text field'}
            
            processed_records.append(result_record)
        
        return processed_records, success_count
    
    def _parse_api_response(self, raw_response):
        """Parse API response - Simplified version"""
        return raw_response if raw_response is not None else None
    
    def _save_progress(self, output_file: str, processed_records: List[Dict], success_count: int, total_records: int):
        """Save current progress"""
        progress_data = {
            'metadata': {
                **ProcessingBatch.create_metadata(
                    total_records=len(processed_records),
                    processing_type='api_processing_in_progress',
                    success_count=success_count
                ),
                'progress': {
                    'completed_records': len(processed_records),
                    'total_records': total_records,
                    'success_count': success_count,
                    'completion_rate': len(processed_records) / total_records if total_records > 0 else 0,
                    'success_rate': success_count / len(processed_records) if processed_records else 0
                }
            },
            'records': processed_records
        }
        
        temp_file = output_file.replace('.json', '_progress.json')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2, default=str)

    def _apply_consistency_strategy(self, round_results: List[Dict]) -> Dict:
        """Apply self-consistency strategy to choose the best result"""
        if not round_results:
            return None
        
        successful_results = [r for r in round_results if r['result'].get('success')]
        
        if not successful_results:
            return round_results[0] if round_results else None
        
        if self.consistency_strategy == 'majority_vote':
            return self._majority_vote_strategy(successful_results)
        elif self.consistency_strategy == 'first_success':
            return successful_results[0]
        elif self.consistency_strategy == 'most_confident':
            return self._most_confident_strategy(successful_results)
        else:
            logger.warning(f"Unknown consistency strategy: {self.consistency_strategy}, using majority_vote")
            return self._majority_vote_strategy(successful_results)
    
    def _majority_vote_strategy(self, results: List[Dict]) -> Dict:
        """Majority vote strategy"""
        if len(results) == 1:
            return results[0]
        
        result_scores = {}
        
        for i, result_a in enumerate(results):
            score = 0
            data_a = result_a['result'].get('data', {})
            
            for j, result_b in enumerate(results):
                if i != j:
                    data_b = result_b['result'].get('data', {})
                    score += self._calculate_similarity(data_a, data_b)
            
            result_scores[i] = score
        
        best_index = max(result_scores, key=result_scores.get)
        return results[best_index]
    
    def _most_confident_strategy(self, results: List[Dict]) -> Dict:
        """Choose most confident result (based on field completeness)"""
        def calculate_confidence(result):
            data = result['result'].get('data', {})
            if not isinstance(data, dict):
                return 0
            
            non_empty_fields = sum(1 for v in data.values() if v and str(v).strip())
            total_chars = sum(len(str(v)) for v in data.values() if v)
            
            return non_empty_fields * 10 + total_chars
        
        return max(results, key=calculate_confidence)
    
    def _calculate_similarity(self, data_a: Dict, data_b: Dict) -> float:
        """Calculate similarity between two parsing results"""
        if not isinstance(data_a, dict) or not isinstance(data_b, dict):
            return 0.0
        
        common_keys = set(data_a.keys()) & set(data_b.keys())
        if not common_keys:
            return 0.0
        
        similarity_score = 0
        for key in common_keys:
            val_a = str(data_a.get(key, '')).strip()
            val_b = str(data_b.get(key, '')).strip()
            
            if val_a == val_b:
                similarity_score += 1
            elif val_a and val_b:
                similarity_score += len(set(val_a.split()) & set(val_b.split())) / max(len(val_a.split()), len(val_b.split()))
        
        return similarity_score / len(common_keys)

# Convenience functions
def process_json_with_prompt(input_file: str, output_file: str, prompt: str = None, config: Dict[str, Any] = None,
                           progress_callback=None, batch_size: int = 50):
    """Convenience function to process JSON file"""
    processor = DataProcessor(config)
    return processor.process_json_file(input_file, output_file, prompt, progress_callback, batch_size)

def main():
    parser = argparse.ArgumentParser(description='Data Processor - Process JSON data and call API')
    
    # Basic arguments
    parser.add_argument('input_file', nargs='?', help='Input JSON file path')
    parser.add_argument('output_file', nargs='?', help='Output JSON file path')
    parser.add_argument('--prompt', help='Prompt content (required in traditional mode)')
    
    # === POML MODIFICATION ===
    parser.add_argument('--use-poml', action='store_true', help='Use POML format instead of prompt')
    parser.add_argument('--poml-file', help='Path to POML file (required if --use-poml is set)')
    # === END MODIFICATION ===
    
    # API configuration
    parser.add_argument('--provider', default='qwen', help='API provider (default: qwen)')
    parser.add_argument('--api-key', default='sk-xx', help='API key')
    parser.add_argument('--model', default='qwen3-8b', help='Model to use (default: qwen3-8b)')
    parser.add_argument('--base-url', default='https://dashscope.aliyuncs.com/compatible-mode/v1', help='API base URL')
    parser.add_argument('--temperature', type=float, default=0.0, help='Temperature parameter, controls output randomness (default: 0.0)')
       
    # Self-consistency configuration
    parser.add_argument('--self-consistency', action='store_true', help='Enable self-consistency')
    parser.add_argument('--consistency-rounds', type=int, default=3, help='Self-consistency rounds (default: 3)')
    parser.add_argument('--consistency-strategy', choices=['majority_vote', 'first_success', 'most_confident'], 
                       default='majority_vote', help='Self-consistency strategy (default: majority_vote)')
    
    # Other options
    parser.add_argument('--evaluate', action='store_true', help='Show evaluation report after processing')
    parser.add_argument('--evaluate_only', metavar='FILE', help='Only evaluate specified file, no processing')
    
    args = parser.parse_args()
    
    # Evaluation-only mode
    if args.evaluate_only:
        print_evaluation_report(args.evaluate_only)
        return
    
    # Validate required parameters (only in non-evaluation mode)
    if not args.input_file or not args.output_file:
        parser.error("In processing mode, input_file and output_file are required parameters")
    
    # === POML MODIFICATION ===
    if args.use_poml:
        if not args.poml_file:
            parser.error("--poml-file is required when --use-poml is set")
        if not os.path.exists(args.poml_file):
            parser.error(f"POML file not found: {args.poml_file}")
        if POML_AVAILABLE:
            poml.set_trace(trace_dir="pomlruns")  # 启用追踪
            print(f"POML mode enabled with file: {args.poml_file}")
        else:
            parser.error("POML module not installed. Please install 'poml' package.")
        actual_prompt = None  # POML模式下不需要prompt
    else:
        if not args.prompt:
            parser.error("In traditional mode, --prompt is required")
        
        # Process prompt: if it's a predefined prompt name, get the actual content
        prompt_map = {
            'LIGHT_PROMPT': LIGHT_PROMPT_ICL,
            'LIGHT_PROMPT_A': LIGHT_PROMPT_ICL_A,
            'LIGHT_PROMPT_Vanilla': LIGHT_PROMPT_Vanilla,
            'LIGHT_PROMPT_A_Vanilla': LIGHT_PROMPT_A_Vanilla,
            'LIGHT_PROMPT_A_COT': LIGHT_PROMPT_A_COT,
            'RUNWAY_PROMPT_ICL': RUNWAY_PROMPT_ICL,
            'RUNWAY_PROMPT_Vanilla': RUNWAY_PROMPT_Vanilla,
            'RUNWAY_PROMPT_COT': RUNWAY_PROMPT_COT,
            'TAXIWAY_PROMPT_Vanilla': TAXIWAY_PROMPT_Vanilla,
            'TAXIWAY_PROMPT_COT': TAXIWAY_PROMPT_COT,
            'TAXIWAY_PROMPT_ICL': TAXIWAY_PROMPT_ICL,
            'AIRPORT_PROMPT_ICL': AIRPORT_PROMPT_ICL,
            'AIRPORT_PROMPT_Vanilla': AIRPORT_PROMPT_Vanilla,
            'AIRPORT_PROMPT_COT': AIRPORT_PROMPT_COT,
            'PROCEDURE_PROMPT_Vanilla': PROCEDURE_PROMPT_Vanilla,
            'PROCEDURE_PROMPT_COT': PROCEDURE_PROMPT_COT,
            'PROCEDURE_PROMPT_ICL': PROCEDURE_PROMPT_ICL,
            'NAVIGATION_PROMPT_ICL': NAVIGATION_PROMPT_ICL,
            'NAVIGATION_PROMPT_Vanilla': NAVIGATION_PROMPT_Vanilla,
            'NAVIGATION_PROMPT_COT': NAVIGATION_PROMPT_COT,
            'STAND_PROMPT_Vanilla': STAND_PROMPT_Vanilla,
            'STAND_PROMPT_COT': STAND_PROMPT_COT,
            'STAND_PROMPT_ICL': STAND_PROMPT_ICL,
            'AIRWAY_PROMPT_Vanilla': AIRWAY_PROMPT_Vanilla,
            'AIRWAY_PROMPT_COT': AIRWAY_PROMPT_COT,
            'AIRWAY_PROMPT_ICL': AIRWAY_PROMPT_ICL,
            'STANDARD_PROMPT_Vanilla': STANDARD_PROMPT_Vanilla,
            'STANDARD_PROMPT_COT': STANDARD_PROMPT_COT,
            'STANDARD_PROMPT_ICL': STANDARD_PROMPT_ICL,
            'AREA_PROMPT_Vanilla': AREA_PROMPT_Vanilla,
            'AREA_PROMPT_COT': AREA_PROMPT_COT,
            'AREA_PROMPT_ICL': AREA_PROMPT_ICL,
            'RVR_PROMPT_Vanilla': RVR_PROMPT_Vanilla,
            'RVR_PROMPT_COT': RVR_PROMPT_COT,
            'RVR_PROMPT_ICL': RVR_PROMPT_ICL
        }
        
        # Get actual prompt content
        if args.prompt in prompt_map:
            actual_prompt = prompt_map[args.prompt]
            print(f"Using predefined prompt: {args.prompt}")
        else:
            actual_prompt = args.prompt
            print(f"Using custom prompt")
        
        # Ensure prompt contains json keyword (if using json format output)
        if 'json' not in actual_prompt.lower():
            actual_prompt = f"{actual_prompt}\n\nPlease respond in JSON format."
            print("Automatically added JSON format requirement to prompt")
    # === END MODIFICATION ===
    
    # Build API configuration based on provider
    api_config = {
        'api_key': args.api_key,
        'base_url': args.base_url,
        'model': args.model,
        'temperature': args.temperature,
        'response_format': {"type": "json_object"},
    }
    
    if args.provider == 'qwen':
        # 千问API的enable_thinking参数需要通过extra_body传递
        api_config['extra_body'] = {'enable_thinking': False}
    
    print(f"API configuration: Provider={args.provider}, Model={args.model}, Temperature={args.temperature}")
    
    config = {
        'max_workers': 10,
        'max_retries': 3,
        'api_config': {
            args.provider: api_config
        },
        'self_consistency': {
            'enabled': args.self_consistency,
            'rounds': args.consistency_rounds,
            'strategy': args.consistency_strategy
        },
        # === POML MODIFICATION ===
        'use_poml': args.use_poml,
        'poml_file': args.poml_file if args.use_poml else None
        # === END MODIFICATION ===
    }
    
    # Process file
    result = process_json_with_prompt(
        args.input_file,
        args.output_file,
        actual_prompt,  # 可能为 None
        config,
        batch_size=100
    )
    
    print(f"Processing complete: {result['success_rate']:.2%} success rate")
    
    if args.evaluate:
        print_evaluation_report(args.output_file)

if __name__ == "__main__":
    main()