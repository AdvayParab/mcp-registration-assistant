import asyncio
import os
import json
import streamlit as st
from dotenv import load_dotenv
from loguru import logger
from openai import AsyncOpenAI
import httpx

load_dotenv()

# OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an AI-based registration assistant. Your capabilities include:
- Registering users with name, email, and date of birth
- Showing all registered user data

When registering users:
- Ask for name, email, and date of birth
- Date of birth should be in YYYY-MM-DD format
- Validate all information before registration

When showing registrations:
- Display all registered users in a clear format
"""

# FastMCP server URL
MCP_BASE_URL = "http://127.0.0.1:8000"

# -------------------------
# HTTP-based MCP client
# -------------------------
async def call_tool_http(tool_name, arguments):
    """Call a tool on FastMCP server via HTTP."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client_http:
            # Try different possible endpoints for FastMCP
            possible_urls = [
                f"{MCP_BASE_URL}/mcp/tools/{tool_name}/call",
                f"{MCP_BASE_URL}/tools/{tool_name}/call", 
                f"{MCP_BASE_URL}/call/{tool_name}",
                f"{MCP_BASE_URL}/{tool_name}"
            ]
            
            for url in possible_urls:
                try:
                    resp = await client_http.post(
                        url,
                        json={"arguments": arguments}
                    )
                    if resp.status_code == 200:
                        return resp.json()
                except:
                    continue
            
            # If all URLs failed, try to get available endpoints
            try:
                resp = await client_http.get(f"{MCP_BASE_URL}/mcp")
                st.error(f"Tool endpoint not found. Server response: {resp.text}")
            except:
                st.error("Cannot connect to MCP server. Make sure it's running on port 8000.")
            
            return {"error": f"Tool {tool_name} not found on server"}
            
    except httpx.RequestError as e:
        st.error(f"Connection error: {e}")
        return {"error": f"Failed to connect to MCP server: {e}"}
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {e}"}

# -------------------------
# Main Streamlit app
# -------------------------
async def main():
    st.title("🔧 Registration Assistant")
    st.markdown("Add new registrations or view existing ones using natural language!")
    
    # Debug section
    with st.sidebar:
        st.header("🔍 Debug Info")
        if st.button("Test MCP Connection"):
            with st.spinner("Testing connection..."):
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client_http:
                        # Test basic connection
                        resp = await client_http.get("http://127.0.0.1:8000")
                        st.success(f"✅ Server is running (Status: {resp.status_code})")
                        
                        # Try to get available endpoints
                        try:
                            resp = await client_http.get("http://127.0.0.1:8000/mcp")
                            st.info(f"MCP endpoint response: {resp.text[:200]}...")
                        except:
                            pass
                            
                except Exception as e:
                    st.error(f"❌ Cannot connect to server: {e}")
    
    # Session state initialization
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Display previous messages (skip system message)
    for msg in st.session_state.messages[1:]:  # Skip system message
        role = msg["role"]
        if role == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif role == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
        elif role == "function":
            with st.chat_message("assistant"):
                st.markdown(f"🔧 Tool `{msg['name']}` executed:\n```\n{msg['content']}\n```")

    # Handle user input
    user_input = st.chat_input("Type your message... (e.g., 'Register John Doe with email john@example.com, DOB 1990-01-15' or 'Show all registrations')")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Tool definitions that match your actual MCP server
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_registration",
                "description": "Add a new user registration with name, email, and date of birth",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Full name of the person"
                        },
                        "email": {
                            "type": "string", 
                            "description": "Email address"
                        },
                        "dob": {
                            "type": "string",
                            "description": "Date of birth in YYYY-MM-DD format"
                        }
                    },
                    "required": ["name", "email", "dob"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "get_all_registration",
                "description": "Get all user registrations",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]

    # Ask OpenAI for completion (with tools/functions)
    with st.spinner("Thinking..."):
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                tools=tools,
                tool_choice="auto"
            )
        except Exception as e:
            st.error(f"OpenAI API Error: {e}")
            return

    message = response.choices[0].message

    # If OpenAI decides to call a tool
    if hasattr(message, "tool_calls") and message.tool_calls:
        # Add the assistant message with tool calls
        st.session_state.messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": message.tool_calls
        })
        
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            with st.spinner(f"Executing {tool_name}..."):
                tool_response = await call_tool_http(tool_name, tool_args)
            
            if "error" in tool_response:
                tool_output = f"Error: {tool_response['error']}"
            else:
                tool_output = tool_response["content"][0]["text"]

            # Store function result
            st.session_state.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": tool_output
            })

            with st.chat_message("assistant"):
                st.markdown(f"🔧 Executed `{tool_name}`:\n```\n{tool_output}\n```")

        # Follow-up AI response after tool calls
        with st.spinner("Generating response..."):
            try:
                followup_response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages,
                )
                final_message = followup_response.choices[0].message
                st.session_state.messages.append({"role": "assistant", "content": final_message.content})
                with st.chat_message("assistant"):
                    st.markdown(final_message.content)
            except Exception as e:
                st.error(f"Error generating follow-up response: {e}")

    else:
        # Normal AI response
        st.session_state.messages.append({"role": "assistant", "content": message.content})
        with st.chat_message("assistant"):
            st.markdown(message.content)

# -------------------------
# Run Streamlit app
# -------------------------
def run_app():
    # Check if we're in an async context
    try:
        loop = asyncio.get_running_loop()
        # If we're in a running loop, create a task
        task = asyncio.create_task(main())
    except RuntimeError:
        # No running loop, so run our main function
        asyncio.run(main())

# Main entry point
if __name__ == "__main__":
    # For direct execution
    asyncio.run(main())
else:
    # For streamlit run app.py
    asyncio.run(main())