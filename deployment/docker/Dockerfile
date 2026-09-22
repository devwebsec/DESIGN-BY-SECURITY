FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /opt/security-copilot
COPY . .

RUN python -m pip install --no-cache-dir --disable-pip-version-check "pip==26.2.0" \
    && useradd --create-home --uid 10001 copilot \
    && mkdir -p /opt/security-copilot/data \
    && chown -R copilot:copilot /opt/security-copilot
USER copilot

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"

CMD ["python", "apps/server/server.py"]
