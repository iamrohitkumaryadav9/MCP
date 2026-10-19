"""
Chapter 3 - LLM agent (Gemini) that uses MCP tools through LLM tool calling.

1. MultiServerMCPClient connects to our MCP server and turns its tools into
   LangChain tools (name + description + JSON schema).
2. create_agent runs the agent loop: Gemini reads the question, decides which
   tool to call with which arguments, we run it via MCP, Gemini reads the
   result, and repeats until it can answer.

Setup:  uv add langchain-google-genai
        set GOOGLE_API_KEY=your_key        (Windows CMD)
        $env:GOOGLE_API_KEY="your_key"     (PowerShell)
Run:    uv run Chapter3/3_gemini_agent.py "Which devices failed?"
"""
import asyncio
import os
import sys
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

SERVER = Path(__file__).resolve().parent / "1_rf_typed_server.py"
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

SYSTEM_PROMPT = (
    "You help RF engineers analyse device test results. "
    "Always use the tools to get numbers; never guess or invent values. "
    "If the tools can't answer the question, say so."
)


def text_of(message) -> str:
    return str(message.text)


async def main() -> None:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Set the GOOGLE_API_KEY environment variable first.")

    client = MultiServerMCPClient({
        "rf": {"transport": "stdio", "command": sys.executable, "args": [str(SERVER)]},
    })
    tools = await client.get_tools()
    print("Tools given to Gemini:", [t.name for t in tools], "\n")

    # timeout + max_retries: fail fast with a clear error instead of hanging silently
    llm = ChatGoogleGenerativeAI(
        model=MODEL, google_api_key=api_key, temperature=0, timeout=120, max_retries=3
    )
    print("Testing Gemini connection...")
    print("Gemini says:", llm.invoke("Reply with the single word: ready").content, "\n")
    agent = create_agent(llm, tools=tools, system_prompt=SYSTEM_PROMPT)

    question = " ".join(sys.argv[1:]) or (
        "Which devices failed any test? Also compare DEV-002 on n77 vs n78."
    )
    print("Question:", question, "\n")

    result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})

    # Show the agent's reasoning trace: which tools it chose and what came back
    for msg in result["messages"]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for call in msg.tool_calls:
                print(f"-> Gemini calls {call['name']}({call['args']})")
        elif isinstance(msg, ToolMessage):
            print(f"<- result: {text_of(msg)[:200]}")

    print("\nAnswer:", text_of(result["messages"][-1]))


if __name__ == "__main__":
    asyncio.run(main())
