PROJECT_NAME = webtraversallibrary
PROJECT_READABLE_NAME = "Web Traversal Library"
PYTHON ?= python3
SOURCE_FOLDER = wtl
ENV_NAME = .env-$(PROJECT_NAME)


.PHONY: env-create
env-create:
	$(PYTHON) -m venv $(ENV_NAME)
	make env-update
	#
	# Don't forget to activate the environment before proceeding! You can run:
	# source $(ENV_NAME)/bin/activate


.PHONY: env-update
env-update:
	bash -c "\
		. $(ENV_NAME)/bin/activate; \
		which python; \
		which pip; \
		pip install --upgrade -r requirements.txt; \
		pip freeze; \
	"


.PHONY: env-delete
env-delete:
	rm -rf $(ENV_NAME)


.PHONY: update
update:
	pip install --upgrade -r requirements.txt


.PHONY: build-all
build-all: clean gitinfo radon lint coverage docs build


.PHONY: clean
clean:
	rm -f .gitinfo
	rm -rf build dist *.egg-info
	find $(SOURCE_FOLDER) -name __pycache__ | xargs rm -rf
	find $(SOURCE_FOLDER) -name '*.pyc' -delete
	rm -rf reports .coverage
	rm -rf docs/build docs/source
	rm -rf .*cache


.PHONY: reformat
reformat:
	isort --recursive wtl examples tests
	black wtl examples tests


.PHONY: lint
lint:
	$(PYTHON) -m pycodestyle . --exclude '.env-*,setup.py,docs/*'
	isort --recursive --check-only wtl examples tests
	black --check wtl examples tests
	pylint $(SOURCE_FOLDER)
	pylint --disable=missing-docstring,no-self-use examples/*.py tests/*
	jshint $(SOURCE_FOLDER)
	mypy $(SOURCE_FOLDER)


.PHONY: test tests
test tests:
	$(PYTHON) -m pytest tests/ -m 'not system'


.PHONY: test_system
test_system:
	$(PYTHON) -m pytest tests/ -m 'system'


.PHONY: coverage
coverage:
	$(PYTHON) -m pytest tests/ -m 'not system' \
		--junitxml=reports/test-result-all.xml \
		--cov=$(SOURCE_FOLDER) \
		--cov-report term-missing \
		--cov-report html:reports/coverage-all.html \
		--cov-report xml:reports/coverage-all.xml


.PHONY: build
build:
	python setup.py --quiet sdist bdist_wheel


.PHONY: radon
radon:
	radon cc $(SOURCE_FOLDER) --min c
	xenon --max-absolute C --max-modules C --max-average A $(SOURCE_FOLDER)/


.PHONY: docs
docs:
	rm -f docs/source/*.rst
	sphinx-apidoc -F -o docs/source $(SOURCE_FOLDER)/ --module-first
	cp README.md docs/source/
	cp CHANGELOG.md docs/source/
	cp examples/*.py docs/source/
	cp docs/index.rst docs/source/index.rst
	cp docs/logo.png docs/source/logo.png
	sh docs/examples.sh
	cp docs/conf.py docs/source/conf.py
	$(MAKE) -C docs html SPHINXOPTS="-W" SPHINXPROJ=$(PROJECT_NAME)


.PHONY: version
version:
	python -c "import $(SOURCE_FOLDER); print($(SOURCE_FOLDER).__version__)"


.PHONY: bump-version-patch
bump-version-patch:
	# Note: You should only run this on a clean working copy
	#       If this operation succeeds, it will create a version-bumping commit
	bump2version patch --list
	git log --oneline -1


.PHONY: bump-version-minor
bump-version-minor:
	# Note: You should only run this on a clean working copy
	#       If this operation succeeds, it will create a version-bumping commit
	bump2version minor --list
	git log --oneline -1

.PHONY: bump-version-major
bump-version-major:
	# Note: You should only run this on a clean working copy
	#       If this operation succeeds, it will create a version-bumping commit
	bump2version major --list
	git log --oneline -1


.PHONY: snyk-auth
snyk-auth:
	snyk auth $(SNYK_API_SECRET_KEY)

.PHONY: snyk-test
snyk-test:
	snyk test --file=requirements.txt --severity-threshold=high

.PHONY: snyk-monitor
snyk-monitor:
	snyk monitor --file=requirements.txt  --project-name=$(PROJECT_READABLE_NAME)
