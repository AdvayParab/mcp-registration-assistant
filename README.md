# 🔧 Registration Assistant

An AI-powered registration system built with **MCP (Model Context Protocol)** tools, **FastAPI**, and **Streamlit**. This application allows users to register new users and view existing registrations using natural language interactions with an AI assistant.

## 🌟 Features

- **Natural Language Interface**: Chat with an AI assistant to manage registrations
- **User Registration**: Add new users with name, email, and date of birth
- **Data Validation**: Comprehensive validation for all input fields
- **View Registrations**: Display all registered users
- **Duplicate Prevention**: Prevents registration with existing email addresses
- **Real-time Chat Interface**: Interactive Streamlit-based UI
- **RESTful API**: FastAPI backend with automatic documentation

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Streamlit     │────│   FastAPI    │────│   MCP Tools     │
│   Frontend      │    │   HTTP API   │    │   (Business     │
│   (app.py)      │    │   (api.py)   │    │    Logic)       │
└─────────────────┘    └──────────────┘    └─────────────────┘
         │                       │                    │
         │                       │                    │
    ┌────▼────┐            ┌─────▼─────┐        ┌─────▼─────┐
    │ OpenAI  │            │ Pydantic  │        │   CSV     │
    │   API   │            │ Validation│        │ Storage   │
    └─────────┘            └───────────┘        └───────────┘
```

## 📁 Project Structure

```
registration-assistant/
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (create this)
├── user_registrations.csv    # Data storage (auto-created)
│
├── app.py                    # Streamlit frontend application
├── api.py                    # FastAPI HTTP endpoints
├── main.py                   # FastMCP server (alternative)
├── manager.py                # Registration business logic
├── validator.py              # Input validation utilities
│
└── tools/                    # MCP Tools directory
    ├── __init__.py
    ├── add_registrations.py   # Add registration tool
    └── get_all_registrations.py # Get all registrations tool
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd registration-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

4. **Start the FastAPI server**
   ```bash
   # Option 1: Direct run
   python api.py
   
   # Option 2: Using uvicorn (recommended)
   uvicorn api:app --reload --host 127.0.0.1 --port 8000
   ```

5. **Start the Streamlit app** (in a new terminal)
   ```bash
   streamlit run app.py
   ```

6. **Access the applications**
   - **Streamlit App**: http://localhost:8501
   - **FastAPI Docs**: http://127.0.0.1:8000/docs
   - **FastAPI API**: http://127.0.0.1:8000

## 📋 Requirements

Create a `requirements.txt` file with:

```
streamlit>=1.28.0
fastapi>=0.104.0
uvicorn>=0.24.0
openai>=1.3.0
httpx>=0.25.0
python-dotenv>=1.0.0
loguru>=0.7.0
pydantic>=2.0.0
mcp>=0.1.0
fastmcp>=0.1.0
```

## 🎯 Usage

### Using the Chat Interface

1. **Register a new user**:
   ```
   "Register John Doe with email john@example.com, DOB 1990-01-15"
   ```

2. **View all registrations**:
   ```
   "Show all registrations"
   "List all users"
   "Display registered users"
   ```

3. **Natural language queries**:
   ```
   "Add a new user named Jane Smith with email jane@test.com born on 1985-06-20"
   "I want to register someone"
   "Can you show me who's registered?"
   ```

### Using the API Directly

#### Add Registration
```bash
curl -X POST "http://127.0.0.1:8000/add_registration" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John Doe",
       "email": "john@example.com",
       "dob": "1990-01-15"
     }'
```

#### Get All Registrations
```bash
curl -X GET "http://127.0.0.1:8000/get_all_registrations"
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Data Storage

- **Format**: CSV file (`user_registrations.csv`)
- **Location**: Project root directory
- **Auto-creation**: File is created automatically on first registration
- **Fields**: Name, Email, Date_of_Birth, Registration_Date


## 🙏 Acknowledgments

- **OpenAI** for the ChatGPT API
- **Streamlit** for the excellent frontend framework
- **FastAPI** for the high-performance API framework
- **MCP Protocol** for the tool integration standards



---

