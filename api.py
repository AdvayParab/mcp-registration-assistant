from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tools.add_registrations import add_registration
from tools.get_all_registrations import get_all_registration

app = FastAPI(title="Registration API", description="API for user registration management")

# Define request model
class AddRegistrationRequest(BaseModel):
    name: str
    email: str
    dob: str

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Registration API",
        "endpoints": {
            "add_registration": "POST /add_registration",
            "get_all_registrations": "GET /get_all_registrations"
        }
    }

@app.post("/add_registration")
async def add_registration_http(request: AddRegistrationRequest):
    """Add a new user registration."""
    try:
        # Call your existing MCP tool function with individual parameters
        response = await add_registration(request.name, request.email, request.dob)
        
        # Return the response
        return {"result": [tc.text for tc in response]}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@app.get("/get_all_registrations")
async def get_all_registrations_http():
    """Get all user registrations."""
    try:
        # Call your existing MCP tool function
        response = await get_all_registration()
        
        # Return the response
        return {"result": [tc.text for tc in response]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch registrations: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Registration API"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FastAPI Registration Server...")
    print("📡 API will be available at: http://127.0.0.1:8000")
    print("📚 API docs at: http://127.0.0.1:8000/docs")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)