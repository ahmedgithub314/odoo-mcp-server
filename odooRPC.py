import odoorpc
import os
from dotenv import load_dotenv
# إعدادات الاتصال
load_dotenv()
odoo = odoorpc.ODOO('umas.odoo.com', protocol='jsonrpc+ssl', port=443)

odoo_api_key = os.getenv("ODOO_API_KEY", "")
print(f"ODOO_API_KEY: {odoo_api_key}")
#your_api_key = "f7cfeebb71ab27c0d6386e257f6bbbfb8273719f" #"1eY8wawUfk5yiz83rFsmNJV9jognqoUq7"
your_email="eng.ahmed.cu.2011@gmail.com"
your_db_name = "umas"
# تسجيل الدخول (استخدم الـ API Key مكان الباسورد)
#odoo.login('your-db-name', 'your_email@example.com', 'your_api_key')
odoo.login(your_db_name, your_email, odoo_api_key)

# البحث عن المنتجات (Apple, Orange)
product_ids = odoo.env['product.template'].search([('name', 'in', ['Apple', 'Orange'])])
products = odoo.env['product.template'].browse(product_ids)

for p in products:
    print(f"Product: {p.name} | Quantity: {p.qty_available}")