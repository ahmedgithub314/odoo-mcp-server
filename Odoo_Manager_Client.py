import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run_odoo_task():
    # الرابط الذي يوفره Docker على جهازك
    url = "http://localhost:8000/sse"
    
    print("🔄 جاري الاتصال بسيرفر Odoo MCP داخل Docker...")
    
    async with sse_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 1. تهيئة الاتصال (Handshake)
            await session.initialize()
            print("✅ متصل!")

            # 2. تجربة أداة جلب كافة المنتجات
            print("\n📦 جلب تقرير المخزون...")
            inventory = await session.call_tool("list_inventory_products")
            print(inventory.content[0].text)

            # 3. تجربة تحديث كمية منتج (اختياري - تأكد من اسم المنتج)
            # print("\n🔧 تحديث كمية منتج...")
            # update_result = await session.call_tool(
            #     "update_product_quantity", 
            #     arguments={"prod_name": "اسم المنتج هنا", "new_quantity": 50.0}
            # )
            # print(update_result.content[0].text)

if __name__ == "__main__":
    try:
        asyncio.run(run_odoo_task())
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")