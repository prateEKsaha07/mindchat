from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ConversationResponse, MessageResponse
from app.services.chat_service import chat, get_conversation_messages, get_or_create_conversation
from app.services.auth_service import get_current_user
from sqlalchemy import select, desc
from app.models.conversation import Conversation
from typing import Optional
from fastapi.responses import StreamingResponse
from app.services.chat_service import chat, get_conversation_messages, get_or_create_conversation, chat_stream


router = APIRouter(prefix="/chat", tags=["chat"])


async def get_authenticated_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    token = authorization.split(" ")[1]
    user = await get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user


@router.post("/", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_authenticated_user)
):

    result = await chat(
        db=db,
        user=current_user,
        message=request.message,
        conversation_id=request.conversation_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return ChatResponse(**result)


@router.get("/conversations", response_model=list[ConversationResponse])
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_authenticated_user)
):

    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.created_at))
    )
    conversations = result.scalars().all()
    return conversations


@router.get("/conversations/{conversation_id}/messages",
            response_model=list[MessageResponse])
async def get_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_authenticated_user)
):
    conversation = await get_or_create_conversation(
        db, current_user, conversation_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    messages = await get_conversation_messages(db, conversation_id)
    return messages

@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_authenticated_user)
):
    async def generate():
        async for token in chat_stream(
            db=db,
            user=current_user,
            message=request.message,
            conversation_id=request.conversation_id
        ):
            yield token

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )