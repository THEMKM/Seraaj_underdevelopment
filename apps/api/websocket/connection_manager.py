from typing import Dict, List, Set, Any
from fastapi import WebSocket
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager for real-time messaging"""

    def __init__(self):
        # Active connections: {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}

        # User presence: {user_id: last_seen}
        self.user_presence: Dict[int, datetime] = {}

        # Conversation participants: {conversation_id: Set[user_id]}
        self.conversation_participants: Dict[int, Set[int]] = {}

        # Track conversations joined per user: {user_id: Set[conversation_id]}
        self.user_conversations: Dict[int, Set[int]] = {}

        # User typing status: {conversation_id: {user_id: datetime}}
        self.typing_status: Dict[int, Dict[int, datetime]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_presence[user_id] = datetime.now(datetime.timezone.utc)

        logger.info(f"User {user_id} connected to WebSocket")

        # Notify other users about online status
        await self.broadcast_user_status(user_id, "online")

    def disconnect(self, user_id: int):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # Update last seen
        self.user_presence[user_id] = datetime.now(datetime.timezone.utc)

        # Remove user from all joined conversations
        for conv_id in list(self.user_conversations.get(user_id, set())):
            self.leave_conversation(user_id, conv_id)

        logger.info(f"User {user_id} disconnected from WebSocket")

        # Notify other users about offline status
        asyncio.create_task(self.broadcast_user_status(user_id, "offline"))

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                # Remove dead connection
                self.disconnect(user_id)
                return False
        return False

    async def send_to_conversation(
        self, message: dict, conversation_id: int, sender_id: int = None
    ):
        """Send a message to all participants in a conversation"""
        if conversation_id not in self.conversation_participants:
            return

        participants = self.conversation_participants[conversation_id].copy()

        # Don't send to sender if specified
        if sender_id and sender_id in participants:
            participants.remove(sender_id)

        # Send to all participants
        for user_id in participants:
            await self.send_personal_message(message, user_id)

    async def broadcast_user_status(self, user_id: int, status: str):
        """Broadcast user online/offline status to relevant users"""
        message = {
            "type": "user_status",
            "data": {
                "user_id": user_id,
                "status": status,
                "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            },
        }

        # Send to all connected users (in a real app, you'd optimize this)
        for connected_user_id in list(self.active_connections.keys()):
            if connected_user_id != user_id:
                await self.send_personal_message(message, connected_user_id)

    def join_conversation(self, user_id: int, conversation_id: int):
        """Add user to conversation participants"""
        if conversation_id not in self.conversation_participants:
            self.conversation_participants[conversation_id] = set()

        self.conversation_participants[conversation_id].add(user_id)

        if user_id not in self.user_conversations:
            self.user_conversations[user_id] = set()
        self.user_conversations[user_id].add(conversation_id)

    def leave_conversation(self, user_id: int, conversation_id: int):
        """Remove user from conversation participants"""
        if conversation_id in self.conversation_participants:
            self.conversation_participants[conversation_id].discard(user_id)

            # Clean up empty conversations
            if not self.conversation_participants[conversation_id]:
                del self.conversation_participants[conversation_id]

        if user_id in self.user_conversations:
            self.user_conversations[user_id].discard(conversation_id)
            if not self.user_conversations[user_id]:
                del self.user_conversations[user_id]

    async def handle_typing(self, user_id: int, conversation_id: int, is_typing: bool):
        """Handle typing indicators"""
        if conversation_id not in self.typing_status:
            self.typing_status[conversation_id] = {}

        if is_typing:
            self.typing_status[conversation_id][user_id] = datetime.now(
                datetime.timezone.utc
            )
        else:
            self.typing_status[conversation_id].pop(user_id, None)

        # Broadcast typing status to conversation participants
        message = {
            "type": "typing_status",
            "data": {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "is_typing": is_typing,
                "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            },
        }

        await self.send_to_conversation(message, conversation_id, sender_id=user_id)

    def get_online_users(self) -> List[int]:
        """Get list of currently online users"""
        return list(self.active_connections.keys())

    def is_user_online(self, user_id: int) -> bool:
        """Check if a user is currently online"""
        return user_id in self.active_connections

    def get_conversation_online_users(self, conversation_id: int) -> List[int]:
        """Get online users in a specific conversation"""
        if conversation_id not in self.conversation_participants:
            return []

        participants = self.conversation_participants[conversation_id]
        return [user_id for user_id in participants if self.is_user_online(user_id)]

    async def ping_all_connections(self):
        """Send ping to all connections to keep them alive"""
        ping_message = {
            "type": "ping",
            "data": {"timestamp": datetime.now(datetime.timezone.utc).isoformat()},
        }

        dead_connections = []

        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(ping_message))
            except Exception as e:
                logger.error(f"Connection to user {user_id} is dead: {e}")
                dead_connections.append(user_id)

        # Clean up dead connections
        for user_id in dead_connections:
            self.disconnect(user_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "active_connections": len(self.active_connections),
            "active_conversations": len(self.conversation_participants),
            "total_participants": sum(
                len(participants)
                for participants in self.conversation_participants.values()
            ),
            "typing_users": sum(len(typing) for typing in self.typing_status.values()),
        }


# Global connection manager instance
connection_manager = ConnectionManager()
