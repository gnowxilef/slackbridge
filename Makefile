DOCKER_REVISION ?= testing-$(USER)
DOCKER_TAG = docker-push.ocf.berkeley.edu/slackbridge:$(DOCKER_REVISION)

.PHONY: test
test: venv install-hooks
		venv/bin/pre-commit run --all-files

.PHONY: dev
dev: venv
		venv/bin/python -m slackbridge.main

.PHONY: install-hooks
install-hooks: venv
		venv/bin/pre-commit install -f --install-hooks

venv: vendor/venv-update requirements.txt requirements-dev.txt
		vendor/venv-update \
				venv= -ppython3 venv \
				install= -r requirements.txt -r requirements-dev.txt

.PHONY: clean
clean:
		rm -rf venv

.PHONY: update-requirements
update-requirements: venv
		venv/bin/upgrade-requirements

.PHONY: cook-image
cook-image:
		docker build -t $(DOCKER_TAG) .

.PHONY: push-image
push-image:
		docker push $(DOCKER_TAG)
