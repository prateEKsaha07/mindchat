from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, 
                primary_key=True, 
                default=lambda: str(uuid.uuid4())
                )
    user_id = Column(String, 
                     ForeignKey("users.id"), 
                     nullable=False
                     )
    title = Column(String, 
                   default="new conversation"
                   )
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
        )
    updated_at = Column(DateTime(timezone=True), 
                        onupdate=func.now()
                        )
    user = relationship("User", 
                        back_populates="conversations"
                        )
    messages = relationship("Message",
                            back_populates="conversation", 
                            cascade="all, delete-orphan"
                            )

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, 
                primary_key=True, 
                default=lambda: str(uuid.uuid4())
                )
    conversation_id = Column(String, 
                             ForeignKey("conversations.id"), 
                             nullable=False
                             )
    role = Column(String,
                  nullable=False
                  ) 
    content = Column(
        Text,
        nullable=False
        )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
        )
    
    conversation = relationship("Conversation",
                                back_populates="messages"
                                )