import asyncio
import os
import json
import streamlit as st
from dotenv import load_dotenv
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

# server URL (change port if needed)
BASE_URL = "http://127.0.0.1:8000"

# -------------------------
# HTTP client
# -------------------------
async def call_api_tool(tool_name, arguments):
    """Call tools via your endpoints."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            if tool_name == "add_registration":
                # Call POST /add_registration
                response = await http_client.post(
                    f"{BASE_URL}/add_registration",
                    json={
                        "name": arguments.get("name"),
                        "email": arguments.get("email"),
                        "dob": arguments.get("dob")
                    }
                )
                response.raise_for_status()
                result = response.json()
                return {"content": [{"text": result["result"][0]}]}
                
            elif tool_name == "get_all_registration":
                # Call GET /get_all_registrations
                response = await http_client.get(f"{BASE_URL}/get_all_registrations")
                response.raise_for_status()
                result = response.json()
                return {"content": [{"text": result["result"][0]}]}
                
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except httpx.RequestError as e:
        return {"error": f"Request failed: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

# -------------------------
# Main Streamlit app
# -------------------------
async def main():
    st.title("🔧 Registration Assistant")
    st.markdown("Add new registrations or view existing ones using natural language!")
   
    # Debug section
    with st.sidebar:
        st.header("🔍 API Status")
        if st.button("Test API Connection"):
            with st.spinner("Testing connection..."):
                try:
                    async with httpx.AsyncClient(timeout=10.0) as http_client:
                        # Test basic connection
                        resp = await http_client.get(f"{BASE_URL}/docs")
                        if resp.status_code == 200:
                            st.success("✅ API server is running!")
                            st.info("📚 API docs available at /docs")
                        else:
                            st.warning(f"⚠️ Server responded with status {resp.status_code}")
                except Exception as e:
                    st.error(f"❌ Cannot connect to API server: {e}")
                    st.info("Make sure to run: uvicorn api:app --reload")
    
    # Session state initialization
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Display previous messages (skip system message)
    for msg in st.session_state.messages[1:]:
        role = msg["role"]
        if role == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif role == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
        elif role == "tool":
            with st.chat_message("assistant"):
                st.markdown(f"🔧 Tool executed:\n```\n{msg['content']}\n```")

    # Handle user input
    user_input = st.chat_input("Type your message... (e.g., 'Register John Doe with email john@example.com, DOB 1990-01-15' or 'Show all registrations')")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Tool definitions that match your endpoints
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

    # Ask OpenAI for completion
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

    # Handle tool calls
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
                # Call tool via API
                tool_response = await call_api_tool(tool_name, tool_args)
            
            if "error" in tool_response:
                tool_output = f"Error: {tool_response['error']}"
            else:
                tool_output = tool_response["content"][0]["text"]

            # Store tool result
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

# Run the app
if __name__ == "__main__":
    asyncio.run(main())
else:
    asyncio.run(main())