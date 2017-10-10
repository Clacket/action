test:
	make clean
	make lint
	python tests/update_test_db.py
	py.test --disable-pytest-warnings tests/

lint:
	@flake8 planning tests --exclude venv,docs

clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete

bootstrap:
	@pip install -r dev_requirements.txt
	make minimal
	@flake8 --install-hook git || true
	@git config --bool flake8.strict true || true

minimal:
	@pip install -r requirements.txt
	@pip install -e .

docs-build:
	@sphinx-build -b html docs/source docs/build

docs-run:
	@sphinx-autobuild -B docs/source docs/build

image-build:
	make clean
	@bash scripts/container_build.sh

run:
	@gunicorn -b 0.0.0.0:8000 action:app
