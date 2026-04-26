from sqlalchemy import select,desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation, Message
from app.models.user import User
from app.services.inference import generate_response, Response_Generator_stream
import logging

logger = logging.getLogger(__name__)

async def get_or_create_conversation(
        db: AsyncSession,
        user: User,
        conversation_id: str = None
) -> Conversation:
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            return None
        return conversation
    
    # no id provided, create new conversation
    conversation = Conversation(
        user_id=user.id,
        title="New Conversation"
        )
    db.add(conversation)
    await db.flush() # gets  is assigned without full commit
    return conversation

async def get_conversation_messages(
        db: AsyncSession,
        conversation_id: str      
)-> list[Message] :
    results = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return results.scalars().all()

async def build_message_history(messages: list[Message]) -> list[dict]:
    history = [
        {
            "role":msg.role,
            "content":msg.content
        }
        for msg in messages
    ]
    return history[-10:] # only keep the last 10 messages for context

async def update_conversation_title(
        db: AsyncSession,
        conversation: Conversation,
        first_message: str
):
    if conversation.title == "New Conversation":
        title = first_message[:50] # limit title length
        if len(first_message) > 50:
            title += "..."
        conversation.title = title
        db.add(conversation)

async def chat(
        db: AsyncSession,
        user: User,
        message: str,
        conversation_id: str = None
) -> dict:
    conversation = await get_or_create_conversation(db, user, conversation_id)
    
    if conversation_id and not conversation:
        return None # doesn't belong to user
    
    existing_messages = await get_conversation_messages(
        db, 
        conversation.id
    )

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=message
    )
    db.add(user_message)
    await db.flush() # assign id to user_message

    history = await build_message_history(existing_messages)
    history.append({
        "role":"user",
        "content":message
    })
    logger.info(f"Generating response with history for conversation {conversation.id}")
    response_text = generate_response(history)

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text
    )
    db.add(assistant_message)
    await db.flush()

    await update_conversation_title(db, conversation, message)

    await db.commit()

    logger.info(f"Chat complete for conversation {conversation.id}")

    return {
        "response": response_text,
        "conversation_id": conversation.id,
        "message_id": assistant_message.id
    }

async def chat_stream(
        db: AsyncSession,
        user: User,
        message: str,
        conversation_id: str = None
):
    conversation = await get_or_create_conversation(db, user, conversation_id)
    if conversation_id and not conversation:
        yield None
        return 
    
    #loading existing messages for context
    existing_messages = await get_conversation_messages(db, conversation.id)

    #saving user messages 
    user_messages = Message(
        conversation_id = conversation.id,
        role = "user",
        content = message
    )
    db.add(user_messages)
    await db.flush() # assign id to user_message
    await db.commit()

    # keeping history of last 10 messages for context
    history = await build_message_history(existing_messages)
    history.append({
        "role":"user",
        "content":message
    })

    # stream tokens , collect full response
    full_response = []

    for token in Response_Generator_stream(history):
        full_response.append(token)
        yield token # stream token to client almost immediately

    # after stream is done, save full response to db 
    complete_response = "".join(full_response)

    assistant_message = Message(
        conversation_id = conversation.id,
        role = "assistant",
        content = complete_response
    )
    db.add(assistant_message)

    await update_conversation_title(db, conversation, message)
    await db.commit()

    logger.info(f"Chat stream complete for conversation {conversation.id}")

    yield f"\n[CONVERSATION ID: {conversation.id}, MESSAGE ID: {assistant_message.id}]"