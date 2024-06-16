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

    def agent_choice(self, text):
        agents = [
            "You are a food character. You know how to cook and always reply with recipes and food facts. They should be concise and in bullet points",
            "You are a music character. You know everything about music and prefer jazz. Everything is about jazz for you. Be short, clever, and funny",
        ]
        prompt = """
        ### USER MESSAGE: {text}
        
        You have to choose exactly one fitting character to be:
        
        0. {agent1}
        1. {agent2}
         
        Do not answer the USER MESSAGE yet. Just choose a character.
        Answer with an interger: 0 or 1.
        
        Do not write anything else in your response. The response should only be one character.
        The answer has to be the first character.
        
        ### RESPONSE: 
        
        """.format(text=text, agent1=agents[0], agent2=agents[1])

        response = self.chat(prompt)
        try:
            agent_choice = int(response.strip()[0])
            logger.info(f"Agent choice: {agent_choice}")
        except Exception:
            logger.error(f"Invalid agent choice: {response}")
            agent_choice = 0

        return agents[agent_choice] + "\nUSER MESSAGE:\n"

    def chat(self, text):
        stream = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": text}],
            stream=True,
        )

        logger.info(f"Start generating response to {text}...")
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
