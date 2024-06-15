# Telegram LM chatbot on cloudrun

Deploy a custom telegram bot to chat with to cloudrun!

## Setup

1. Get an API token from the telegram [BotFather](https://t.me/BotFather)
2. Make sure you write your own `.env` file and put it into the root of this directory
    ```
    # .env
    TOKEN=<TELEGRAM API TOKEN>
    TOKEN_TEST=<OPTIONAL_FOR_PARALLEL_TESTING>
    SERVICE_NAME=<CLOUD RUN SERVICE NAME>
    PROJECT_ID=<GOOGLE PROJECT ID>
    REGION=<GOOGLE SERVICE REGION>
    PORT=<PORT FOR THE SERVER TO RUN ON>
    ```

## Development

1. Install uv with `curl -LsSf https://astral.sh/uv/0.2.11/install.sh | sh`
2. Make sure to have the correct python version available
3. Create virtual environment with `uv venv` and sync dependencies with `uv pip sync requirements/requirements.macos.dev.txt`
4. Run the polling bot using `make run-polling`

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
