from typing import Dict, Any, Optional
from sqlmodel import Session, select
from datetime import datetime
import json
import logging

from database import get_session
from models import (
    Message, MessageCreate, Conversation, ConversationParticipant,
    MessageReadReceipt, User, MessageType
)
from websocket.connection_manager import connection_manager

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handle different types of WebSocket messages"""
    
    def __init__(self):
        self.handlers = {
            "send_message": self.handle_send_message,
            "mark_read": self.handle_mark_read,
            "typing": self.handle_typing,
            "join_conversation": self.handle_join_conversation,
            "leave_conversation": self.handle_leave_conversation,
            "get_online_users": self.handle_get_online_users,
        }
    
    async def handle_message(self, message_data: Dict[str, Any], user_id: int, session: Session):
        """Route incoming WebSocket messages to appropriate handlers"""
        message_type = message_data.get("type")
        
        if message_type not in self.handlers:
            logger.error(f"Unknown message type: {message_type}")
            return {
                "type": "error",
                "data": {"message": f"Unknown message type: {message_type}"}
            }
        
        try:
            handler = self.handlers[message_type]
            return await handler(message_data.get("data", {}), user_id, session)
        except Exception as e:
            logger.error(f"Error handling message type {message_type}: {e}")
            return {
                "type": "error", 
                "data": {"message": "Internal server error"}
            }
    
    async def handle_send_message(self, data: Dict[str, Any], user_id: int, session: Session):
        """Handle sending a new message"""
        conversation_id = data.get("conversation_id")
        content = data.get("content")
        message_type = data.get("message_type", "text")
        
        if not conversation_id or not content:
            return {
                "type": "error",
                "data": {"message": "Missing required fields: conversation_id, content"}
            }
        
        # Verify user is participant in conversation
        participant = session.exec(
            select(ConversationParticipant).where(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id
            )
        ).first()
        
        if not participant:
            return {
                "type": "error",
                "data": {"message": "Not authorized to send messages in this conversation"}
            }
        
        # Create message
        db_message = Message(
            conversation_id=conversation_id,
            sender_id=user_id,
            content=content,
            message_type=MessageType(message_type) if message_type in [e.value for e in MessageType] else MessageType.TEXT
        )
        
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
        
        # Get sender info
        sender = session.get(User, user_id)
        
        # Prepare message for broadcast
        message_response = {
            "type": "new_message",
            "data": {
                "id": db_message.id,
                "conversation_id": conversation_id,
                "sender_id": user_id,
                "sender_name": f"{sender.first_name} {sender.last_name}" if sender else "Unknown",
                "content": content,
                "message_type": message_type,
                "created_at": db_message.created_at.isoformat(),
                "is_edited": False
            }
        }
        
        # Send to all conversation participants
        await connection_manager.send_to_conversation(
            message_response, 
            conversation_id, 
            sender_id=user_id
        )
        
        # Update conversation last activity
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.now(datetime.timezone.utc)
            session.add(conversation)
            session.commit()
        
        return {
            "type": "message_sent",
            "data": {"message_id": db_message.id, "status": "delivered"}
        }
    
    async def handle_mark_read(self, data: Dict[str, Any], user_id: int, session: Session):
        """Handle marking messages as read"""
        message_id = data.get("message_id")
        conversation_id = data.get("conversation_id")
        
        if message_id:
            # Mark specific message as read
            message = session.get(Message, message_id)
            if not message:
                return {
                    "type": "error",
                    "data": {"message": "Message not found"}
                }
            
            # Check if read receipt already exists
            existing_receipt = session.exec(
                select(MessageReadReceipt).where(
                    MessageReadReceipt.message_id == message_id,
                    MessageReadReceipt.user_id == user_id
                )
            ).first()
            
            if not existing_receipt:
                # Create read receipt
                read_receipt = MessageReadReceipt(
                    message_id=message_id,
                    user_id=user_id,
                    read_at=datetime.now(datetime.timezone.utc)
                )
                session.add(read_receipt)
                session.commit()
                
                # Notify sender about read receipt
                read_notification = {
                    "type": "message_read",
                    "data": {
                        "message_id": message_id,
                        "reader_id": user_id,
                        "read_at": read_receipt.read_at.isoformat()
                    }
                }
                
                await connection_manager.send_personal_message(
                    read_notification, 
                    message.sender_id
                )
        
        elif conversation_id:
            # Mark all unread messages in conversation as read
            unread_messages = session.exec(
                select(Message).where(
                    Message.conversation_id == conversation_id,
                    Message.sender_id != user_id
                )
            ).all()
            
            for message in unread_messages:
                # Check if already read
                existing_receipt = session.exec(
                    select(MessageReadReceipt).where(
                        MessageReadReceipt.message_id == message.id,
                        MessageReadReceipt.user_id == user_id
                    )
                ).first()
                
                if not existing_receipt:
                    read_receipt = MessageReadReceipt(
                        message_id=message.id,
                        user_id=user_id,
                        read_at=datetime.now(datetime.timezone.utc)
                    )
                    session.add(read_receipt)
            
            session.commit()
        
        return {
            "type": "marked_read",
            "data": {"status": "success"}
        }
    
    async def handle_typing(self, data: Dict[str, Any], user_id: int, session: Session):
        """Handle typing indicators"""
        conversation_id = data.get("conversation_id")
        is_typing = data.get("is_typing", False)
        
        if not conversation_id:
            return {
                "type": "error",
                "data": {"message": "Missing conversation_id"}
            }
        
        # Verify user is participant in conversation
        participant = session.exec(
            select(ConversationParticipant).where(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id
            )
        ).first()
        
        if not participant:
            return {
                "type": "error",
                "data": {"message": "Not authorized to participate in this conversation"}
            }
        
        # Handle typing status
        await connection_manager.handle_typing(user_id, conversation_id, is_typing)
        
        return {
            "type": "typing_updated",
            "data": {"status": "success"}
        }
    
    async def handle_join_conversation(self, data: Dict[str, Any], user_id: int, session: Session):
        """Handle user joining a conversation"""
        conversation_id = data.get("conversation_id")
        
        if not conversation_id:
            return {
                "type": "error",
                "data": {"message": "Missing conversation_id"}
            }
        
        # Verify user is participant in conversation
        participant = session.exec(
            select(ConversationParticipant).where(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.user_id == user_id
            )
        ).first()
        
        if not participant:
            return {
                "type": "error",
                "data": {"message": "Not authorized to join this conversation"}
            }
        
        # Join conversation
        connection_manager.join_conversation(user_id, conversation_id)
        
        # Notify other participants
        join_notification = {
            "type": "user_joined",
            "data": {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "timestamp": datetime.now(datetime.timezone.utc).isoformat()
            }
        }
        
        await connection_manager.send_to_conversation(
            join_notification, 
            conversation_id, 
            sender_id=user_id
        )
        
        return {
            "type": "joined_conversation",
            "data": {"conversation_id": conversation_id, "status": "success"}
        }
    
    async def handle_leave_conversation(self, data: Dict[str, Any], user_id: int, session: Session):
        """Handle user leaving a conversation"""
        conversation_id = data.get("conversation_id")
        
        if not conversation_id:
            return {
                "type": "error",
                "data": {"message": "Missing conversation_id"}
            }
        
        # Leave conversation
        connection_manager.leave_conversation(user_id, conversation_id)
        
        # Notify other participants
        leave_notification = {
            "type": "user_left",
            "data": {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "timestamp": datetime.now(datetime.timezone.utc).isoformat()
            }
        }
        
        await connection_manager.send_to_conversation(
            leave_notification, 
            conversation_id, 
            sender_id=user_id
        )
        
        return {
            "type": "left_conversation",
            "data": {"conversation_id": conversation_id, "status": "success"}
        }
    
    async def handle_get_online_users(self, data: Dict[str, Any], user_id: int, session: Session):
        """Handle request for online users"""
        conversation_id = data.get("conversation_id")
        
        if conversation_id:
            # Get online users in specific conversation
            online_users = connection_manager.get_conversation_online_users(conversation_id)
        else:
            # Get all online users
            online_users = connection_manager.get_online_users()
        
        return {
            "type": "online_users",
            "data": {
                "online_users": online_users,
                "count": len(online_users),
                "conversation_id": conversation_id
            }
        }


# Global message handler instance
message_handler = MessageHandler()