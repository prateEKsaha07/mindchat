from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.init_db import init_db
from contextlib import asynccontextmanager
import logging
from app.routers import auth, chat
from app.services.inference import get_model

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    await init_db()
    logger.info("Database initialized.")
    logger.info("Loading the model...")
    get_model()
    logger.info("Application startup complete.")
    yield
    logger.info("Shutting down the application...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan        
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} is running! version is {settings.APP_VERSION}"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/test-model")
def test_model(prompt:str):
    from app.services.inference import generate_response
    message = [{
        "role": "user", 
        "content": prompt
        }]
    response = generate_response(message)
    return {
        "prompt": prompt, 
        "response": response
        }