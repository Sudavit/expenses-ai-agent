# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN uv pip install --system .

# Stage 2: Runtime
FROM python:3.13-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.13/site-packages \
                    /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src/ ./src/
COPY pyproject.toml ./

RUN useradd --create-home --uid 501 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "expenses_ai_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
