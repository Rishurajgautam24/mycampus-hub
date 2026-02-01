import os
import resend
import yaml
import autogen
from dotenv import load_dotenv
from typing import Annotated, Literal

# ============================================================================
# 1. ENVIRONMENT SETUP
# ============================================================================

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")


# ============================================================================
# 2. CONFIGURATION LOADER
# ============================================================================

def load_config(yaml_path="config.yaml"):
    """Load and configure LLM settings from YAML file."""
    with open(yaml_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    # Substitute environment variables
    for item in config_data['config_list']:
        item['model'] = os.getenv('OLLAMA_MODEL', item['model'])
        item['base_url'] = os.getenv('OLLAMA_BASE_URL', item['base_url'])
        
    return config_data['config_list']


config_list = load_config()
llm_config = {
    "config_list": config_list,
    "timeout": 120,
}


# ============================================================================
# 3. TOOL DEFINITIONS
# ============================================================================

def calculator_tool(
    a: Annotated[int, "The first number"], 
    b: Annotated[int, "The second number"], 
    operation: Annotated[Literal["add", "subtract", "multiply", "divide"], "The operation to perform"]
) -> str:
    """Perform basic arithmetic operations."""
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


def format_email_body(subject: str, body: str) -> str:
    """Create professional HTML email body using email_formatter agent."""
    temp_assistant = autogen.AssistantAgent(
        name="temp_formatter",
        system_message="""You are an Email Body Formatter Agent.
        Create a professional HTML email body with inline CSS styling.
        Include a header, body content, and footer with signature.
        Sender name: "RISHU", Designation: "AI Specialist"
        Return ONLY the HTML content, followed by 'TERMINATE'.""",
        llm_config=llm_config,
    )
    
    temp_user = autogen.UserProxyAgent(
        name="temp_user",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        code_execution_config={"use_docker": False},  # Fixed: Added use_docker: False
    )
    
    format_request = f"""Format this into professional HTML:
    
Subject: {subject}
Body: {body}

Create professional HTML with header, styled content, and signature.
Return ONLY the HTML."""
    
    temp_user.initiate_chat(
        temp_assistant, 
        message=format_request, 
        clear_history=True
    )
    
    # Extract HTML from response
    last_message = temp_assistant.chat_messages[temp_user][-1]["content"] if temp_assistant.chat_messages.get(temp_user) else ""
    html_content = last_message.replace("TERMINATE", "").strip()
    
    return html_content if html_content else f"<p>{body}</p>"


def send_formatted_email_tool(
    to: Annotated[str, "The recipient's email address"],
    subject: Annotated[str, "The subject of the email"],
    body: Annotated[str, "The body content of the email"]
) -> str:
    """Send a professionally formatted HTML email."""
    try:
        # Format email body with professional HTML
        html_body = format_email_body(subject, body)
        
        # Send email
        params = {
            "from": os.getenv("DEFAULT_SENDER_EMAIL"),
            "to": [to],
            "subject": subject,
            "html": html_body,
        }
        response = resend.Emails.send(params)
        
        return {
            "status": "success", 
            "message_id": response.get("id"), 
            "message": "Email sent successfully!"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================================
# 4. AGENT CREATION
# ============================================================================

# Main Assistant Agent
assistant = autogen.AssistantAgent(
    name="assistant",
    system_message="""You are a helpful AI assistant with access to tools:
    
    1. calculator_tool - Perform arithmetic operations (add, subtract, multiply, divide)
    2. send_formatted_email_tool - Send professionally formatted HTML emails
    
    WORKFLOW:
    1. PLAN: Determine what tool is needed
    2. ACT: Call the appropriate function
    3. OBSERVE: Wait for the result
    4. RESPOND: Provide the final answer
    
    Return 'TERMINATE' when the task is complete.""",
    llm_config=llm_config,
)

# User Proxy Agent (Executes tools)
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"use_docker": False},  # Fixed: Set use_docker to False
)


# ============================================================================
# 5. REGISTER TOOLS
# ============================================================================

autogen.register_function(
    calculator_tool,
    caller=assistant,
    executor=user_proxy,
    name="calculator_tool",
    description="A calculator that can add, subtract, multiply, or divide two numbers."
)

autogen.register_function(
    send_formatted_email_tool,
    caller=assistant,
    executor=user_proxy,
    name="send_formatted_email_tool",
    description="Send a professionally formatted HTML email."
)


# ============================================================================
# 6. MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Get task from user
    task = input("Enter your task: ")
    
    print(f"\n{'='*60}")
    print(f"Starting ReAct Agent with task: {task}")
    print(f"{'='*60}\n")
    
    # Start the conversation
    user_proxy.initiate_chat(
        assistant,
        message=task
    )
    
    print(f"\n{'='*60}")
    print("Task completed!")
    print(f"{'='*60}")