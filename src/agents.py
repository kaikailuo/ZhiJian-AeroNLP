import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
from collections import defaultdict
import sys
from pathlib import Path

# Add config path
sys.path.append(str(Path(__file__).parent.parent / "config"))
from config.prompts import get_agent_prompt

logger = logging.getLogger(__name__)

class FieldType(Enum):
    BOOLEAN_FLAG = "boolean"
    DESCRIPTIVE_VALUE = "descriptive"
    TEMPORAL_INFO = "temporal"
    NUMERIC_VALUE = "numeric"
    LOCATION_INFO = "location"

@dataclass
class ExtractedField:
    """Extracted field"""
    key: str
    value: Any
    field_type: FieldType
    source_phrase: str
    confidence: float
    context: str = ""
    agent_name: str = ""

class BaseAgent(ABC):
    """Base Agent class"""
    
    def __init__(self, api_manager, name: str):
        self.api_manager = api_manager
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")
    
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task"""
        pass
    
    def _call_api(self, prompt: str, input_text: str) -> Dict[str, Any]:
        """Call API"""
        try:
            result = self.api_manager.single_call(prompt, input_text)
            if result.get('success'):
                return {'success': True, 'data': result.get('data')}
            else:
                self.logger.error(f"API call failed: {result.get('error')}")
                return {'success': False, 'error': result.get('error')}
        except Exception as e:
            self.logger.error(f"API call exception: {e}")
            return {'success': False, 'error': str(e)}

class DiscoveryAgent(BaseAgent):
    """Discovery Agent"""
    
    def __init__(self, api_manager):
        super().__init__(api_manager, "Discovery")
        self.prompt = get_agent_prompt('discovery')
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Discover new fields"""
        self.logger.info("🔍 Discovery Agent working...")
        
        notam_text = state.get('notam_text', '')
        existing_json = state.get('existing_json', {})
        
        input_text = f"""
NOTAM original text: {notam_text}
Parsed fields: {json.dumps(existing_json, ensure_ascii=False, indent=2)}
Please discover valuable missing fields.
"""
        
        result = self._call_api(self.prompt, input_text)
        
        if result.get('success'):
            data = result.get('data', {})
            extracted_fields = []
            
            for field_data in data.get('fields', []):
                try:
                    field_type = FieldType(field_data.get('type', 'descriptive'))
                    extracted_field = ExtractedField(
                        key=field_data.get('key', ''),
                        value=field_data.get('value'),
                        field_type=field_type,
                        source_phrase=field_data.get('source_phrase', ''),
                        confidence=field_data.get('confidence', 0.7),
                        context=field_data.get('context', ''),
                        agent_name=self.name
                    )
                    extracted_fields.append(extracted_field)
                except Exception as e:
                    self.logger.warning(f"Failed to parse field: {e}")
            
            state['discovery_fields'] = extracted_fields
            self.logger.info(f"✅ Discovered {len(extracted_fields)} fields")
        else:
            state['discovery_fields'] = []
        
        return state

class AnalystAgent(BaseAgent):
    """Analyst Agent"""
    
    def __init__(self, api_manager):
        super().__init__(api_manager, "Analyst")
        self.prompt = get_agent_prompt('analyst')
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fields"""
        self.logger.info("📊 Analyst Agent working...")
        
        notam_text = state.get('notam_text', '')
        existing_json = state.get('existing_json', {})
        
        input_text = f"""
NOTAM original text: {notam_text}
Parsed fields: {json.dumps(existing_json, ensure_ascii=False, indent=2)}
Please analyze and extract valuable missing fields.
"""
        
        result = self._call_api(self.prompt, input_text)
        
        if result.get('success'):
            data = result.get('data', {})
            extracted_fields = []
            
            for field_data in data.get('fields', []):
                try:
                    field_type = FieldType(field_data.get('type', 'descriptive'))
                    extracted_field = ExtractedField(
                        key=field_data.get('key', ''),
                        value=field_data.get('value'),
                        field_type=field_type,
                        source_phrase=field_data.get('source_phrase', ''),
                        confidence=field_data.get('confidence', 0.7),
                        context=field_data.get('context', ''),
                        agent_name=self.name
                    )
                    extracted_fields.append(extracted_field)
                except Exception as e:
                    self.logger.warning(f"Failed to parse field: {e}")
            
            state['analyst_fields'] = extracted_fields
            self.logger.info(f"✅ Analysis yielded {len(extracted_fields)} fields")
        else:
            state['analyst_fields'] = []
        
        return state

class ValidatorAgent(BaseAgent):
    """Validator Agent"""
    
    def __init__(self, api_manager):
        super().__init__(api_manager, "Validator")
        self.prompt = get_agent_prompt('validator')
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate fields"""
        self.logger.info("🔍 Validator Agent working...")
        
        notam_text = state.get('notam_text', '')
        existing_json = state.get('existing_json', {})
        
        input_text = f"""
NOTAM original text: {notam_text}
Parsed fields: {json.dumps(existing_json, ensure_ascii=False, indent=2)}
Please validate and extract high-quality missing fields.
"""
        
        result = self._call_api(self.prompt, input_text)
        
        if result.get('success'):
            data = result.get('data', {})
            extracted_fields = []
            
            for field_data in data.get('fields', []):
                try:
                    field_type = FieldType(field_data.get('type', 'descriptive'))
                    extracted_field = ExtractedField(
                        key=field_data.get('key', ''),
                        value=field_data.get('value'),
                        field_type=field_type,
                        source_phrase=field_data.get('source_phrase', ''),
                        confidence=field_data.get('confidence', 0.7),
                        context=field_data.get('context', ''),
                        agent_name=self.name
                    )
                    extracted_fields.append(extracted_field)
                except Exception as e:
                    self.logger.warning(f"Failed to parse field: {e}")
            
            state['validator_fields'] = extracted_fields
            self.logger.info(f"✅ Validation yielded {len(extracted_fields)} fields")
        else:
            state['validator_fields'] = []
        
        return state

class ConsensusAgent(BaseAgent):
    """Consensus Agent - Simplified Version"""
    
    def __init__(self, api_manager):
        super().__init__(api_manager, "Consensus")
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate all agent results"""
        self.logger.info("🤝 Consensus Agent working...")
        
        # Collect all fields
        all_fields = []
        all_fields.extend(state.get('discovery_fields', []))
        all_fields.extend(state.get('analyst_fields', []))
        all_fields.extend(state.get('validator_fields', []))
        
        if not all_fields:
            state['consensus_fields'] = []
            return state
        
        # Simple deduplication - based on similarity
        consensus_fields = self._deduplicate_fields(all_fields)
        
        # Sort by confidence
        consensus_fields.sort(key=lambda x: x.confidence, reverse=True)
        
        # Convert to dictionary format
        result_fields = []
        for field in consensus_fields:
            result_fields.append({
                'key': field.key,
                'value': field.value,
                'field_type': field.field_type.value,
                'source_phrase': field.source_phrase,
                'confidence': field.confidence,
                'context': field.context,
                'agent_name': field.agent_name
            })
        
        state['consensus_fields'] = result_fields
        self.logger.info(f"✅ Generated {len(result_fields)} consensus fields")
        
        return state
    
    def _deduplicate_fields(self, fields: List[ExtractedField]) -> List[ExtractedField]:
        """Deduplicate based on similarity"""
        if not fields:
            return []
        
        unique_fields = []
        
        for field in fields:
            is_duplicate = False
            for existing in unique_fields:
                # Calculate similarity
                similarity = self._calculate_similarity(field, existing)
                if similarity > 0.7:  # Similarity threshold
                    is_duplicate = True
                    # Keep the one with higher confidence
                    if field.confidence > existing.confidence:
                        unique_fields.remove(existing)
                        unique_fields.append(field)
                    break
            
            if not is_duplicate:
                unique_fields.append(field)
        
        return unique_fields
    
    def _calculate_similarity(self, field1: ExtractedField, field2: ExtractedField) -> float:
        """Calculate similarity between two fields"""
        # Field name similarity
        key_similarity = self._text_similarity(field1.key, field2.key)
        
        # Source phrase similarity
        phrase_similarity = self._text_similarity(field1.source_phrase, field2.source_phrase)
        
        # Value similarity
        value_similarity = self._text_similarity(str(field1.value), str(field2.value))
        
        # Combined similarity
        return (key_similarity * 0.4 + phrase_similarity * 0.3 + value_similarity * 0.3)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity"""
        if not text1 or not text2:
            return 0.0
        
        # Simple vocabulary overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

# Agent Factory
def create_agents(api_manager) -> Dict[str, BaseAgent]:
    """Create agents"""
    return {
        'discovery': DiscoveryAgent(api_manager),
        'analyst': AnalystAgent(api_manager),
        'validator': ValidatorAgent(api_manager),
        'consensus': ConsensusAgent(api_manager)
    }