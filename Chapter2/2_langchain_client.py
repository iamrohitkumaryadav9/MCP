from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import sys
from pathlib import Path

mcp_server_script = Path(__file__).resolve().parents[1] / "Chapter1" / "1_firstmcp_stdio_server.py"

async def main():
    client = MultiServerMCPClient(
        {
            "data_fetch_mcp_stdio": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(mcp_server_script)],
            },
            "data_fetch_mcp_http": {
                "transport": "streamable-http",
                "url": "http://localhost:8050/mcp",
            }
        }
    )

    tools = await client.get_tools()
    print("Available tools:", tools)

if __name__ == "__main__":
    asyncio.run(main())

