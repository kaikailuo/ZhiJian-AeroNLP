import json
import time
import random
from typing import List, Dict, Any
from api_manager import create_api_manager, APIManager

# API Configuration
API_CONFIG = {
    "deepseek": {
        "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Masked API key
        "use_json_format": True
    },
    "dmxapi": {
        "api_key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Masked API key
        "base_url": "https://www.dmxapi.com/v1",
        "model": "gpt-4.1-mini",
        "temperature": 0.1,
        "max_tokens": 8000,
        "timeout": 120,
        "response_format": {"type": "json_object"}  # If JSON format is required
    }
}

# Initialize API Manager
api_manager = create_api_manager(
    config=API_CONFIG,
    max_workers=3,
    max_retries=3,
    retry_delay=2.0,
    rate_limit=1.0  # 1 request per second
)

def call_llm_api(system_prompt: str, user_prompt: str) -> Any:
    """Wrapper function to call the LLM API"""
    result = api_manager.single_call(
        prompt=system_prompt,
        input_text=user_prompt,
        client_name="deepseek"
    )

    print(f"🔍 API Call: {result.get('client_name', 'unknown')} - Success: {result.get('success', False)}")
    
    # Update statistics
    api_manager.stats['total_requests'] += 1
    
    if result.get('success'):
        return result['data']
    else:
        raise Exception(f"API call failed: {result.get('error')}")

# Improved Agent Prompts
IMPROVED_AGENT_PROMPTS = {
    "consolidator": {
        "system_prompt": """You are an expert in field consolidation. Analyze NOTAM field definitions and identify semantic duplicates or overlaps.

**Key Analysis Points:**
1. Semantic overlap in field names (e.g., runway_closure vs runway_closed)
2. Redundancy in descriptive content (e.g., ice vs ice_condition)
3. High overlap in sources content

**Output Requirements:**
- Output only a JSON array, where each object includes:
  - action: "merge"
  - fields_to_merge: [Array of field names]
  - new_field_name: "Suggested new field name"
  - reason: "Reason for merging, citing specific sources as evidence"
  - confidence: 0.0-1.0

**Example:**
[{
  "action": "merge",
  "fields_to_merge": ["runway_closure", "runway_closed"],
  "new_field_name": "runway_closure",
  "reason": "The two fields have highly overlapping sources, both containing 'RWY CLSD' type content, and are semantically identical",
  "confidence": 0.95
}]

If no fields need merging, return an empty array: []
"""
    },
    "specializer": {
        "system_prompt": """You are an aviation terminology expert. Analyze field definitions and suggest renaming if field names are too generic and sources contain more precise terms.

**Key Points:**
1. Check for specialized terms in sources
2. Suggest using industry-standard terminology
3. Provide renaming suggestions

**Output Requirements:**
- Output only a JSON array, where each object includes:
  - action: "rename"
  - old_field_name: "Original field name"
  - new_field_name: "New field name"
  - reason: "Reason for renaming, citing specific sources as evidence"
  - confidence: 0.0-1.0

**Example:**
[{
  "action": "rename",
  "old_field_name": "declared_distance",
  "new_field_name": "TORA",
  "reason": "The sources explicitly include 'TORA 8102FT', so the precise term should be used",
  "confidence": 1.0
}]

If no fields need renaming, return an empty array: []
"""
    },
    "critic": {
        "system_prompt": """You are a critical analysis expert. Review the previous merging and renaming suggestions and identify potential issues.

**Key Analysis Points:**
1. Are merging suggestions too aggressive, potentially causing information loss?
2. Are renaming suggestions accurate, or do they lose important context?
3. Are there overlooked duplicate fields that were not identified?

**Output Requirements:**
- Output only a JSON array, where each object includes:
  - action: "challenge" or "approve"
  - target_proposal: Index of the proposal being reviewed (integer)
  - reason: "Reason for critique or approval"
  - confidence: 0.0-1.0

**Example:**
[{
  "action": "challenge",
  "target_proposal": 0,
  "reason": "hazard and hazard_area are similar, but hazard_area emphasizes spatial scope and should not be merged",
  "confidence": 0.8
}]

If all suggestions are fine, return an empty array: []
"""
    }
}

class FieldManager:
    """
    Programmatically manage field states to ensure uniqueness and apply changes.
    This is the core mechanism to avoid duplicate fields.
    """
    def __init__(self, initial_fields: List[Dict]):
        # Use a dictionary for state management, with fieldName as the key to ensure uniqueness
        self.fields = {field['fieldName']: field for field in initial_fields}
        print(f"✅ FieldManager initialized, managing {len(self.fields)} unique fields.")

    def get_all_fields(self) -> List[Dict]:
        """Return a list of all current fields."""
        return list(self.fields.values())

    def apply_merge(self, fields_to_merge: List[str], new_field_name: str):
        """Merge multiple fields into a new field."""
        # Ensure all fields to be merged exist
        if not all(field in self.fields for field in fields_to_merge):
            print(f"⚠️ Merge operation skipped: Not all fields {fields_to_merge} exist.")
            return

        print(f"  ➡️  Merging {fields_to_merge} -> {new_field_name}")
        
        # Merge all sources and remove duplicates
        all_sources = set()
        for name in fields_to_merge:
            all_sources.update(self.fields[name].get('sources', []))
            
        # Use the description of the first field as the base description
        new_description = self.fields[fields_to_merge[0]].get('description', '')
        
        # Create the new merged field
        self.fields[new_field_name] = {
            'fieldName': new_field_name,
            'description': new_description,
            'sources': sorted(list(all_sources))
        }
        
        # Delete old fields
        for name in fields_to_merge:
            if name != new_field_name:  # Do not delete if the new field name overwrites an old one
                if name in self.fields:
                    del self.fields[name]

    def apply_rename(self, old_name: str, new_name: str):
        """Rename a field."""
        if old_name not in self.fields:
            print(f"⚠️ Rename operation skipped: Field '{old_name}' does not exist.")
            return

        print(f"  ➡️  Renaming '{old_name}' -> '{new_name}'")
        field_data = self.fields.pop(old_name)
        field_data['fieldName'] = new_name
        self.fields[new_name] = field_data


