.PHONY: install migrate test run health ready

install:
	pip install -e ".[dev]"

migrate:
	alembic upgrade head

test:
	pytest tests/ -v

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

health:
	curl -s http://localhost:8000/health | python -m json.tool

ready:
	curl -s http://localhost:8000/ready | python -m json.tool
