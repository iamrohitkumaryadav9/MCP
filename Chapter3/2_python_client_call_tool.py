"""
Chapter 3 - Plain MCP client that discovers AND calls tools.

Flow: start server as a subprocess (stdio) -> initialize -> tools/list -> tools/call
"""
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).resolve().parent / "1_rf_typed_server.py"

server_params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])


def show(result) -> None:
    status = "ERROR" if result.isError else "OK"
    text = " ".join(c.text for c in result.content if hasattr(c, "text"))
    print(f"  [{status}] {text}\n")


async def main() -> None:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()  # handshake + capability negotiation

            # 1. Discover tools (tools/list)
            tools = await session.list_tools()
            print("Tools on the server:")
            for t in tools.tools:
                params = list(t.inputSchema.get("properties", {}))
                print(f"  - {t.name}({', '.join(params)}): {t.description}")
            print()

            # 2. Call a tool (tools/call)
            print("call get_device_stats(DEV-001, n77)")
            show(await session.call_tool(
                "get_device_stats", {"device_id": "DEV-001", "band": "n77"}))

            print("call find_failures(max_evm_pct=3.0)")
            show(await session.call_tool("find_failures", {"max_evm_pct": 3.0}))

            # 3. Invalid input: the schema rejects a band that doesn't exist
            print("call get_device_stats(DEV-001, n99)  <- invalid band")
            show(await session.call_tool(
                "get_device_stats", {"device_id": "DEV-001", "band": "n99"}))


if __name__ == "__main__":
    asyncio.run(main())
