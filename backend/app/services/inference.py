from llama_cpp import Llama
from app.config import settings
import logging
from typing import Generator, Iterator

logger = logging.getLogger(__name__)
_model: Llama = None

def load_model() -> Llama:
    logger.info("Loading model... from {settings.MODEL_PATH}")
    model = Llama(
        model_path = settings.MODEL_PATH,
        n_ctx = settings.MODEL_CONTEXT_LENGTH,
        n_threads = 4,
        n_gpu_layers = 0,
        verbose = False,
    )
    logger.info("Model loaded successfully.")
    return model

def get_model() -> Llama:
    global _model
    if _model is None:
        _model = load_model()
    return _model

def format_prompt(message: list[dict]) -> str:
    system_prompt = (
        "you are MindChat, a helpful and friendly AI assistent."
        "Answer as concisely as possible. If you don't know the answer, say you don't know."
        )

    prompt = f"<|system|>\n{system_prompt}</s>\n"

    for msg in message:
        if msg["role"] == "user":
            prompt += f"<|user|>\n{msg['content']}</s>\n"
        elif msg["role"] == "assistant":
            prompt += f"<|assistant|>\n{msg['content']}</s>\n"
    prompt += "<|assistant|>\n"
    return prompt

def generate_response(messages: list[dict]) -> str:
    model = get_model()
    prompt = format_prompt(messages)
    
    # Temporary debug — will remove after testing
    # logger.info(f"Full history being sent to model: {messages}")
    
    logger.info("Generating response...")
    output = model(
        prompt,
        max_tokens=settings.MODEL_MAX_TOKENS,
        temperature=settings.MODEL_TEMPERATURE,
        stop=["</s>", "<|user|>", "<|system|>"],
        echo=False,
    )
    response = output["choices"][0]["text"].strip()
    logger.info("Response generated successfully.")
    return response

def Response_Generator_stream(messages: list[dict]) -> Generator[str, None, None]:
    model = get_model()
    prompt = format_prompt(message=messages)

    logger.info("Generating response stream...")

    output: Iterator = model(
        prompt,
        max_tokens = settings.MODEL_MAX_TOKENS,
        temperature = settings.MODEL_TEMPERATURE,
        stop = ["</s>", "<|user|>", "<|system|>"],
        stream = True,
        echo = False
    )

    for chunk in output:
        token = chunk["choices"][0]["text"]
        if token:
            yield token
