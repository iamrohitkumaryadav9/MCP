# MCP_Start: MCP servers, clients, a Gemini agent and a gateway

Learning project for the Model Context Protocol (MCP) using FastMCP and LangChain.

## Structure

| Folder | What it shows |
|---|---|
| Chapter1 | First stdio MCP server, a raw Python MCP client, a LangChain client |
| Chapter2 | Streamable HTTP MCP server; one LangChain client connected to a stdio and an HTTP server at once |
| Chapter3 | Typed tools over fake RF test data; a client that **calls** tools; a **Gemini agent** that picks tools via LLM tool calling |
| Chapter4 | The RF server over HTTP + **Dockerfile**; an **MCP gateway** that fronts several servers with logging and an allow-list |

## Setup

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/).

```
uv sync
```

Only the Gemini agent (Chapter 3) needs an API key (PowerShell): `$env:GOOGLE_API_KEY="your_key"`
Optionally pick another model: `$env:GEMINI_MODEL="gemini-2.5-flash"`

## Run

Chapter 1 (each client starts the stdio server itself):
```
uv run Chapter1/2_python_client.py
uv run Chapter1/3_langchain_client.py
```

Chapter 2 (two terminals):
```
uv run Chapter2/1_http_mcp.py                 # HTTP server on port 8050
uv run Chapter2/2_langchain_client.py         # connects to stdio + HTTP servers
```

Chapter 3:
```
uv run Chapter3/2_python_client_call_tool.py
uv run Chapter3/3_gemini_agent.py "Which devices failed, and compare DEV-002 on n77 vs n78"
```

Chapter 4 (three terminals):
```
uv run Chapter4/1_rf_http_server.py          # or: docker build -t rf-mcp-server Chapter4
                                              #     docker run --rm -p 8070:8070 rf-mcp-server
uv run Chapter4/2_mcp_gateway.py
uv run Chapter4/3_gateway_client.py
```

Inspect any server: `npx @modelcontextprotocol/inspector`, then connect to `http://localhost:8070/mcp`.

## How it works (short)

- **Server** wraps functions as MCP tools. Type hints become a JSON schema; bad inputs are rejected before the code runs.
- **Client** connects, runs `initialize`, discovers tools with `tools/list`, runs them with `tools/call`.
- **Agent**: Gemini receives the tool schemas, decides which tool to call with which arguments, reads the result, and repeats until it can answer. The LLM never runs code itself.
- **Gateway**: one endpoint in front of many servers. Tool names get a prefix (`rf_`, `demo_`), and every call passes through shared controls: an allow-list and audit logging.

The RF data in Chapter 3/4 is made up for demonstration.
