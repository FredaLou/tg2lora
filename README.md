# tg2lora

Turn Telegram exports into LoRA-ready training data. Quality-filter messages, generate replies with a local LLM, export to conversations / ChatML / Alpaca.

## Pipeline

```
raw input → [source parser] → [rule filter] → [LLM judge (optional)] → [LLM generation] → output dataset
```

## Quick Start

```bash
pip install -r requirements.txt

# Run a local LLM server (llama.cpp, vLLM, etc.) on port 8080, then:
python main.py full --input data/my_chat.json --output data/train.json
```

## Commands

| Command | Description |
|---------|-------------|
| `full` | Filter + generate in one shot |
| `filter` | Filter only → JSON array of strings |
| `generate` | Generate from pre-filtered texts |

### Examples

```bash
# Full pipeline with intermediate file
python main.py full --input data/chat.json --output data/train.json --filtered-output data/filtered.json

# Change output format
python main.py full --input data/chat.json --output data/train.json --format chatml
python main.py full --input data/chat.json --output data/train.json --format alpaca

# Custom config
python main.py full --input data/chat.json --output data/train.json --config my_config.yaml
```

## Input Formats

| Format | Source | Example |
|--------|--------|---------|
| `telegram` | Telegram chat export JSON | `{\"messages\": [{\"from\": \"...\", \"text\": \"...\"}]}` |
| `jsonl` | JSONL or JSON array | `{\"user\": \"hello\"}` |
| `conversations` | Existing conversation files | `{\"conversations\": [{\"from\": \"human\", \"value\": \"...\"}]}` |

## Output Formats

| Format | Structure |
|--------|-----------|
| `conversations` | `[{\"conversations\": [{\"from\": \"human\", \"value\": \"...\"}, {\"from\": \"gpt\", \"value\": \"...\"}]}]` |
| `chatml` | `<\\|user\\|>text<\\|assistant\\|>reply<\\|end\\|>` (one per line) |
| `alpaca` | `[{\"prompt\": \"...\", \"completion\": \"...\"}]` |

## Configuration

All settings in `dataset_config.yaml`:

```yaml
source:
  format: telegram          # telegram | jsonl | conversations
  field: text

filters:
  min_len: 30
  max_len: 300
  rule_threshold: 0
  range:
    start: 0
    end: null               # null = all
  llm_judge:
    enabled: false
    url: http://127.0.0.1:8080/completion
    keep_score: 5
    max_results: 1000

generation:
  url: http://127.0.0.1:8080/completion
  temperature: 0.85
  max_tokens: 1024
  top_p: 0.9
  min_p: 0.05
  repeat_penalty: 1.1
  delay: 0.2
  stop: [\"</s>\", \"User:\"]
  system_prompt: |
    You are a helpful assistant.
    Be natural, concise, and direct.
    Speak in the same language as the user.

output:
  format: conversations     # conversations | chatml | alpaca
```

## Project Structure

```
├── main.py              # CLI entry point
├── dataset_config.yaml  # Main configuration
├── config/              # Config loading
├── sources/             # Input parsers (telegram, jsonl, conversations)
├── filters/             # Rule-based + LLM quality filters
├── generators/          # LLM server client (llama.cpp / OpenAI-compatible)
├── output/              # Format converters (conversations, chatml, alpaca)
└── data/                # Input/output files
```

## Notes

- **Resume**: generation skips already-processed texts if output file exists
- **LLM judge**: opt-in via `llm_judge.enabled: true`
- Works with any OpenAI-compatible server (llama.cpp, vLLM, text-generation-webui)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
