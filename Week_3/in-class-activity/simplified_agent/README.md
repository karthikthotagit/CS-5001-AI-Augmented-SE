# Classroom CLI Agent (cca)

**LLM-powered** Natural Language-based Python code generation using Ollama.

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# 1. Start Ollama
ollama serve

# 2. Pull model
ollama pull devstral-small-2:24b-cloud

# 3. Create projects with natural language
cca create "calculator with basic operations"
cca create "streamlit weather dashboard"
cca create "todo list manager"

# 4. Commit
cca commit --repo output/calculator_20240210_120000
```

## Usage

### Create Projects

Simple - just describe what you want:

```bash
cca create "calculator"
cca create "streamlit data visualization app"
cca create "prime number checker"
cca create "REST API for user management"
cca create "discord bot for moderation"
```

**What is happening using LLM:**
- **LLM analyzes** your description
- **Smart project naming** (e.g., `calculator_basic_operations`)
- **Intelligent module naming** (e.g., `src/calculator.py`, `src/app.py`, `src/api.py`)
- **Auto-generates project files:**
  - `requirements.txt` - Dependencies based on your project
  - `README.md` - Project documentation
  - `.gitignore` - Python gitignore
- Git initialized
- Code generated

**No hard-coded rules** - the LLM decides the best structure for your project!

### Options

```bash
# Custom repository
cca create "my app" --repo output/custom_name

# Custom module
cca create "my app" --module src/custom.py

# Different model
cca create "my app" --model llama3.2:3b

# Verbose output
cca create "my app" --verbose
```

### Commit Changes

```bash
# Simple commit
cca commit --repo output/calculator

# With custom message
cca commit "Add new features" --repo output/calculator

# Commit and push
cca commit --repo output/calculator --push
```

## Examples

### Calculator
```bash
cca create "calculator with add, subtract, multiply, divide"
```
**Creates:**
```
output/calculator_add_subtract_multiply_20240210_120000/
├── .git/
├── .gitignore
├── README.md
├── requirements.txt
└── src/
    └── calculator.py
```

### Streamlit App
```bash
cca create "streamlit weather dashboard"
```
**Creates:**
```
output/streamlit_weather_dashboard_20240210_120030/
├── .git/
├── .gitignore
├── README.md
├── requirements.txt (includes streamlit, requests, etc.)
└── src/
    └── app.py
```

### Prime Checker
```bash
cca create "prime number checker"
```
**Creates:**
```
output/prime_number_checker_20240210_120045/
├── .git/
├── .gitignore
├── README.md
├── requirements.txt
└── src/
    └── prime.py
```

### REST API
```bash
cca create "REST API for user authentication"
```
**Creates:**
```
output/rest_api_user_authentication_20240210_120100/
├── .git/
├── .gitignore
├── README.md
├── requirements.txt (includes flask/fastapi, etc.)
└── src/
    └── api.py
```

## LLM-Powered Intelligence

The CLI uses the LLM to intelligently analyze your description and determine:

### Project Structure Examples

| You Say | LLM Infers |
|---------|------------|
| "calculator with basic operations" | Project: `calculator_basic_operations`<br>Module: `src/calculator.py` |
| "streamlit dashboard for analytics" | Project: `streamlit_dashboard_analytics`<br>Module: `src/app.py` |
| "REST API for user authentication" | Project: `rest_api_user_authentication`<br>Module: `src/api.py` |
| "discord bot for server moderation" | Project: `discord_bot_server_moderation`<br>Module: `src/bot.py` |
| "data scraper for news articles" | Project: `data_scraper_news_articles`<br>Module: `src/scraper.py` |

**The LLM understands context** and creates appropriate names and structures automatically!

## Configuration

### Environment Variables

```bash
export OLLAMA_MODEL="llama2"
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_TEMPERATURE="0.0"
```

### Command Options

```bash
cca --help                  # Show all options
cca create --help          # Show create options
cca commit --help          # Show commit options
```

## Common Commands (commands.yml)

See `commands.yml` for predefined shell commands:

```bash
# Using the commands.yml
./run_command.sh setup              # Setup everything
./run_command.sh ollama-start       # Start Ollama
./run_command.sh example-calculator # Run example
```

## How It Works

**Phase 0: Structure Inference (LLM-powered)**
- Analyzes your description
- Determines optimal project name
- Selects appropriate module path

**Phase 0.5: Project Scaffolding (LLM-powered)**
- Generates `requirements.txt` with relevant dependencies
- Creates `README.md` with project documentation
- Adds `.gitignore` for Python projects

**Phase 1: Planning**
- Analyzes description and existing code
- Creates implementation plan

**Phase 2: Drafting**
- Generates initial code based on plan

**Phase 3: Review**
- Reviews and improves code quality

**Phase 4: Writing**
- Saves to repository with git initialization

## Troubleshooting

```bash
# Ollama not running
ollama serve

# Model not found
ollama pull devstral-small-2:24b-cloud

# Clean up
rm -rf output/*/
```

## Project Structure

```
simplified_agent/
├── commands.yml             # Predefined commands (optional)
├── pyproject.toml          # Project config
├── README.md
└── src/
    └── classroom_cli_agent/
        ├── cli.py          # CLI with smart defaults
        ├── agent.py        # Core agent logic
        ├── llm.py          # Ollama integration
        ├── prompts.py      # Prompt templates
        ├── tools.py        # File/Git tools
        └── utils.py
```

## Examples Comparison

### Before (Complex)
```bash
cca --repo output/demo_calculator --verbose create \
    --desc "A calculator with add, subtract, multiply, divide" \
    --module src/calculator.py
```

### After (Simple)
```bash
cca create "calculator"
```

**That's it!** The CLI now works with natural language by default.
