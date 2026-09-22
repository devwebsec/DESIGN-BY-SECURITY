FROM python:3.12-slim

WORKDIR /opt/security-copilot

COPY . .

RUN python -m pip install --no-cache-dir --disable-pip-version-check "pip==26.2.0" "setuptools>=78.1.1" \
    && useradd --create-home --uid 10001 copilot \
    && mkdir -p /opt/security-copilot/data \
    && chown -R copilot:copilot /opt/security-copilot