class DebateSystem:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.initial_fields = self.load_initial_data()
        self.debate_log = []

    def load_initial_data(self) -> List[Dict]:
        """Load and deduplicate initial data."""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            initial_data = json.load(f)
        
        # Initial deduplication to handle duplicate dirty data during loading
        field_dict = {}
        for field in initial_data:
            field_name = field['fieldName']
            if field_name not in field_dict:
                field_dict[field_name] = field
            else:
                # If duplicates are found, merge their sources
                existing_sources = set(field_dict[field_name].get('sources', []))
                new_sources = set(field.get('sources', []))
                field_dict[field_name]['sources'] = sorted(list(existing_sources.union(new_sources)))
        
        return list(field_dict.values())

    def save_intermediate_result(self, stage: str, data: any):
        """Save intermediate results."""
        filename = f"data/output/intermediate_{stage}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Intermediate results saved to {filename}")

    def _get_proposals_from_llm(self, agent_name: str, current_fields: List[Dict], context_prompt: str = "", batch_size: int = 50) -> List[Dict]:
        """Process a large number of fields in batches to avoid oversized requests."""
        prompt_config = IMPROVED_AGENT_PROMPTS[agent_name]
        
        all_proposals = []
        
        # If the number of fields is small, process them directly
        if len(current_fields) <= batch_size:
            user_prompt = f"""{context_prompt}
            
Please analyze the following {len(current_fields)} fields:
{json.dumps(current_fields, indent=2, ensure_ascii=False)}
"""
            try:
                response = call_llm_api(prompt_config["system_prompt"], user_prompt)
                # Handle different types of responses
                if isinstance(response, list):
                    all_proposals.extend(response)
                elif isinstance(response, dict):
                    # If a single object is returned, add it to the array
                    if response.get('action'):
                        all_proposals.append(response)
                    elif 'proposals' in response:
                        all_proposals.extend(response['proposals'])
                else:
                    print(f"⚠️ {agent_name} returned an incorrect data format: {type(response)}")
            except Exception as e:
                print(f"⚠️ {agent_name} processing failed: {e}")
        
        else:
            # Process in batches
            for i in range(0, len(current_fields), batch_size):
                batch = current_fields[i:i + batch_size]
                print(f"📦 Processing batch {i//batch_size + 1}: {len(batch)} fields")
                
                user_prompt = f"""{context_prompt}
                
Please analyze the following {len(batch)} fields (Batch {i//batch_size + 1}):
{json.dumps(batch, indent=2, ensure_ascii=False)}
"""
                
                try:
                    response = call_llm_api(prompt_config["system_prompt"], user_prompt)
                    # Handle different types of responses
                    if isinstance(response, list):
                        all_proposals.extend(response)
                    elif isinstance(response, dict):
                        # If a single object is returned, add it to the array
                        if response.get('action'):
                            all_proposals.append(response)
                        elif 'proposals' in response:
                            all_proposals.extend(response['proposals'])
                    
                    # Pause between batches
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"⚠️ Batch {i//batch_size + 1} processing failed: {e}")
                    continue
        
        self.debate_log.append({"round": agent_name, "proposals": all_proposals})
        return all_proposals

    def _get_proposals_batch(self, agent_name: str, current_fields: List[Dict], context_prompt: str = "", batch_size: int = 50) -> List[Dict]:
        """Process fields using batch API calls."""
        prompt_config = IMPROVED_AGENT_PROMPTS[agent_name]
        
        # Prepare batch requests
        requests = []
        for i in range(0, len(current_fields), batch_size):
            batch = current_fields[i:i + batch_size]
            user_prompt = f"""{context_prompt}
            
Please analyze the following {len(batch)} fields (Batch {i//batch_size + 1}):
{json.dumps(batch, indent=2, ensure_ascii=False)}
"""
            requests.append({
                'prompt': prompt_config["system_prompt"],
                'input_text': user_prompt
            })
        
        # Progress callback
        def progress_callback(completed, total):
            print(f"📊 {agent_name} batch processing progress: {completed}/{total} ({completed/total*100:.1f}%)")
        
        # Execute batch calls
        results = api_manager.batch_call(
            requests=requests,
            progress_callback=progress_callback,
            client_name="deepseek"
        )
        
        # Process results
        all_proposals = []
        for result in results:
            if result['result'].get('success'):
                response_data = result['result']['data']
                # Handle different types of responses
                if isinstance(response_data, list):
                    all_proposals.extend(response_data)
                elif isinstance(response_data, dict):
                    # If a single object is returned, add it to the array
                    if response_data.get('action'):
                        all_proposals.append(response_data)
                    elif 'proposals' in response_data:
                        all_proposals.extend(response_data['proposals'])
            else:
                print(f"⚠️ Batch processing failed: {result['result'].get('error')}")
        
        self.debate_log.append({"round": agent_name, "proposals": all_proposals})
        return all_proposals

    def run_debate(self, use_batch_processing: bool = True) -> Dict:
        """Run the complete debate process with programmatic state management."""
        print(f"🏛️ Starting the debate process, initial unique fields count: {len(self.initial_fields)}")
        
        manager = FieldManager(self.initial_fields)
        
        # Choose processing method
        process_method = self._get_proposals_batch if use_batch_processing else self._get_proposals_from_llm

        # === Round 1: Consolidation Proposals ===
        print("\n=== Round 1: Getting Consolidation Proposals ===")
        consolidation_proposals = process_method("consolidator", manager.get_all_fields())
        self.save_intermediate_result("consolidation", consolidation_proposals)
        print(f"✅ Round 1 completed, obtained {len(consolidation_proposals)} consolidation proposals")
        
        # === Round 2: Specialization Proposals ===
        print("\n=== Round 2: Getting Specialization Proposals ===")
        specialization_proposals = process_method("specializer", manager.get_all_fields())
        self.save_intermediate_result("specialization", specialization_proposals)
        print(f"✅ Round 2 completed, obtained {len(specialization_proposals)} specialization proposals")
        
        # === Round 3: Critique Proposals ===
        print("\n=== Round 3: Getting Critique Proposals ===")
        all_proposals = consolidation_proposals + specialization_proposals
        if not all_proposals:
            print("⚠️ No proposals available for critique, skipping critique round.")
            critique_proposals = []
        else:
            print(f"📋 A total of {len(all_proposals)} proposals need critique")
            critique_proposals = process_method("critic", all_proposals, "Please review the following proposals:")
            self.save_intermediate_result("critique", critique_proposals)
            print(f"✅ Round 3 completed, obtained {len(critique_proposals)} critique proposals")
        
        # Create a set of proposals challenged with high confidence
        challenged_indices = {
            p['target_proposal'] for p in critique_proposals 
            if p.get('action') == 'challenge' and p.get('confidence', 0.0) > 0.75
        }
        print(f"🚫 {len(challenged_indices)} proposals were challenged with high confidence")
        
        # === Round 4: Programmatically Apply All Approved Proposals ===
        print("\n🏆 Starting to apply all approved proposals...")

        # 1. Apply consolidation proposals
        print(f"\n--- Applying Consolidation Proposals ({len(consolidation_proposals)} total) ---")
        applied_merges = 0
        for i, prop in enumerate(consolidation_proposals):
            if i in challenged_indices:
                print(f"🚫 Consolidation proposal {i} ({prop.get('new_field_name')}) was challenged, skipped.")
                continue
            if prop.get('confidence', 0.0) > 0.7:
                manager.apply_merge(prop['fields_to_merge'], prop['new_field_name'])
                applied_merges += 1
            else:
                print(f"⚠️ Consolidation proposal {i} has low confidence ({prop.get('confidence', 0.0)}), skipped.")
        print(f"✅ Applied {applied_merges} consolidation proposals")

        # 2. Apply renaming proposals
        print(f"\n--- Applying Renaming Proposals ({len(specialization_proposals)} total) ---")
        applied_renames = 0
        # Note: Index needs to account for the number of consolidation proposals
        start_index = len(consolidation_proposals)
        for i, prop in enumerate(specialization_proposals):
            proposal_index = start_index + i
            if proposal_index in challenged_indices:
                print(f"🚫 Renaming proposal {proposal_index} ({prop.get('old_field_name')} -> {prop.get('new_field_name')}) was challenged, skipped.")
                continue
            if prop.get('confidence', 0.0) > 0.7:
                manager.apply_rename(prop['old_field_name'], prop['new_field_name'])
                applied_renames += 1
            else:
                print(f"⚠️ Renaming proposal {proposal_index} has low confidence ({prop.get('confidence', 0.0)}), skipped.")
        print(f"✅ Applied {applied_renames} renaming proposals")
        
        final_result = manager.get_all_fields()
        
        # Log the final result
        self.debate_log.append({
            "round": "final_synthesis",
            "final_fields": final_result,
            "applied_merges": applied_merges,
            "applied_renames": applied_renames,
            "comments": "Fields were generated through programmatic application of AI proposals, ensuring uniqueness."
        })
        
        # Print API statistics
        print(f"\n📊 API Call Statistics:")
        stats = api_manager.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return {
            "initial_count": len(self.initial_fields),
            "final_count": len(final_result),
            "final_fields": final_result,
            "debate_log": self.debate_log,
            "applied_merges": applied_merges,
            "applied_renames": applied_renames,
            "api_stats": stats
        }


# --- Execute Script ---
if __name__ == "__main__":
    # Ensure your input file path is correct
    input_filename = "data/input/final.json"
    output_filename = "data/output/debate_result_final.json"
    
    try:
        debate_system = DebateSystem(input_filename)
        result = debate_system.run_debate(use_batch_processing=True)
        
        # Save results
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Debate completed!")
        print(f"📊 Field count reduced from {result['initial_count']} to {result['final_count']}")
        print(f"🔄 Applied {result['applied_merges']} consolidation proposals")
        print(f"📝 Applied {result['applied_renames']} renaming proposals")
        print(f"💾 Results saved to {output_filename}")

    except FileNotFoundError:
        print(f"Error: Input file not found. Please check if the path '{input_filename}' is correct.")
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")