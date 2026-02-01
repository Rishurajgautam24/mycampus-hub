# Email AI Agent

A Multi-Tool AI Agent built with AutoGen that can perform calculations and send emails. This project demonstrates the ReAct (Reasoning + Acting) pattern where the AI assistant can plan, act using tools, observe results, and respond.

## Architecture

### Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User Query    │────▶│  AssistantAgent  │────▶│   LLM (Ollama)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               │ Plans & Decides
                               ▼
                        ┌──────────────────┐
                        │   UserProxyAgent │
                        │   (Tool Executor)│
                        └──────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
     ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
     │calculator_tool│  │send_email_tool│  │Code Executor│
     └─────────────┘   └─────────────┘   └─────────────┘
```

### Components

1. **AssistantAgent** (`ollama_assistant`)
   - The "brain" of the system
   - Reasons about user queries and decides which tool to use
   - Has access to two tools:
     - [`calculator_tool`](email-ai-agent/app.py:27) - Performs arithmetic operations
     - [`send_email_tool`](email-ai-agent/app.py:46) - Sends emails via Resend API

2. **UserProxyAgent** (`user_proxy`)
   - Executes tools suggested by the Assistant
   - Runs in automated mode (`human_input_mode="NEVER"`)
   - Also handles code execution when needed

3. **Tools**
   - **Calculator Tool**: Supports add, subtract, multiply, divide operations
   - **Send Email Tool**: Sends emails using Resend API with HTML support

4. **LLM Configuration**
   - Uses Ollama for local LLM inference
   - Configurable via environment variables and [`config.yaml`](email-ai-agent/config.yaml:1)

## Prerequisites

- Python 3.14 or higher
- [Ollama](https://ollama.com/) installed and running locally
- [Resend](https://resend.com/) API key for email functionality
- [uv](https://docs.astral.sh/uv/) for dependency management

## Installation

1. **Clone the repository and navigate to the project:**
   ```bash
   cd email-ai-agent
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

3. **Set up environment variables:**
   Create a `.env` file with the following:
   ```env
   # Ollama Configuration
   OLLAMA_MODEL=qwen2.5:14b
   OLLAMA_BASE_URL=http://localhost:11434/v1
   
   # Resend Email Configuration
   RESEND_API_KEY=your_resend_api_key_here
   DEFAULT_SENDER_EMAIL=your-verified-sender@yourdomain.com
   ```

4. **Configure the model in `config.yaml`:**
   ```yaml
   config_list:
     - model: "${OLLAMA_MODEL}"
       base_url: "${OLLAMA_BASE_URL}"
       api_key: "ollama"
       price: [0, 0]
       temperature: 0.1
       cache_seed: null
   ```

## Usage

### Running the Agent

```bash
uv run python app.py
```

### Example Tasks

The agent can handle different types of tasks by selecting the appropriate tool:

#### 1. Calculator Tasks
```python
task = "What is 125 multiplied by 8? Then subtract 50 from the result."
```

#### 2. Email Tasks
```python
task = "Send an email to user@example.com with subject 'Hello' and body 'This is a test email from my AI agent.'"
```

### How It Works

1. **User** sends a task to the [`UserProxyAgent`](email-ai-agent/app.py:90)
2. **Assistant** receives the message and plans the approach
3. **Assistant** calls the appropriate tool with arguments
4. **UserProxyAgent** executes the tool and returns the result
5. **Assistant** provides the final response
6. Conversation terminates when "TERMINATE" is returned

## Project Structure

```
email-ai-agent/
├── app.py              # Main application with agent setup
├── config.yaml         # LLM configuration
├── pyproject.toml      # Project dependencies
├── .env               # Environment variables (not in git)
└── README.md          # This file
```

## Dependencies

- [`autogen`](https://github.com/microsoft/autogen) - Multi-agent conversation framework
- [`resend`](https://github.com/resend/resend-python) - Email API client
- [`pyyaml`](https://pyyaml.org/) - YAML configuration parsing
- [`python-dotenv`](https://github.com/theskumar/python-dotenv) - Environment variable management

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OLLAMA_MODEL` | Ollama model to use | `qwen2.5:14b` |
| `OLLAMA_BASE_URL` | Ollama API endpoint | `http://localhost:11434/v1` |
| `RESEND_API_KEY` | Resend API key | `re_xxxxxxxx` |
| `DEFAULT_SENDER_EMAIL` | Verified sender email | `bot@yourdomain.com` |

## Customization

### Adding New Tools

To add a new tool to the agent:

1. Define the tool function with type annotations:
   ```python
   def my_new_tool(
       param: Annotated[str, "Parameter description"]
   ) -> str:
       # Tool implementation
       return result
   ```

2. Register the tool:
   ```python
   autogen.register_function(
       my_new_tool,
       caller=assistant,
       executor=user_proxy,
       name="my_new_tool",
       description="What this tool does"
   )
   ```

3. Update the assistant's system message to mention the new tool

## License

MIT
