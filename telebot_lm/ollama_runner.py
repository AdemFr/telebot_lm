import logging
import subprocess
import threading
import time

import ollama

logger = logging.getLogger(__name__)


MODELS = {
    "phi3": "phi3:mini",
    "gemma": "gemma:2B",
    "qwen": "qwen:1.8b",
}


class OllamaRunner:
    """Runner singleton for Ollama process."""

    _instance = None
    process = None
    thread = None
    model = MODELS["phi3"]

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OllamaRunner, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def start_ollama(self):
        self.process = subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE)
        time.sleep(3)
        logger.info("Ollama process started")

        # Start a thread to handle the process's output
        self.thread = threading.Thread(target=self.handle_output, args=(self.process,))
        self.thread.start()
        logger.info("Ollama logging thread started")

        logger.info("Start pulling model...")
        ollama.pull(self.model)
        logger.info("Done pulling model")

    def stop_ollama(self):
        if self.process:
            self.process.terminate()
            self.process = None
        logger.info("Ollama process stopped")
        if self.thread:
            self.thread.join()
            self.thread = None
        logger.info("Thread stopped")

    def set_model(self, model):
        if model not in MODELS:
            logger.error(f"Model {model} not found")
            return
        self.model = model
        ollama.pull(self.model)
        logger.info(f"Model set to {model}")

    def chat(self, message):
        stream = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": message.text}],
            stream=True,
        )

        logger.info(f"Start generating response to {message.text}...")
        response = ""
        for chunk in stream:
            _output = chunk["message"]["content"]
            response += _output
            print(_output, end="", flush=True)
            if chunk["done"]:
                print("")
        return response

    @staticmethod
    def handle_output(process):
        for c in iter(lambda: process.stdout.read(), b""):
            logger.info(c.decode())


if __name__ == "__main__":
    try:
        runner = OllamaRunner()
        runner.start_ollama()
        logger.info("Ollama started.")

        stream = ollama.chat(
            model="phi3:mini",
            messages=[{"role": "user", "content": "Why is the sky blue?"}],
            stream=True,
        )

        output = ""
        for chunk in stream:
            _output = chunk["message"]["content"]
            output += _output
            print(_output, end="", flush=True)
        logger.info(f"Output: {output}")

    except Exception as e:
        logger.error(e, exc_info=True)
    finally:
        runner.stop_ollama()
