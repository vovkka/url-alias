.PHONY: migrate-generate migrate-up build up down logs ps start-dev destroy install run-local install-pre-commit run-pre-commit setup-dev


APP_CONTAINER_NAME ?= web


migrate-generate:
	@echo "Debug: message variable is [$(message)]"
ifndef message
	$(error message is not set. Usage: make migrate-generate message="your_migration_message")
endif
	@echo "Generating migration: $(message)"
	@docker compose run --rm -w /app migrate uv run alembic revision --autogenerate -m "$(message)"

migrate-up:
	@echo "Applying migrations..."
	@docker compose run --rm migrate
	@echo "Migrations applied."


build:
	@echo "Building Docker images..."
	@docker compose build

up:
	@echo "Starting Docker containers..."
	@docker compose up -d

down:
	@echo "Stopping Docker containers..."
	@docker compose down

logs:
	@echo "Showing logs for $(APP_CONTAINER_NAME)..."
	@docker compose logs -f $(APP_CONTAINER_NAME)

ps:
	@echo "Current Docker container status:"
	@docker compose ps

start-dev:
	make migrate-up
	make up
	make logs

destroy:
	@echo "Destroying all containers, networks, and volumes..."
	@docker compose down -v 

install-pre-commit:
	@echo "Installing pre-commit hooks..."
	@uv add --dev pre-commit
	@uv run pre-commit install
	@echo "Pre-commit hooks installed successfully."

run-pre-commit:
	@echo "Running pre-commit on all files..."
	@uv run pre-commit run --all-files
