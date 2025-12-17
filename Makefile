.PHONY: help install dev build start stop logs clean test

help:
	@echo "AI Community Platform - Available commands:"
	@echo ""
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Start development servers"
	@echo "  make build      - Build for production"
	@echo "  make start      - Start with Docker Compose"
	@echo "  make stop       - Stop Docker containers"
	@echo "  make logs       - View container logs"
	@echo "  make clean      - Remove containers and volumes"
	@echo "  make test       - Run tests"
	@echo "  make migrate    - Run database migrations"
	@echo "  make collect    - Trigger data collection"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	docker-compose up -d postgres redis elasticsearch
	@echo "Waiting for services..."
	sleep 5
	cd backend && uvicorn main:app --reload &
	cd frontend && npm run dev

build:
	docker-compose build

start:
	docker-compose up -d

stop:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	rm -rf backend/__pycache__
	rm -rf frontend/.next
	rm -rf frontend/node_modules

test:
	cd backend && pytest
	cd frontend && npm test

migrate:
	cd backend && alembic upgrade head

migrate-create:
	cd backend && alembic revision --autogenerate -m "$(msg)"

collect:
	cd backend && python -c "from app.tasks import collect_all; collect_all()"

shell:
	cd backend && python -c "from app.db.database import *; from app.models import *"
