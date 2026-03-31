FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# إعداد متغيرات البيئة لـ FastMCP لكي يسمع للخارج
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
# تأكد من أن الـ Output يظهر فوراً في الـ Logs
ENV PYTHONUNBUFFERED=1 

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY . .

# تشغيل السيرفر عبر uv مع التأكد من استخدام البيئة المثبتة
CMD ["uv", "run", "python", "Odoo_Manager_MCP.py"]