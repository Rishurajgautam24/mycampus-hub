# 💻 AutoGen Code Agent

A code execution agent that can write, execute, and iterate on Python code to solve tasks autonomously.

## 📖 Overview

This project demonstrates an **autonomous coding agent** that:
1. Receives a task in natural language
2. Reasons about the solution
3. Writes Python code to solve it
4. Executes the code locally
5. Analyzes results and iterates if needed
6. Terminates when the task is complete

## 🏗️ Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│   Assistant Agent   │◄───►│   User Proxy Agent  │
│   (Code Generator)  │     │   (Code Executor)   │
└─────────────────────┘     └─────────────────────┘
                                      │
                                      ▼
                            ┌─────────────────────┐
                            │   Local Execution   │
                            │   (coding/ folder)  │
                            └─────────────────────┘
```

## 🎯 What It Does

The default task demonstrates the agent:
1. Finding the current date and time
2. Writing it to a file (`current_time.txt`)
3. Listing directory contents to confirm file creation

## 🛠️ Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) installed
- [Ollama](https://ollama.com/) running locally (or any OpenAI-compatible API)

## 🚀 How to Run

### 1. Navigate to Project Directory

```bash
cd autogen-code-agent
```

### 2. Install Dependencies (from root directory)

If you haven't already installed dependencies:

```bash
# From root directory
uv venv
source .venv/bin/activate
uv sync
```

### 3. Setup Environment Variables

Create a `.env` file in the project directory (or root):

```env
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434/v1
```

### 4. Start Ollama (if using locally)

```bash
ollama serve
# In another terminal, pull a model:
ollama pull qwen2.5:7b
```

### 5. Run the Agent

```bash
python app.py
```

### 6. Check the Output

After execution, check the `coding/` directory:

```bash
ls coding/
cat coding/current_time.txt
```

## 📁 Project Structure

```
autogen-code-agent/
├── app.py          # Main application with agent logic
├── config.yaml     # LLM configuration
├── coding/         # Generated after first run (code execution workspace)
└── README.md       # This file
```

## ⚙️ Configuration

The `config.yaml` file contains LLM settings:

```yaml
config_list:
  - model: "${OLLAMA_MODEL}"
    base_url: "${OLLAMA_BASE_URL}"
    api_key: "ollama"
    price: [0, 0]
    temperature: 0.1
    cache_seed: null
```

## 🔧 Customization

### Change the Task

Modify the `task` variable in `app.py` to give the agent different challenges:

```python
task = """
Fetch the weather data from a public API.
Parse the JSON response and extract the temperature.
Save the result to a file named 'weather.txt'.
"""
```

### Enable Docker Execution

For safer code execution in isolation:

```python
code_execution_config={
    "work_dir": "coding",
    "use_docker": True,  # Enable Docker
},
```

### Adjust Agent Behavior

Modify the `system_message` to change how the agent approaches problems.

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `autogen` | Multi-agent framework |
| `python-dotenv` | Load environment variables |
| `pyyaml` | Parse YAML config |

## ⚠️ Safety Notes

- The agent executes code locally on your machine
- Use `use_docker=True` for untrusted tasks
- Review the `coding/` directory for generated files
- The agent has a `max_consecutive_auto_reply=10` limit

## 📺 Video Tutorial

Watch the full tutorial to understand the concepts in depth!

## 💡 Example Tasks to Try

1. **Data Processing**: "Read a CSV file and calculate statistics"
2. **Web Scraping**: "Fetch a webpage and extract all links"
3. **File Operations**: "Create a folder structure for a Python project"
4. **API Calls**: "Call a public API and format the response"

## 🤝 Contributing

Feel free to:
- Add more complex example tasks
- Improve error handling
- Add new capabilities

---

**Part of [MyCampus Hub](../README.md) 🎓**
