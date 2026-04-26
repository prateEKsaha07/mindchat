from app.db.database import engine, Base
from app.models.user import User
from app.models.conversation import Conversation, Message

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully.")