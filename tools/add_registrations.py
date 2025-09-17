"""Tool to add a new registration via manager."""
from mcp.types import TextContent
from manager import RegistrationManager

# Single instance for state
registration_manager = RegistrationManager()

async def add_registration(name: str, email: str, dob: str) -> list[TextContent]:
    """
    Add a new user registration.
    """
    # Call manager
    result = registration_manager.add_registration(name, email, dob)

    # Format response
    if result["success"]:
        msg = (
            f"✅ SUCCESS: {result['message']}\n"
            f"Name: {result['data']['Name']}\n"
            f"Email: {result['data']['Email']}\n"
            f"DOB: {result['data']['Date_of_Birth']}\n"
            f"Registered: {result['data']['Registration_Date']}"
        )
    else:
        msg = f"❌ ERROR: {result['error']}"
        if "details" in result:
            msg += "\n" + "\n".join(result["details"])

    return [TextContent(type="text", text=msg)]
