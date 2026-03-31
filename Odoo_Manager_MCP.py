import os
from dotenv import load_dotenv
import odoorpc
from mcp.server.fastmcp import FastMCP

# مثال لإضافة قيود على المدخلات
from pydantic import Field, PositiveFloat

import logging
from datetime import datetime

# 1. تحميل الإعدادات الأمنية من .env
load_dotenv()

# 2. تهيئة خادم MCP (سيكون اسم الخادم "Odoo-Manager")
mcp = FastMCP("Odoo-Manager")

# 3. إعداد الاتصال بـ Odoo (مرة واحدة ليستخدمه الخادم)
def get_odoo_client():
    odoo = odoorpc.ODOO(os.getenv('ODOO_URL'), protocol='jsonrpc+ssl', port=443)
    odoo.login(
        os.getenv('ODOO_DB'), 
        os.getenv('ODOO_USER'), 
        os.getenv('ODOO_API_KEY')
    )
    return odoo


# 4. إعداد التكوينات الأساسية للـ Logging
# إعداد الـ Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Odoo-MCP")

# إضافة الـ File Handler بشكل يدوي لضمان التحكم
file_handler = logging.FileHandler("mcp_odoo_audit.log", mode='a', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# سطر اختبار يظهر فور تشغيل السيرفر
logger.info("=== تم تشغيل سيرفر MCP Odoo بنجاح وبانتظار الأوامر ===")

# تأكيد الكتابة على القرص
file_handler.flush()

# --- الـ Tool الأولى: جلب المنتجات ---

@mcp.tool()
def list_inventory_products() -> str:
    """
    تستعلم هذه الأداة عن قائمة المنتجات المتاحة في مخزن Odoo 
    وتعيد أسمائها والكميات المتاحة حالياً.
    """
    try:
        odoo = get_odoo_client()
        # البحث عن كل المنتجات في المستودع
        product_ids = odoo.env['product.template'].search([])
        products = odoo.env['product.template'].browse(product_ids)
        
        if not products:
            return "المخزن فارغ حالياً."
        
        inventory_report = "تقرير المخزون الحالي:\n"
        for p in products:
            inventory_report += f"- {p.name}: الكمية ({p.qty_available})\n"
            
        return inventory_report
    except Exception as e:
        return f"خطأ أثناء الاتصال بـ Odoo: {str(e)}"

@mcp.tool()
def list_inventory_product(prod_name: str = Field(description="name of the product"),) -> str:
    """
    تستعلم هذه الأداة عن خزون منتج محدد في مخزن Odoo 
    وتعيد أسمه والكميه المتاحة حالياً.
    """
    try:
        odoo = get_odoo_client()
        # البحث عن كل المنتجات في المستودع
        product_ids = odoo.env['product.template'].search([('name', 'in', [prod_name])])
        products = odoo.env['product.template'].browse(product_ids)
        
        if not products:
            return "المخزن فارغ حالياً."
        
        inventory_report = "تقرير المخزون الحالي:\n"
        for p in products:
            inventory_report += f"- {p.name}: الكمية ({p.qty_available})\n"
            
        return inventory_report
    except Exception as e:
        return f"خطأ أثناء الاتصال بـ Odoo: {str(e)}"
    
from pydantic import Field

@mcp.tool()
def update_product_quantity(
    prod_name: str = Field(description="اسم المنتج المراد تحديث كميته", min_length=2),
    new_quantity: PositiveFloat = Field(description="الكمية الجديدة التي سيتم وضعها في المخزن")
) -> str:
    """
    تستخدم هذه الأداة لتحديث كمية منتج معين في مخزن Odoo.
    تحذير: هذا التحديث يغير الرصيد الحالي مباشرة.
    """

    # تسجيل بداية العملية (Auditing)
    logger.info(f"محاولة تحديث المنتج: {prod_name} إلى كمية: {new_quantity}")
    file_handler.flush()
    try:
        odoo = get_odoo_client()
        
        # 1. البحث عن المنتج للحصول على الـ ID
        product_template_ids = odoo.env['product.template'].search([('name', '=', prod_name)])
        
        if not product_template_ids:
            return f"عذراً، لم أجد منتجاً باسم '{prod_name}' لتحديثه."

        # 2. الوصول للمنتج وتحديث الكمية
        # ملاحظة: في Odoo، تحديث الكمية يفضل أن يتم عبر 'product.product'
        product_variant_ids = odoo.env['product.product'].search([('product_tmpl_id', '=', product_template_ids[0])])
        
        if product_variant_ids:
            product = odoo.env['product.product'].browse(product_variant_ids[0])
            
            # تنفيذ التحديث (في النسخ الحديثة نستخدم دالة التحديث المباشر)
            product.write({'qty_available': new_quantity}) 
            # ملاحظة هندسية: بعض نسخ Odoo تتطلب Inventory Wizard، لكن odoorpc يسهل الكثير
            
            #return f"تم تحديث مخزون '{prod_name}' بنجاح إلى {new_quantity}."
            success_msg = f"تم تحديث {prod_name} بنجاح إلى {new_quantity}"
            logger.info(success_msg)
            file_handler.flush()
            return success_msg
        
        return "فشل التحديث: لم يتم العثور على Variant للمنتج."

    except Exception as e:
        #return f"حدث خطأ أثناء التحديث: {str(e)}"    
        # عند الفشل - تسجيل الخطأ بالتفصيل (Critical Error)
        error_msg = f"فشل تحديث {prod_name}: {str(e)}"
        logger.error(error_msg, exc_info=True) # exc_info تسجل الـ Stack Trace كاملاً
        file_handler.flush()
        return error_msg        
# تشغيل الخادم
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)