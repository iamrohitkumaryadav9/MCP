"""
Chapter 4 - MCP gateway: one endpoint in front of several MCP servers.

Clients connect only to the gateway (http://localhost:8080/mcp). The gateway
proxies to two backend servers and prefixes their tool names:
  rf_*    -> the HTTP RF server (Chapter4/1_rf_http_server.py, or its Docker container)
  demo_*  -> the Chapter1 stdio server (started by the gateway as a subprocess)

Because all traffic passes through one place, the gateway is where you add
shared controls. Here: logging every tool call, and a simple allow-list.

Start the RF server first (python Chapter4/1_rf_http_server.py, or Docker),
then: uv run Chapter4/2_mcp_gateway.py
"""
import os
import sys
import time
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.client.transports import StdioTransport
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.proxy import ProxyClient

RF_SERVER_URL = os.getenv("RF_SERVER_URL", "http://localhost:8070/mcp")
DEMO_SERVER = Path(__file__).resolve().parents[1] / "Chapter1" / "1_firstmcp_stdio_server.py"

# Only these tools may be called through the gateway (least privilege)
ALLOWED_TOOLS = {
    "rf_list_devices", "rf_get_device_stats", "rf_compare_bands", "rf_find_failures",
    "demo_fetch",
}


class AuditMiddleware(Middleware):
    """Blocks tools that aren't allowed, and logs each call with its duration."""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        name = context.message.name
        if name not in ALLOWED_TOOLS:
            print(f"[gateway] BLOCKED {name}")
            raise ToolError(f"Tool '{name}' is not allowed through this gateway.")
        start = time.perf_counter()
        result = await call_next(context)
        print(f"[gateway] {name}({context.message.arguments}) "
              f"took {(time.perf_counter() - start) * 1000:.0f} ms")
        return result


gateway = FastMCP("mcp-gateway")

rf_backend = FastMCP.as_proxy(ProxyClient(RF_SERVER_URL), name="rf-backend")
demo_backend = FastMCP.as_proxy(
    ProxyClient(StdioTransport(command=sys.executable, args=[str(DEMO_SERVER)])),
    name="demo-backend",
)

gateway.mount(rf_backend, prefix="rf")
gateway.mount(demo_backend, prefix="demo")
gateway.add_middleware(AuditMiddleware())

if __name__ == "__main__":
    gateway.run(transport="streamable-http", host="127.0.0.1", port=8080, show_banner=False)
