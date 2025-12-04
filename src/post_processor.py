import argparse
import sys
from pathlib import Path

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import os
from datetime import datetime
from typing import Dict, Any, List
from api_manager import create_api_manager
from utils import get_logger, print_evaluation_report
from handler.json_handler import JSONHandler
from models import ProcessingBatch
from config.prompts import AREA_POST_PROCESSING_ENHANCED_PROMPT_EN

logger = get_logger('post_processor')

class PostProcessor:
    """Post-Processor - Handles post-processing and corrections for parsed results"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Post-Processor"""
        self.config = config
        self.api_manager = create_api_manager(
            config.get('api_config', {}),
            max_workers=config.get('max_workers', 5),
            max_retries=config.get('max_retries', 3),
            retry_delay=config.get('retry_delay', 1.0),
            rate_limit=config.get('rate_limit', None)
        )
        self.json_handler = JSONHandler()
        logger.info("Post-Processor initialized")
    
    def post_process_json_file(self, 
                              input_file: str, 
                              output_file: str, 
                              post_processing_prompt: str,
                              progress_callback=None, 
                              batch_size: int = 50) -> Dict[str, Any]:
        """Post-process a parsed JSON file"""
        logger.info(f"Starting post-processing: {input_file} -> {output_file}")
        
        # 1. Read parsed data
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = data.get('records', [])
        metadata = data.get('metadata', {})
        api_stats = data.get('api_stats', {})
        
        logger.info(f"Loaded {len(records)} records for post-processing")
        
        # 2. Prepare output file directory
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 3. Filter records for post-processing
        records_to_process = []
        records_no_process = []
        
        for record in records:
            # Only process records with parse_fields and no errors
            if ('parse_fields' in record and 
                'error' not in record['parse_fields'] and
                'raw_text' in record):
                records_to_process.append(record)
            else:
                records_no_process.append(record)
        
        logger.info(f"Records to process: {len(records_to_process)}, skipped: {len(records_no_process)}")
        
        # 4. Process in batches
        post_processed_records = []
        total_success_count = 0
        
        for batch_start in range(0, len(records_to_process), batch_size):
            batch_end = min(batch_start + batch_size, len(records_to_process))
            batch_records = records_to_process[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_start//batch_size + 1}: records {batch_start+1}-{batch_end}/{len(records_to_process)}")
            
            # Process current batch
            batch_processed, batch_success = self._post_process_batch(
                batch_records, post_processing_prompt, batch_start, len(records_to_process), progress_callback
            )
            
            post_processed_records.extend(batch_processed)
            total_success_count += batch_success
            
            logger.info(f"Batch completed: {batch_success}/{len(batch_records)} successful")
        
        # 5. Merge all records
        all_processed_records = post_processed_records + records_no_process
        
        # 6. Save final results
        final_output_data = {
            'metadata': {
                **metadata,
                'post_processing': {
                    'timestamp': datetime.now().isoformat(),
                    'original_success_count': metadata.get('success_count', 0),
                    'post_processed_count': len(records_to_process),
                    'post_processing_success_count': total_success_count,
                    'final_success_count': metadata.get('success_count', 0) - len(records_to_process) + total_success_count
                }
            },
            'records': all_processed_records,
            'api_stats': {
                **api_stats,
                'post_processing_stats': self.api_manager.get_stats()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Post-processing completed: {total_success_count}/{len(records_to_process)} successful")
        
        # 7. Output evaluation report
        print_evaluation_report(output_file)
        
        return {
            'input_file': input_file,
            'output_file': output_file,
            'total_records': len(records),
            'processed_records': len(records_to_process),
            'success_count': total_success_count,
            'final_success_rate': final_output_data['metadata']['post_processing']['final_success_count'] / len(records) if records else 0,
            'api_stats': self.api_manager.get_stats()
        }
    
    def _post_process_batch(self, batch_records: List[Dict], prompt: str, 
                           batch_start: int, total_records: int, progress_callback) -> tuple[List[Dict], int]:
        """Post-process a single batch"""
        # Prepare API requests
        batch_requests = []
        
        for i, record in enumerate(batch_records):
            # Build post-processing request
            post_process_input = self._build_post_process_input(record)
            batch_requests.append({
                'prompt': prompt,
                'input_text': post_process_input,
                'max_retries': 3,
                'original_index': i
            })
        
        # Batch API call
        def batch_progress_wrapper(completed, total):
            overall_completed = batch_start + completed
            if progress_callback:
                progress_callback(overall_completed, total_records)
        
        api_results = self.api_manager.batch_call(batch_requests, progress_callback=batch_progress_wrapper) if batch_requests else []
        
        # Process results
        processed_records = []
        success_count = 0
        
        for i, original_record in enumerate(batch_records):
            result_record = original_record.copy()
            
            if i < len(api_results):
                api_result = api_results[i]
                if api_result['result'].get('success'):
                    new_parse_fields = api_result['result']['data']
                    if new_parse_fields is not None:
                        # Directly use new post-processing results
                        result_record['parse_fields'] = new_parse_fields
                        result_record['post_processing_info'] = {
                            'processed': True,
                            'original_parse_fields': original_record.get('parse_fields', {})
                        }
                        success_count += 1
                    else:
                        result_record['post_processing_info'] = {
                            'error': 'Post-processing returned empty data',
                            'original_preserved': True
                        }
                else:
                    result_record['post_processing_info'] = {
                        'error': f"Post-processing failed: {api_result['result'].get('error')}",
                        'original_preserved': True
                    }
            else:
                result_record['post_processing_info'] = {
                    'error': 'Post-processing API call failed',
                    'original_preserved': True
                }
            
            processed_records.append(result_record)
        
        return processed_records, success_count
    
    def _build_post_process_input(self, record: Dict) -> str:
        """Build input for post-processing"""
        raw_text = record.get('raw_text', '')
        current_result = record.get('parse_fields', {})
        
        # Ensure current_result is not None and can be JSON serialized
        if current_result is None:
            current_result = {}
        
        try:
            current_result_json = json.dumps(current_result, ensure_ascii=False, indent=2)
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON serialization failed: {e}, using string representation")
            current_result_json = str(current_result)
        
        return f"""raw_text: {raw_text}

current_result: {current_result_json}"""

# Convenience function
def post_process_json_file(input_file: str, output_file: str, config: Dict[str, Any], 
                          progress_callback=None, batch_size: int = 50):
    """Convenience function for post-processing JSON files"""
    processor = PostProcessor(config)
    return processor.post_process_json_file(
        input_file, output_file, AREA_POST_PROCESSING_ENHANCED_PROMPT_EN, 
        progress_callback, batch_size
    )

def main():
    parser = argparse.ArgumentParser(description='Post-Processor - Handles post-processing for parsed JSON')
    
    # Basic parameters
    parser.add_argument('input_file', help='Path to the input parsed JSON file')
    parser.add_argument('output_file', help='Path to the output post-processed JSON file')
    
    # API configuration
    parser.add_argument('--provider', default='qwen', help='API provider (default: qwen)')
    parser.add_argument('--api-key', default='sk-60122c0caf2c461a9aa106c0ba04d419', help='API key')
    parser.add_argument('--model', default='qwen3-8b', help='Model to use (default: qwen3-8b)')
    parser.add_argument('--base-url', default='https://dashscope.aliyuncs.com/compatible-mode/v1', help='API base URL')
    parser.add_argument('--temperature', type=float, default=0.0, help='Temperature parameter (default: 0.0)')
    
    # Other options
    parser.add_argument('--evaluate', action='store_true', help='Show evaluation report after post-processing')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size (default: 50)')
    
    args = parser.parse_args()
    
    # Build API configuration
    api_config = {
        'api_key': args.api_key,
        'base_url': args.base_url,
        'model': args.model,
        'temperature': args.temperature,
        'response_format': {"type": "json_object"},
    }
    
    # Add enable_thinking parameter only for qwen provider
    if args.provider == 'qwen':
        api_config['extra_body'] = {'enable_thinking': False}
    
    config = {
        'max_workers': 10,
        'max_retries': 3,
        'api_config': {
            args.provider: api_config
        }
    }
    
    # Display configuration information
    print(f"Post-processing configuration: Provider={args.provider}, Model={args.model}, Temperature={args.temperature}")
    print(f"Input file: {args.input_file}")
    print(f"Output file: {args.output_file}")
    
    # Process file
    result = post_process_json_file(
        args.input_file,
        args.output_file,
        config,
        batch_size=args.batch_size
    )
    
    print(f"Post-processing completed:")
    print(f"  Processed records: {result['processed_records']}/{result['total_records']}")
    if result['processed_records'] > 0:
        print(f"  Success rate: {result['success_count']}/{result['processed_records']} = {result['success_count']/result['processed_records']:.2%}")
    print(f"  Final success rate: {result['final_success_rate']:.2%}")

    if args.evaluate:
        print_evaluation_report(args.input_file)

    # Show evaluation report
    if args.evaluate:
        print_evaluation_report(args.output_file)

if __name__ == "__main__":
    main()