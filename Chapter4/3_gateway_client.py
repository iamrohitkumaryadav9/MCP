"""
Chapter 4 - Client that talks only to the gateway, yet reaches both backends.

Needs: RF server (port 8070) and gateway (port 8080) running.
Run:   uv run Chapter4/3_gateway_client.py
"""
import asyncio

from fastmcp import Client

GATEWAY_URL = "http://localhost:8080/mcp"


async def main() -> None:
    async with Client(GATEWAY_URL) as client:
        tools = await client.list_tools()
        print("Tools visible through the gateway:")
        for t in tools:
            print(f"  - {t.name}")
        print()

        result = await client.call_tool(
            "rf_get_device_stats", {"device_id": "DEV-003", "band": "B3"})
        print("rf_get_device_stats ->", result.data)

        result = await client.call_tool("demo_fetch", {})
        print("demo_fetch          ->", result.data)

        # demo_process exists on the backend but is not on the allow-list
        result = await client.call_tool("demo_process", {}, raise_on_error=False)
        print("demo_process        ->", "blocked:" if result.is_error else "", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
