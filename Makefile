SHELL := /bin/bash

# Sets all secret variables needed for running the commands
include .env

# Non secret variables
.DEFAULT_GOAL=help
SERVICE_NAME=telebot-lm

help: # Show this help
	@egrep -h '\s#\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: # Build docker image with loaded env variables
	@docker build -t ${TAG} .

.PHONY: push
push: build # Build and push docker image
	@docker push ${TAG}

.PHONY: drun
drun: build # Build and run server in docker container
	@docker run -it --rm \
		-p ${PORT}:${PORT} \
		-e TOKEN=${TOKEN} \
		-e PORT=${PORT} \
		-e PROJECT_ID=${PROJECT_ID} \
		-e REGION=${REGION} \
		-e SERVICE_NAME=${SERVICE_NAME} \
		${TAG}

.PHONY: run
run: # Run server inside poetry shell
	@TOKEN=${TOKEN} poetry run uvicorn telebot_template.main:app --reload --host 0.0.0.0 --port ${PORT}

.PHONY: run
run-poll: # Run server inside poetry shell
	@TOKEN=${TOKEN} poetry run python telebot_template/main.py

.PHONY: deploy
deploy: push # Build, push and deploy cloud run service
	@gcloud run deploy ${SERVICE_NAME} \
		--image ${TAG} \
		--set-env-vars TOKEN=${TOKEN},PROJECT_ID=${PROJECT_ID},REGION=${REGION},SERVICE_NAME=${SERVICE_NAME} \
		--allow-unauthenticated \
		--min-instances=0 \
		--max-instances=1 \
		--port ${PORT} \
		--cpu 1 \
		--timeout 30 \

