# main.py
import autogen
import yaml
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Step 1: Load LLM Configuration from YAML
# This function searches for a 'config.yaml' file in the current directory and
# loads the LLM configurations. It uses the OLLAMA_API_KEY from the .env file.
# 2. Load Configuration from YAML
def load_config(yaml_path="config.yaml"):
    with open(yaml_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    # Substitute environment variables in the YAML data
    for item in config_data['config_list']:
        item['model'] = os.getenv('OLLAMA_MODEL', item['model'])
        item['base_url'] = os.getenv('OLLAMA_BASE_URL', item['base_url'])
        
    return config_data['config_list']

config_list = load_config()
# The Assistant (The "Reasoning" Engine)
llm_config = {
    "config_list": config_list,
    "timeout": 120,
}


# Step 2: Create the Assistant Agent (The "Thinker" and "Coder")
# This agent uses the Ollama model to reason, plan, and generate code.
assistant = autogen.AssistantAgent(
    name="Assistant",
    llm_config=llm_config,
    system_message="""You are a helpful AI assistant.
    You solve tasks by generating Python code.
    You will reason about the task, write a plan, and then write a ```python block with the code to execute.
    After the user proxy agent executes the code, you will analyze the result and decide if the task is complete.
    If the task is not complete, you will reason about the next step and provide new code.
    If an error occurs, analyze the error and provide corrected code.
    When the task is fully complete, reply with only the word TERMINATE."""
)

# Step 3: Create the User Proxy Agent (The "Executor")
# This agent acts as a proxy for the user. It executes code blocks sent by the assistant.
# 'code_execution_config' directs it to use a local command-line environment.
# The 'work_dir' is a directory where the agent can save files.
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    human_input_mode="NEVER",  # Never ask for human input, fully automated
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding",  # Directory to store files and code
        "use_docker": False,   # Set to True if you have Docker and want to run code in a container
    },
)

# Step 4: Initiate the Chat and Start the ReAct Loop
# The user_proxy sends the initial task to the assistant.
# The agents will then converse back and forth to solve the task.
task = """
Find the current date and time.
Write this information to a file named 'current_time.txt'.
After that, list the files in the current directory to confirm the file was created.
"""

print(f"Starting task: {task}")

user_proxy.initiate_chat(
    assistant,
    message=task,
)