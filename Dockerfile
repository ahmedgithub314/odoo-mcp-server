# استخدام صورة uv الرسمية خفيفة الوزن
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# ضبط مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملفات الإعداد أولاً (للاستفادة من الـ Caching)
COPY pyproject.toml uv.lock ./

# تثبيت الاعتمادات دون الحاجة لإنشاء Virtual Env داخل الحاوية
RUN uv sync --frozen --no-install-project --no-dev

# نسخ باقي ملفات المشروع (سيرفر الـ MCP وملف الـ .env)
COPY . .

# تشغيل السيرفر باستخدام uv
CMD ["uv", "run", "Odoo_Manager_MCP.py"]