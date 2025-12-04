# NOTAM Parsing System

Official Repository for Our Paper

## Project Structure

```
├── config/                 # Configuration files
│   ├── prompts.py         # Traditional prompt definitions
│   └── settings.py        # System settings
├── src/                   # Source code
│   ├── agents.py         # Intelligent agents
│   ├── api_manager.py    # API manager
│   ├── debate.py         # Debate mechanism
│   ├── mining.py         # Data mining
│   ├── models.py         # Data models
│   ├── post_processor.py # Post processor
│   └── utils.py          # Utility functions
├── config.yaml           # Main configuration file
├── main.py               # Main program entry
└── requirements.txt      # Dependencies list
```

## Environment Setup

### Installing Dependencies with uv

We recommend using [uv](https://github.com/astral-sh/uv) to manage Python dependencies:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Install project dependencies
uv pip install -r requirements.txt
```

### Environment Variables Configuration

Create a `.env` file to configure API keys:

```bash
# DMX API
DMXAPI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Other API keys...
```

## Usage

### For Web Demo

```
uv run streamlit run streamlit_app.py
```

### Basic Command Format

```bash
uv run main.py <input_file> <output_file> --prompt <prompt> [options]
```

### Example Commands

#### 1. Airport Data Processing
```bash
uv run main.py data/output/airport.json data/output/airport_icl_gpt-4.1-nano.json \
  --prompt AIRPORT_PROMPT_ICL \
  --provider dmxapi \
  --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --model gpt-4.1-nano \
  --base-url https://www.dmxapi.com/v1 \
  --evaluate
```

#### 2. Runway Data Processing (with Self-consistency)
```bash
uv run main.py data/output/runway.json data/output/runway_processed.json \
  --prompt RUNWAY_PROMPT_ICL \
  --provider deepseek \
  --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --model deepseek-chat \
  --self-consistency \
  --consistency-rounds 5 \
  --consistency-strategy majority_vote \
  --evaluate
```

#### 3. Light Data Processing (with Different Temperature)
```bash
uv run main.py data/output/light.json data/output/light_processed.json \
  --prompt LIGHT_PROMPT_A_COT \
  --provider qwen \
  --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --model qwen3-8b \
  --temperature 0.2 \
  --evaluate
```

#### 4. Taxiway Data Processing
```bash
uv run main.py data/output/taxiway.json data/output/taxiway_processed.json \
  --prompt TAXIWAY_PROMPT_ICL \
  --provider qwen \
  --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --model qwen3-8b \
  --evaluate
```

#### 5. Navigation Data Processing
```bash
uv run main.py data/output/navigation.json data/output/navigation_processed.json \
  --prompt NAVIGATION_PROMPT_COT \
  --provider deepseek \
  --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --model deepseek-chat \
  --temperature 0.1 \
  --evaluate
```

#### 6. POML Mode Processing
```bash
uv run main.py data/output/airport.json data/output/airport_poml_processed.json \
  --use-poml \
  --poml-file config/Airport.poml \
  --provider qwen \
  --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --model qwen3-8b \
  --evaluate
```

#### 7. POML Mode with Self-consistency
```bash
uv run main.py data/output/runway.json data/output/runway_poml_processed.json \
  --use-poml \
  --poml-file config/Airport.poml \
  --provider deepseek \
  --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --model deepseek-chat \
  --self-consistency \
  --consistency-rounds 3 \
  --consistency-strategy majority_vote \
  --evaluate
```

### Command Line Arguments

#### Required Parameters
- `input_file`: Input JSON file path
- `output_file`: Output JSON file path
- `--prompt`: Prompt content or predefined prompt name (required in traditional mode)

#### POML Mode Parameters
- `--use-poml`: Enable POML (Prompt Optimization Markup Language) mode
- `--poml-file`: Path to POML file (required when --use-poml is set)

#### API Configuration Parameters
- `--provider`: API provider (qwen/deepseek/dmxapi/openai)
- `--api-key`: API key
- `--model`: Model name to use
- `--base-url`: API base URL
- `--temperature`: Temperature parameter, controls output randomness (0.0-1.0)

#### Self-consistency Parameters
- `--self-consistency`: Enable self-consistency validation
- `--consistency-rounds`: Number of self-consistency rounds (default: 3)
- `--consistency-strategy`: Strategy selection
  - `majority_vote`: Majority voting (default)
  - `first_success`: First success
  - `most_confident`: Highest confidence

#### Other Options
- `--evaluate`: Show evaluation report after processing
- `--evaluate_only FILE`: Only evaluate specified file, no processing

## Predefined Prompts

The system provides various predefined prompts covering different data types and reasoning strategies:

### Data Types
- `AIRPORT_PROMPT_*`: Airport-related data
- `RUNWAY_PROMPT_*`: Runway-related data
- `LIGHT_PROMPT_*`: Light-related data
- `TAXIWAY_PROMPT_*`: Taxiway-related data
- `AIRWAY_PROMPT_*`: Airway-related data
- `AREA_PROMPT_*`: Area-related data
- `STAND_PROMPT_*`: Stand-related data
- `NAVIGATION_PROMPT_*`: Navigation-related data
- `PROCEDURE_PROMPT_*`: Procedure-related data
- `STANDARD_PROMPT_*`: Standard-related data
- `RVR_PROMPT_*`: RVR-related data

### Reasoning Strategies
- `*_Vanilla`: Basic prompts
- `*_ICL`: In-context learning with examples
- `*_COT`: Chain-of-thought reasoning
- `*_POML`: POML (Prompt Optimization Markup Language) mode

## Post-processing(SRCV)

For further optimization and validation of parsed data:

```bash
uv run src/post_processor.py input_file.json output_file.json \
  --provider qwen \
  --api-key sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \
  --model qwen3-8b \
  --evaluate
```

## Configuration Files

### config.yaml
Main configuration file containing API settings, path configurations, and processing parameters:

```yaml
api:
  default_provider: "deepseek"
  providers:
    deepseek:
      api_key: "${DEEPSEEK_API_KEY}"
      base_url: "https://api.deepseek.com/v1"
      model: "deepseek-chat"

paths:
  data_dir: "./data"
  output_dir: "./data/output"

processing:
  default_sample_size: 100
  max_workers: 4
```

## Logging and Monitoring

- Log files located in `logs/` directory
- Real-time progress display and success rate statistics
- API call statistics and error tracking
- Automatic evaluation report generation after processing completion

## Supported Data Formats

### Input Format
```json
{
  "records": [
    {
      "raw_text": "NOTAM raw text...",
      "category": "runway",
      "telex": "A001/23"
    }
  ]
}
```

### Output Format
```json
{
  "metadata": {
    "total_records": 100,
    "success_count": 95,
    "processing_time": "2023-01-01T12:00:00"
  },
  "records": [
    {
      "raw_text": "Raw text",
      "parse_fields": {
        "airport": "ZBAA",
        "runway": "18L/36R",
        "status": "closed"
      }
    }
  ],
  "api_stats": {
    "total_requests": 100,
    "successful_requests": 95
  }
}
```



