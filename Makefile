SHELL := /bin/bash

# Sets all secret variables needed for running the commands
include .env

# Non secret variables
.DEFAULT_GOAL=help
IMAGE_NAME=${REGION}-docker.pkg.dev/${PROJECT_ID}/${SERVICE_NAME}/main

help: # Show this help
	@egrep -h '\s#\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: # Build docker image with loaded env variables
	@docker build -t ${IMAGE_NAME} .

buildx: # Build docker image with loaded env variables
	@docker buildx build --platform linux/amd64 -t ${IMAGE_NAME} .


.PHONY: push
push: buildx # Build and push docker image
	@docker push ${IMAGE_NAME}

.PHONY: run
run-poll: # Run server inside poetry shell
	@TOKEN=${TOKEN_TEST} \
	POLLING=True \
	PROJECT_ID=${PROJECT_ID} \
	ZONE=${ZONE} \
	SERVICE_NAME=${SERVICE_NAME} \
	ADMIN_CHAT_ID=${ADMIN_CHAT_ID} \
	python telebot_lm/main.py

.PHONY: deploy
deploy: push # Build, push and deploy cloud run service
	@gcloud run deploy ${SERVICE_NAME} \
		--project ${PROJECT_ID} \
		--image ${IMAGE_NAME} \
		--region ${REGION} \
		--set-env-vars TOKEN=${TOKEN_MANAGER},PROJECT_ID=${PROJECT_ID},REGION=${REGION},SERVICE_NAME=${SERVICE_NAME},ZONE=${ZONE},ADMIN_CHAT_ID=${ADMIN_CHAT_ID} \
		--allow-unauthenticated \
		--min-instances=0 \
		--max-instances=1 \
		--port ${PORT} \
		--cpu 1 \
		--timeout 1m

.PHONY: compile
compile:
	@uv pip compile --emit-index-url --emit-find-links --no-cache --python 3.11 --python-platform linux --python-version 3.11 --generate-hashes --output-file requirements/requirements.linux.txt requirements/requirements.in > /dev/null
	@uv pip compile --emit-index-url --emit-find-links --no-cache --python 3.11 --python-platform macos --python-version 3.11 --generate-hashes --output-file requirements/requirements.macos.txt requirements/requirements.in > /dev/null
	@uv pip compile --emit-index-url --emit-find-links --no-cache --python 3.11 --python-platform macos --python-version 3.11 --generate-hashes --output-file requirements/requirements.macos.dev.txt requirements/requirements.dev.in > /dev/null


.PHONY: sync
sync: compile
	@uv pip sync requirements/requirements.macos.dev.txt


.PHONY: create_vm
create_vm: push # Build, push and deploy cloud run service
	@gcloud compute instances create-with-container telebot-lm \
		--container-image ${IMAGE_NAME} \
		--container-command "python" \
		--container-arg "telebot_lm/main.py" \
		--container-env POLLING=True,TOKEN=${TOKEN},PROJECT_ID=${PROJECT_ID},ZONE=${ZONE},SERVICE_NAME=${SERVICE_NAME},ADMIN_CHAT_ID=${ADMIN_CHAT_ID} \
		--machine-type ${MACHINE_TYPE} \
		--project ${PROJECT_ID} \

.PHONY: update_vm
update_vm: push # Build, push and deploy cloud run service
	@gcloud compute instances update-container telebot-lm \
		--container-image ${IMAGE_NAME} \
		--container-command "python" \
		--container-arg "telebot_lm/main.py" \
		--container-env POLLING=True,TOKEN=${TOKEN},PROJECT_ID=${PROJECT_ID},ZONE=${ZONE},SERVICE_NAME=${SERVICE_NAME},ADMIN_CHAT_ID=${ADMIN_CHAT_ID} \
		--project ${PROJECT_ID} \


.PHONY: update_all
update_all: deploy update_vm
