"""""Tool to get all registrations."""
from mcp.types import TextContent
from manager import RegistrationManager

# Single manager instance
registration_manager = RegistrationManager()

async def get_all_registration() -> list[TextContent]:
    """Tool to fetch all registrations via manager."""
    result = registration_manager.get_all_registrations()

    if result["success"]:
        registrations = result.get("data", [])
        if not registrations:
            msg = "ℹ️ No registrations found."
        else:
            msg = "**All Registrations:**\n\n"
            for i, reg in enumerate(registrations, 1):
                msg += (
                    f"{i}. {reg['Name']} | {reg['Email']} | "
                    f"{reg['Date_of_Birth']} | {reg['Registration_Date']}\n"
                )
    else:
        msg = f"❌ ERROR: {result['error']}"

    return [TextContent(type="text", text=msg)]
