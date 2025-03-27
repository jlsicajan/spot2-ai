FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.5.13 /uv /bin/uv

WORKDIR /backend

ENV PYTHONPATH=/backend

COPY ./uv.lock ./pyproject.toml /backend/

RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip sync --system uv.lock

COPY backend/ .

EXPOSE 8082

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]
