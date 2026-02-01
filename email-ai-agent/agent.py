import os
import resend
import yaml
import autogen
from dotenv import load_dotenv
from typing import Annotated, Literal

# 1. Load Environment Variables
load_dotenv()

# Initialize Resend with API key
resend.api_key = os.getenv("RESEND_API_KEY")

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

# 3. Define the Tool (The "Act" part of ReAct)
# We will create a simple calculator tool.
def calculator_tool(
    a: Annotated[int, "The first number"], 
    b: Annotated[int, "The second number"], 
    operation: Annotated[Literal["add", "subtract", "multiply", "divide"], "The operation to perform"]
) -> str:
    if operation == "add":
        return f"{a} + {b} = {a + b}"
    elif operation == "subtract":
        return f"{a} - {b} = {a - b}"
    elif operation == "multiply":
        return f"{a} * {b} = {a * b}"
    elif operation == "divide":
        if b == 0:
            return "Error: Division by zero"
        return f"{a} / {b} = {a / b}"
    else:
        return "Error: Invalid operation"

# Define a send email tool
def send_email_tool(
    to: Annotated[str, "The recipient's email address"],
    subject: Annotated[str, "The subject of the email"],
    body: Annotated[str, "The body content of the email (can include HTML)"]
) -> str:
    try:
        params = {
            "from": os.getenv("DEFAULT_SENDER_EMAIL"),  # Replace with your verified sender email
            "to": [to],
            "subject": subject,
            "html": f"<p>{body}</p>",
        }
        response = resend.Emails.send(params)
        return {"status": "success", "message_id": response.get("id"), "message": "Email sent successfully. Task complete."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# 4. Create the Agents

# The Assistant (The "Reasoning" Engine)
llm_config = {
    "config_list": config_list,
    "timeout": 120,
}

assistant = autogen.AssistantAgent(
    name="ollama_assistant",
    system_message="""You are a helpful AI assistant.
    You have access to two tools:
    1. calculator_tool - A calculator that can add, subtract, multiply, or divide two numbers.
    2. send_email_tool - Send an email to a recipient with a subject and body.
    
    To answer questions, you must:
    1. PLAN: Think about what tool is needed.
    2. ACT: Call the appropriate function with the correct arguments.
    3. OBSERVE: Wait for the result provided by the user proxy.
    4. RESPONSE: Provide the final answer based on the result.
    Return 'TERMINATE' when the task is complete.""",
    llm_config=llm_config,
)

# The User Proxy (The "Actor"/Executor)
# This agent executes the code/tools suggested by the assistant.
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER", # Automated loop
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "coding", "use_docker": False},
)

# 5. Register the Tools
# This registers the function so the Assistant knows it exists and the User Proxy knows how to execute it.
autogen.register_function(
    calculator_tool,
    caller=assistant,
    executor=user_proxy,
    name="calculator_tool",
    description="A simple calculator that can add, subtract, multiply, or divide two numbers."
)

autogen.register_function(
    send_email_tool,
    caller=assistant,
    executor=user_proxy,
    name="send_email_tool",
    description="Send an email to a recipient with a subject and body. Use this when the user asks to send an email."
)

# 6. Start the Interaction
# Example task using calculator tool
task = input("Enter your task for the AI agent: ")

# Example task using send_email tool (uncomment to use)
# task = "Send an email to user@example.com with subject 'Hello' and body 'This is a test email from my AI agent.'"

print(f"Starting ReAct loop with task: {task}\n" + "-"*50)

user_proxy.initiate_chat(
    assistant,
    message=task
)