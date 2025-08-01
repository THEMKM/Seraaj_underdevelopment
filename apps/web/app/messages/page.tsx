"use client";

import React, { useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { MessageInterface } from '../../components/messaging/MessageInterface';
import { useWebSocket } from '../../contexts/WebSocketContext';

export default function MessagesPage() {
  const { connect, isConnected } = useWebSocket();

  useEffect(() => {
    // WebSocket will auto-connect when user is authenticated
    // No manual connection needed
  }, []);

  return (
    <AppLayout userType="volunteer">
      <div className="h-[calc(100vh-140px)]"> {/* Adjust height for header/nav */}
        <MessageInterface />
      </div>
    </AppLayout>
  );
}