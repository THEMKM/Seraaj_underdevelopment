from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    status,
    Query,
)
from sqlmodel import Session, select
from typing import Annotated, List, Optional
import json
import logging
from datetime import datetime

from database import get_session, engine
from models import (
    User,
    Message,
    MessageRead,
    Conversation,
    ConversationCreate,
    ConversationRead,
    ConversationParticipant,
)
from auth.jwt import verify_token
from routers.auth import get_current_user
from websocket.connection_manager import connection_manager
from websocket.message_handler import message_handler

ws_router = APIRouter()
router = APIRouter(prefix="/v1/messaging", tags=["messaging"])
logger = logging.getLogger(__name__)


async def get_user_from_token(token: str, session: Session) -> Optional[User]:
    """Extract user from WebSocket token"""
    try:
        user_id = verify_token(token)
        if not user_id:
            return None

        user = session.get(User, int(user_id))
        if not user or user.status != "active":
            return None

        return user
    except Exception as e:
        logger.error(f"Error verifying WebSocket token: {e}")
        return None


@ws_router.websocket("/ws/{conversation_id}")
async def conversation_websocket(
    websocket: WebSocket,
    conversation_id: int,
    token: str = Query(...),
):
    """WebSocket endpoint for a specific conversation"""
    session = Session(engine)

    try:
        # Verify user token
        user = await get_user_from_token(token, session)
        if not user:
            await websocket.close(code=4001, reason="Invalid token")
            return

        # Verify participant in conversation
        participant = session.exec(
            select(ConversationParticipant).where(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user.id,
            )
        ).first()
        if not participant:
            await websocket.close(code=4003, reason="Not a participant")
            return

        # Connect user
        await connection_manager.connect(websocket, user.id)
        connection_manager.join_conversation(user.id, conversation_id)

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # Ensure conversation id is present
                message_data.setdefault("data", {})
                message_data["data"].setdefault("conversation_id", conversation_id)

                # Handle message
                response = await message_handler.handle_message(
                    message_data, user.id, session
                )

                # Send response back to client
                if response:
                    await websocket.send_text(json.dumps(response))

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user.id}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from user {user.id}")
            await websocket.send_text(
                json.dumps(
                    {"type": "error", "data": {"message": "Invalid JSON format"}}
                )
            )
        except Exception as e:
            logger.error(f"WebSocket error for user {user.id}: {e}")
            await websocket.send_text(
                json.dumps(
                    {"type": "error", "data": {"message": "Internal server error"}}
                )
            )

    finally:
        # Always disconnect user
        if "user" in locals():
            connection_manager.leave_conversation(user.id, conversation_id)
            connection_manager.disconnect(user.id)
        session.close()


# REST API endpoints for messaging
@router.post("/conversations", response_model=ConversationRead)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Create a new conversation"""
    # Create conversation
    db_conversation = Conversation(
        title=conversation_data.title, created_by=current_user.id
    )

    session.add(db_conversation)
    session.commit()
    session.refresh(db_conversation)

    # Add creator as participant
    creator_participant = ConversationParticipant(
        conversation_id=db_conversation.id, user_id=current_user.id, role="admin"
    )
    session.add(creator_participant)

    # Add other participants
    for participant_id in conversation_data.participant_ids:
        if participant_id != current_user.id:  # Don't add creator twice
            participant = ConversationParticipant(
                conversation_id=db_conversation.id,
                user_id=participant_id,
                role="member",
            )
            session.add(participant)

    session.commit()

    return ConversationRead.model_validate(db_conversation)


@router.get("/conversations", response_model=List[ConversationRead])
async def get_my_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get current user's conversations"""
    # Get conversations where user is a participant
    conversations = session.exec(
        select(Conversation)
        .join(
            ConversationParticipant,
            Conversation.id == ConversationParticipant.conversation_id,
        )
        .where(ConversationParticipant.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()

    return [ConversationRead.model_validate(conv) for conv in conversations]


@router.get("/conversations/{conversation_id}", response_model=ConversationRead)
async def get_conversation(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Get a specific conversation"""
    # Verify user is participant
    participant = session.exec(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.id,
        )
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    return ConversationRead.model_validate(conversation)


@router.get(
    "/conversations/{conversation_id}/messages", response_model=List[MessageRead]
)
async def get_conversation_messages(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get messages in a conversation"""
    # Verify user is participant
    participant = session.exec(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.id,
        )
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    # Get messages
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
    ).all()

    # Reverse to get chronological order
    messages.reverse()

    return [MessageRead.model_validate(msg) for msg in messages]


@router.post("/conversations/{conversation_id}/participants")
async def add_participant(
    conversation_id: int,
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Add a participant to a conversation"""
    # Verify user is admin of the conversation
    participant = session.exec(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.id,
            ConversationParticipant.role == "admin",
        )
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add participants to this conversation",
        )

    # Check if user is already a participant
    existing_participant = session.exec(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id,
        )
    ).first()

    if existing_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a participant",
        )

    # Verify the user exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Add participant
    new_participant = ConversationParticipant(
        conversation_id=conversation_id, user_id=user_id, role="member"
    )

    session.add(new_participant)
    session.commit()

    # Notify conversation participants
    notification = {
        "type": "participant_added",
        "data": {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "added_by": current_user.id,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
        },
    }

    await connection_manager.send_to_conversation(notification, conversation_id)

    return {"message": "Participant added successfully"}


@router.delete("/conversations/{conversation_id}/participants/{user_id}")
async def remove_participant(
    conversation_id: int,
    user_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    """Remove a participant from a conversation"""
    # Check if user is admin or removing themselves
    is_admin = session.exec(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == current_user.id,
            ConversationParticipant.role == "admin",
        )
    ).first()

    if not is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to remove this participant",
        )

    # Find and remove participant
    participant = session.exec(
        select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id,
        )
    ).first()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )

    session.delete(participant)
    session.commit()

    # Remove from active connection
    connection_manager.leave_conversation(user_id, conversation_id)

    # Notify conversation participants
    notification = {
        "type": "participant_removed",
        "data": {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "removed_by": current_user.id,
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
        },
    }

    await connection_manager.send_to_conversation(notification, conversation_id)

    return {"message": "Participant removed successfully"}


@router.get("/online-users")
async def get_online_users(current_user: Annotated[User, Depends(get_current_user)]):
    """Get currently online users"""
    online_users = connection_manager.get_online_users()
    return {"online_users": online_users, "count": len(online_users)}


@router.get("/stats")
async def get_messaging_stats(current_user: Annotated[User, Depends(get_current_user)]):
    """Get messaging system statistics"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return connection_manager.get_stats()


__all__ = ["router", "ws_router"]
