# Variables
VENV_NAME=/Users/matt/.envs/menv
DOCKER_IMG_NAME=dash_demo
DOCKER_CONTAINER_NAME=dash_container
JUPYTER_NOTEBOOK=dash_v3-xyz.py
PYTHON=python3
PIP=$(VENV_NAME)/bin/pip
APP=$(VENV_NAME)/bin/python

help:
	@echo "Choose a command to run in pca-proj:"
	@echo
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup-directories: ## Create the project directory structure
	mkdir -p data/raw
	mkdir -p data/processed
	mkdir -p data/external
	mkdir -p notebooks/exploratory
	mkdir -p notebooks/report
	mkdir -p src
	mkdir -p tests
	mkdir -p docker

setup_venv: ## Set up the virtual environment
	$(PYTHON) -m venv $(VENV_NAME)
	$(PIP) install -r requirements.txt


test: ## Run tests
	@echo "Running tests with pytest..."
	@PYTHONPATH=./src pytest -v tests/


docker_build: ## Build the Docker image
	docker build -t $(DOCKER_IMG_NAME) .


docker_deploy: ## Deploy the Docker container
	docker run -d --name $(DOCKER_CONTAINER_NAME) -p 8050:8050 $(DOCKER_IMG_NAME)


ci: test docker_build docker_deploy ## Run CI/CD
	@echo "Continuous Integration and Deployment completed."


docker_stop: ## Stop and remove Docker container
	docker stop $(DOCKER_CONTAINER_NAME)
	docker rm $(DOCKER_CONTAINER_NAME)


clean: ## Cleanup the development environment
	rm -rf $(VENV_NAME)
	docker rmi $(DOCKER_IMG_NAME)

run_dash_app: ## Run the dash app
	PYTHONPATH=src $(APP) src/app.py

setup_readme:  ## Create a README.md
	@if [ ! -f README.md ]; then \
		echo "# Project Name\n\
Description of the project.\n\n\
## Installation\n\
- Step 1\n\
- Step 2\n\n\
## Usage\n\
Explain how to use the project here.\n\n\
## Contributing\n\
Explain how to contribute to the project.\n\n\
## License\n\
License information." > README.md; \
		echo "README.md created."; \
	else \
		echo "README.md already exists."; \
	fi




# Make it PHONY
.PHONY: setup_venv test docker_build docker_deploy ci docker_stop clean help setup_readme
