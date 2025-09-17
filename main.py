from fastmcp import FastMCP
from tools import add_registrations, get_all_registrations
from tools.add_registrations import add_registration
from tools.get_all_registrations import get_all_registration

app = FastMCP("registration-server")

# Register tools
app.tool(description="Add a new registration")(add_registration)
app.tool(description="Get all registrations")(get_all_registration)

if __name__ == "__main__":
    print("🚀 FastMCP Registration Server started at http://127.0.0.1:8000/mcp")
    app.run(
        transport="http",
        host="127.1.0.1",
        port=8000,
        path="/mcp"
    )
