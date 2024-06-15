# Telegram Webhook Bot on Google Cloud Run

This repo gives a minimal example for how to run a telegram bot using webhooks on cloud run.

The main reason to do so is cost effectiveness, because one has to only pay for the CPU time that actually handles requests instead of constantly having to run a server which polls for updates. In order to do this, we need to enable scaling to 0 instances of our app, so that it only scales up when requests come in.

## Setup

1. Get an API token from the telegram [BotFather](https://t.me/BotFather)
2. Make sure you write your own `.env` file and put it into the root of this directory
    ```
    # .env
    TOKEN=<TELEGRAM API TOKEN>
    SERVICE_NAME=<CLOUD RUN SERVICE NAME>
    PROJECT_ID=<GOOGLE PROJECT ID>
    REGION=<GOOGLE SERVICE REGION>
    TAG=<DOCKER IMAGE TAG>
    PORT=<PORT FOR THE SERVER TO RUN ON>
    ```

## Development

1. Install uv with `curl -LsSf https://astral.sh/uv/0.2.11/install.sh | sh`
2. Make sure to have the correct python version available
3. Create virtual environment with `uv venv` and sync dependencies with `uv pip sync requirements/requirements.macos.dev.txt`

## Run polling locally
In order to run the bot via simple polling mechanism locally:

1. Install the package using `poetry install`
2. Run the polling bot using `make run-polling`

You can also test the functionality this way by just creating a new testing bot as suggested [here](https://core.telegram.org/bots/features#testing-your-bot).

## Deploy to Cloud Run
Make sure the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) is installed and that you have access to a google cloud project via the CLI.

If you followed the setup above, you should be able to just run
```bash
make deploy
```

This will
1. Build the docker file (optionally via `make build`)
2. Push it to google artifact registry (optionally via `make push`)
3. Deploy the image using google cloud run
