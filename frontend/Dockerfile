FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.5.13 /uv /bin/uv

WORKDIR /frontend

ENV PYTHONPATH=/frontend

COPY ./uv.lock ./pyproject.toml /frontend/

RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip sync --system uv.lock

COPY frontend/ .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
