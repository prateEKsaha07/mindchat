from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, 
                primary_key=True, 
                default=lambda: str(uuid.uuid4())
                )
    username = Column(String, 
                      unique=True, 
                      nullable=False, 
                      index = True
                      )
    email = Column(String, 
                   unique=True, 
                   nullable=False, 
                   index = True
                   )
    hashed_password = Column(
        String, 
        nullable=False
        )
    is_active = Column(
        Boolean, 
        default=True
        )
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
        )

    conversations = relationship("Conversation", 
                                 back_populates="user", 
                                 cascade="all, delete-orphan")