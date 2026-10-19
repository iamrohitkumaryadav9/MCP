from fastmcp import FastMCP

mcp=FastMCP()

@mcp.tool()
def fetch():
    ''' Use this tool to fetch data. '''
    #simulate fetching data from a database or an API
    return {"data": "Hello! MCP."}

@mcp.tool()

def process():
    ''' Use this tool to process data. '''
    #simulate processing data
    return {"processed_data": "Data has been processed."}


if __name__ == "__main__":
    mcp.run(transport="stdio")