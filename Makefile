.PHONY: install test lint demo train app api docker

install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check .

demo:
	python scripts/generate_demo_data.py --rows 1500

train:
	python scripts/train.py --input data/generated/demo_train.csv --model-output artifacts/model_bundle.joblib --metrics-output artifacts/metrics.json

app:
	streamlit run app/Home.py

api:
	uvicorn api.main:app --reload --port 8000

docker:
	docker compose up --build
