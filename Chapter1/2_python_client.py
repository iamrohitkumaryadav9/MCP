import os
import sys
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import asyncio

#Path to the server script

mcp_server_script=os.path.join(os.path.dirname(os.path.abspath(__file__)), "1_firstmcp_stdio_server.py")

print(mcp_server_script)

# Create Server Parameters

server_params=StdioServerParameters(
    command=sys.executable,
    args=[str(mcp_server_script)],
)

#create a client session

async def main():
    async with stdio_client(server_params) as (read,write):

        async with ClientSession(read, write) as session:
            await session.initialize()
            #  Fetch the tools
            tools=await session.list_tools()
            print("Available tools:", tools)


if __name__ == "__main__":
    asyncio.run(main()) 