PYTHON ?= python

install:
	$(PYTHON) -m pip install -e .[dev]

test:
	$(PYTHON) -m pytest

lint:
	ruff check src tests scripts app

download:
	$(PYTHON) scripts/run_pipeline.py --stage download

build:
	$(PYTHON) scripts/run_pipeline.py --stage all

snapshot:
	$(PYTHON) scripts/build_verified_snapshot.py

app:
	streamlit run app/streamlit_app.py
