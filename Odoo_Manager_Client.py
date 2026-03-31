import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run_client():
    # الرابط الذي قمت بتشغيله في Docker
    url = "http://localhost:9090/sse" #/sse
    print(f"Connecting to MCP server at {url}...")
    
    async with sse_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            try:
                # 1. تهيئة الاتصال
                await session.initialize()
                
                # 2. استعراض الأدوات (Tools) المتاحة في سيرفر Odoo
                tools = await session.list_tools()
                print("الأدوات المتاحة في السيرفر:")
                for tool in tools:
                    print(f"- {tool.name}: {tool.description}")

                # 3. مثال لاستدعاء أداة (تأكد من اسم الأداة من النتائج السابقة)
                # result = await session.call_tool("search_partners", arguments={"name": "Ahmed"})
                # print(result)
                print("Connected to MCP server successfully!")  
            except Exception as e:
                print(f"Failed to connect to MCP server: {e}")
                return
                        


if __name__ == "__main__":
    asyncio.run(run_client())