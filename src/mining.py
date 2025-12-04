import json
import time
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd

from .api_manager import create_api_manager
from .agents import create_agents, ExtractedField

logger = logging.getLogger(__name__)

class FieldMiner:
    """Field Miner - Based on multi-agent voting"""
    
    def __init__(self, api_config: Dict[str, Any]):
        """Initialization"""
        self.api_manager = create_api_manager(
            config=api_config,
            max_workers=3,
            max_retries=2,
            retry_delay=1.0,
            rate_limit=1.0
        )
        
        # Create agents
        self.agents = create_agents(self.api_manager)
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'fields_discovered': 0,
            'consensus_fields': 0,
            'processing_time': 0.0
        }
    
    def process_single_notam(self, notam_text: str, existing_json: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single NOTAM"""
        start_time = time.time()
        
        try:
            # Workflow state
            state = {
                'notam_text': notam_text,
                'existing_json': existing_json
            }
            
            # Execute multiple agents in parallel
            state = self.agents['discovery'].execute(state)
            state = self.agents['analyst'].execute(state)
            state = self.agents['validator'].execute(state)
            
            # Generate consensus
            state = self.agents['consensus'].execute(state)
            
            # Statistics
            self.stats['total_processed'] += 1
            self.stats['consensus_fields'] += len(state.get('consensus_fields', []))
            self.stats['processing_time'] += time.time() - start_time
            
            return {
                'success': True,
                'consensus_fields': state.get('consensus_fields', []),
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Failed to process NOTAM: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def batch_process(self, notam_data: List[Dict[str, Any]], 
                     progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """Batch processing"""
        logger.info(f"🚀 Starting batch processing of {len(notam_data)} NOTAMs...")
        
        all_consensus_fields = []
        successful_count = 0
        
        for i, data in enumerate(notam_data):
            result = self.process_single_notam(
                data.get('notam_text', ''),
                data.get('existing_json', {})
            )
            
            if result.get('success'):
                all_consensus_fields.extend(result.get('consensus_fields', []))
                successful_count += 1
            
            if progress_callback:
                progress_callback(i + 1, len(notam_data))
            
            # Avoid API rate limits
            time.sleep(0.5)
        
        # Global aggregation - based on quality scores
        final_recommendations = self._create_final_recommendations(all_consensus_fields)
        
        return {
            'success': True,
            'final_recommendations': final_recommendations,
            'statistics': {
                'total_processed': len(notam_data),
                'successful': successful_count,
                'failed': len(notam_data) - successful_count,
                'consensus_fields': len(all_consensus_fields),
                'final_recommendations': len(final_recommendations),
                'processing_time': self.stats['processing_time']
            }
        }
    
    def _create_final_recommendations(self, all_consensus_fields: List[Dict]) -> List[Dict]:
        """Create final recommendations"""
        if not all_consensus_fields:
            return []
        
        # Sort by quality score
        all_consensus_fields.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        # Deduplicate - keep the highest quality
        seen_keys = set()
        final_recommendations = []
        
        for field in all_consensus_fields:
            key = field.get('key', '')
            if key not in seen_keys:
                seen_keys.add(key)
                final_recommendations.append({
                    'key': key,
                    'field_type': field.get('field_type', ''),
                    'quality_score': field.get('quality_score', 0),
                    'confidence': field.get('confidence', 0),
                    'vote_count': field.get('vote_count', 0),
                    'agent_diversity': field.get('agent_diversity', 0),
                    'example_value': field.get('value', ''),
                    'source_phrase': field.get('source_phrase', ''),
                    'context': field.get('context', ''),
                    'recommendation_reason': self._generate_recommendation_reason(field)
                })
        
        return final_recommendations
    
    def _generate_recommendation_reason(self, field: Dict) -> str:
        """Generate recommendation reason"""
        reasons = []
        
        if field.get('agent_diversity', 0) >= 2:
            reasons.append(f"Multiple agents ({field.get('agent_diversity')}) reached consensus")
        
        if field.get('confidence', 0) >= 0.8:
            reasons.append("High confidence")
        
        if field.get('quality_score', 0) >= 0.8:
            reasons.append("High quality score")
        
        field_type = field.get('field_type', '')
        if field_type == 'temporal':
            reasons.append("Temporal information is operationally important")
        elif field_type == 'boolean':
            reasons.append("Boolean status aids decision-making")
        
        return "; ".join(reasons) if reasons else "Recommended by agents"
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """Save results"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save full results
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Save recommendations as CSV
        recommendations = results.get('final_recommendations', [])
        if recommendations:
            df = pd.DataFrame(recommendations)
            csv_path = output_path.with_suffix('.csv')
            df.to_csv(csv_path, index=False, encoding='utf-8')
        
        logger.info(f"✅ Results saved to {output_path}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return self.stats.copy()

# Convenience function
def create_field_miner(api_config: Dict[str, Any]) -> FieldMiner:
    """Create a Field Miner"""
    return FieldMiner(api_config)