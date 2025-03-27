.PHONY: install build start stop restart format lint test logs backend frontend bash-backend bash-frontend reset

build:
	uv pip compile pyproject.toml --output-file uv.lock --generate-hashes
	uv pip sync uv.lock

build:
	docker-compose build

start:
	docker-compose up -d

stop:
	docker-compose down

restart:
	docker-compose down --remove-orphans && docker-compose up -d

format:
	uv pip install black --system && black .

lint:
	uv pip install flake8 --system && flake8 .

test:
	uv pip install pytest --system && pytest

logs:
	docker-compose logs -f

backend:
	docker-compose up -d backend

frontend:
	docker-compose up -d frontend

bash-backend:
	docker exec -it $(shell docker ps -qf "name=backend") /bin/sh

bash-frontend:
	docker exec -it $(shell docker ps -qf "name=frontend") /bin/sh

reset:
	docker-compose down --remove-orphans --volumes
	docker rmi $$(docker images -q)
	make build
