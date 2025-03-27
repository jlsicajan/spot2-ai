# Spot2 AI – Conversational Real Estate Assistant

Spot2 AI is a web application that guides users through a simple conversation to collect real estate requirements, using OpenAI's language model behind the scenes.

It has a FastAPI backend that handles API requests and OpenAI interactions, and a Streamlit frontend for the user interface. The app is containerized using Docker, and dependency management is handled with uv.

---

## Installation and Setup

### 1. Requirements

Before starting, make sure you have:
- Docker and Docker Compose installed
- A valid OpenAI API key

### 2. Clone the project

```bash
git clone git@github.com:jlsicajan/spot2-ai.git
cd spot2-ai
```

### 3. Set up environment variables

Create a `.env` file at the root of the project and add your API key:

```env
OPENAI_API_KEY=your-openai-api-key
```

### 4. Install dependencies locally (optional)

If you're running the project outside Docker:

```bash
uv pip compile pyproject.toml --output-file uv.lock --generate-hashes
uv pip sync --system uv.lock
```

---

## Running the App

### 1. Start using Docker

Build and start all services:

```bash
make build
make start
```

### 2. Access the app

- Backend (FastAPI): http://localhost:8082/docs  
- Frontend (Streamlit): http://localhost:8501

### 3. Logs

To view logs:

```bash
docker logs $(docker ps -qf "name=backend")
docker logs $(docker ps -qf "name=frontend")
```

---

## Development

You can run backend and frontend services individually:

```bash
make backend
make frontend
```

To access the shell inside each container:

```bash
make bash-backend
make bash-frontend
```

Run code formatting, linting, and tests:

```bash
make format
make lint
make test
```

---

## Deployment

To deploy to a server manually:

```bash
docker-compose up -d --build
```
