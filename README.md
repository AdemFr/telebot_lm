# Telegram LM chatbot

Chat with LM from [Ollama](https://ollama.com/) using telegram chatbots.

Two telegram bots are used here:
1. A management bot, which is running on cloudrun and which manages a VM
2. A bot running on a VM, which runs the model

This is only so that we do not pay for our VM if we do not need it, but we can also choose to start / stop it via telegram whenever we like.

## Setup

1. Get three API tokens from the telegram [BotFather](https://t.me/BotFather) (one for the management bot in cloudrun, one for the bot running on a VM and one for testing.)
2. Make sure you write your own `.env` file and put it into the root of this directory
    ```
    # .env
    TOKEN=<TOKEN_LM>
    TOKEN_MANAGER=<TOKEN_MANAGER>
    TOKEN_TEST=<TOKEN_TEST>
    SERVICE_NAME=<SERVICE_NAME>
    PROJECT_ID=<PROJECT_ID>
    REGION=<REGION>
    ZONE=<ZONE>
    MACHINE_TYPE=<MACHINE_TYPE>
    PORT=<PORT>
    ADMIN_CHAT_ID=<ADMIN_CHAT_ID>
    ```

## Development

1. Install uv with `curl -LsSf https://astral.sh/uv/0.2.11/install.sh | sh`
2. Make sure to have the correct python version available
3. Create virtual environment with `uv venv` and sync dependencies with `uv pip sync requirements/requirements.macos.dev.txt`
4. Run the polling bot using `make run-polling`

## Deploy to CloudRun and GCE
Make sure the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) is installed and that you have access to a google cloud project via the CLI.

NOTE: When deploying the app to cloudrun for the first time, the public URL is not available yet and the server fails.
You can deploy the app without the `lifespan` hook, so that the url exists, and then redeploy again.

If you followed the setup above, you should be able to just run
```bash
make deploy
```
This will
1. Build the docker file (optionally via `make build`)
2. Push it to google artifact registry (optionally via `make push`)
3. Deploy the image using google cloud run


In order to create a container VM to run the bot
```bash
make create_vm
```

When the machine is running, and you want to push updates to it, run
```bash
make create_vm
```
